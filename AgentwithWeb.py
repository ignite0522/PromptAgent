import json
import os
import sys
from typing import TypedDict, Annotated, Any, Literal

import dotenv
from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

from tools import (
    nmap_scan,
    dirsearch_scan,
    read_web_file,
    web_request,
    check_xss,
    read_doc,
    MAX_TOOL_RESULT_CHARS,
)

dotenv.load_dotenv()

# Agent 最多执行多少轮「LLM -> 工具 -> LLM」，防止无限循环
MAX_TOOL_ROUNDS = 20


# --- 步骤 1：图状态与节点 ---

class State(TypedDict, total=False):
    """图状态。
    - messages: 对话与工具调用消息
    - code_summary: 已读取页面/源码中与 XSS 相关的摘要（输入点、反射位置、编码/过滤），供后续每轮 LLM 优先参考
    - doc_content: read_doc 获取的技术文档内容（防御与绕过），供后续每轮 LLM 优先参考
    - tool_rounds: 已执行的「LLM->工具->LLM」轮数，用于达到 MAX_TOOL_ROUNDS 后强制结束
    """

    messages: Annotated[list, add_messages]
    code_summary: str
    doc_content: str
    tool_rounds: int


# 当前题型：XSS（跨站脚本）。目标是发现输入点、分析反射/存储位置与编码情况，构造并验证 XSS  payload。
tools = [nmap_scan, dirsearch_scan, read_web_file, web_request, check_xss, read_doc]
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY", ""),
    openai_api_base="https://api.deepseek.com",
    request_timeout=120,
)
llm_with_tools = llm.bind_tools(tools)



def chatbot(state: State, config: RunnableConfig | None = None) -> Any:
    """核心 LLM 节点。

    会把 `doc_content`（read_doc 结果）和 `code_summary` 放在系统提示最前面，让 LLM 每轮优先看到。
    """
    summary_prefix = ""
    doc_content = state.get("doc_content")
    if doc_content:
        summary_prefix += (
            "【以下是 read_doc 获取的技术文档（防御与绕过），请优先按文档思路测试：】\n"
            f"{doc_content}\n\n"
        )
    code_summary = state.get("code_summary")
    if code_summary:
        summary_prefix += (
            "【以下是你此前读取到的与 XSS 相关的页面/源码关键信息（输入点、反射位置、编码与过滤），请在构造 payload 时优先参考：】\n"
            f"{code_summary}\n\n"
        )

    # 系统提示：XSS 渗透测试 Agent
    sys_msg = SystemMessage(
        content=(
            summary_prefix
            + "你是 XSS 渗透测试助手，发现并验证反射型/存储型 XSS，目标弹窗为 alert('success')。\n"
            "工具：nmap_scan、dirsearch_scan、read_web_file、web_request、check_xss、read_doc。**必须先调用 read_doc(\"xss\") 获取 XSS 防御与绕过文档，再按文档思路进行测试。**\n"
            "web_request 只返回 HTML 不执行 JS，无法判断弹窗；只有 check_xss(url) 能在浏览器中探测。构造候选 URL 后应对该 URL 调用 check_xss，以 alert_detected 为准；少用 web_request 做“验证”。web_request 仅允许 GET/POST。\n"
            "要点：找输入点与反射上下文→选 payload（<script>、<img onerror=>、<svg onload=> 及大小写/换标签/双写/编码等绕过）→每试一个 URL 就 check_xss。\n"
            "结束：check_xss 返回 alert_detected 为 true 则给出成功结论并结束；主要点与常见 payload 都试过仍无则给出结论并结束。\n"
        ),
    )
    # 将系统提示和历史消息组合
    messages = [sys_msg] + state["messages"]
    ai_message = llm_with_tools.invoke(messages)
    return {"messages": [ai_message]}


def final_llm(state: State, config: RunnableConfig | None = None) -> Any:
    """达到最大工具轮数后强制要求给出结论，不再调用工具。"""
    summary_prefix = ""
    if state.get("doc_content"):
        summary_prefix += "【技术文档】\n" + state["doc_content"][:2000] + "\n\n"
    if state.get("code_summary"):
        summary_prefix += "【源码摘要】\n" + state["code_summary"][:1500] + "\n\n"
    sys_msg = SystemMessage(
        content=summary_prefix
        + f"已达最大工具轮数（{MAX_TOOL_ROUNDS}），请**直接给出最终结论**，不要调用任何工具。简要总结已尝试的输入点、payload 与 check_xss 结果，并给出是否发现 XSS 的结论。"
    )
    messages = [sys_msg] + state["messages"]
    ai_message = llm.invoke(messages)
    return {"messages": [ai_message]}


def _summarize_source(raw_content: str) -> str:
    """内部工具：对 read_web_file 读到的源码/页面内容做一次与 XSS 相关的摘要。

    说明：
    - 不是对外暴露的 LangChain 工具，而是在工具执行后自动调用
    - 输出会存进 State 的 `code_summary` 字段中，供后续每轮对话使用
    """
    try:
        system = SystemMessage(
            content=(
                "你是 XSS 代码审计助手。请用不超过150字指出：页面中的输入点（URL 参数、表单名、Cookie/Header 使用）、"
                "用户输入在 HTML 中的输出位置与上下文（标签内、属性、JS 字符串、URL）、是否存在编码/转义（如 htmlspecialchars、escape）、"
                "以及可尝试的 payload 类型与绕过思路（如事件处理器、编码绕过、闭合上下文）。"
            )
        )
        human = HumanMessage(
            content=f"下面是完整内容，请直接给出与 XSS 相关的摘要：\n\n=== 内容开始 ===\n{raw_content}\n=== 内容结束 ==="
        )
        resp = llm.invoke([system, human])
        return resp.content if hasattr(resp, "content") else str(resp)
    except Exception as e:
        return f"（源码摘要自动生成失败：{e}）"


def tool_executor(state: State, config: RunnableConfig | None = None) -> Any:
    tools_by_name = {tool.name: tool for tool in tools}
    tool_calls = state["messages"][-1].tool_calls
    messages = []
    accumulated_summary = state.get("code_summary", "")
    accumulated_doc = state.get("doc_content", "")

    for tool_call in tool_calls:
        print(f"---- 正在执行工具: {tool_call['name']} 参数: {tool_call['args']} ---")
        tool = tools_by_name[tool_call["name"]]
        raw_content = tool.invoke(tool_call["args"])
        content = raw_content
        if isinstance(content, str) and len(content) > MAX_TOOL_RESULT_CHARS:
            content = content[:MAX_TOOL_RESULT_CHARS] + "\n\n...(结果已截断，超出上下文限制)"
        messages.append(ToolMessage(tool_call_id=tool_call["id"], content=json.dumps(content, ensure_ascii=False) if not isinstance(content, str) else content, name=tool_call["name"]))

        if tool_call["name"] == "read_web_file" and isinstance(raw_content, str) and raw_content.strip():
            summary = _summarize_source(raw_content)
            accumulated_summary = accumulated_summary + "\n\n---\n\n" + summary if accumulated_summary else summary
        if tool_call["name"] == "read_doc" and isinstance(raw_content, str) and raw_content.strip():
            accumulated_doc = accumulated_doc + "\n\n---\n\n" + raw_content if accumulated_doc else raw_content

    result: State = {"messages": messages, "tool_rounds": state.get("tool_rounds", 0) + 1}
    if accumulated_summary:
        result["code_summary"] = accumulated_summary
    if accumulated_doc:
        result["doc_content"] = accumulated_doc
    return result


def route(state: State, config: RunnableConfig | None = None) -> Literal["tool_executor", "final_llm", "__end__"]:
    ai_message = state["messages"][-1]
    tool_rounds = state.get("tool_rounds", 0)
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        if tool_rounds >= MAX_TOOL_ROUNDS:
            return "final_llm"
        return "tool_executor"
    return END

def print_banner_colored() -> None:
    art = [
    " ██████╗████████╗███████╗ █████╗  ██████╗ ███████╗███╗   ██╗████████╗",
    "██╔════╝╚══██╔══╝██╔════╝██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝",
    "██║        ██║   █████╗  ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║",
    "██║        ██║   ██╔══╝  ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║",
    "╚██████╗   ██║   ██║     ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║",
    " ╚═════╝   ╚═╝   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝",
    "=========================Author:矛盾实验室=========================="
    ]
    DEEP_GREEN = "\033[38;5;22m"
    RESET = "\033[0m"

    if sys.stdout.isatty():
        for line in art:
            print(DEEP_GREEN + line + RESET)
    else:
        for line in art:
            print(line)


# --- 步骤 3：构建与运行 ---

def main() -> None:
    """简单的命令行入口，演示如何运行整个 Agent。"""
    graph_builder = StateGraph(State)
    graph_builder.add_node("llm", chatbot)
    graph_builder.add_node("tool_executor", tool_executor)
    graph_builder.add_node("final_llm", final_llm)
    graph_builder.add_edge(START, "llm")
    graph_builder.add_edge("tool_executor", "llm")
    graph_builder.add_conditional_edges("llm", route)
    graph_builder.add_edge("final_llm", END)
    graph = graph_builder.compile()
    print_banner_colored()
    print("\nAgent 启动，进入 XSS 渗透模式...")
    target = "http://a27d1b2a-620f-48dd-9d85-7a49cacffe6c.challenge.ctf.show/"
    state = graph.invoke(
        {"messages": [("human", f"目标为 {target}。请发现 XSS 输入点，构造 payload 使页面弹出 alert('success')，并用 check_xss(完整 URL) 在浏览器中验证；若返回 alert_detected 为 true 即成功并结束。")]},
        config={"recursion_limit": 100},
    )

    # 打印完整 messages 列表
    print("\n" + "=" * 50)
    print("完整 messages：")
    print("=" * 50)
    print(state.get("messages", []))

    print("\n" + "=" * 20 + " 渗透日志 " + "=" * 20)
    for message in state["messages"]:
        role = "AI" if message.type == "ai" else ("TOOL" if message.type == "tool" else "User")
        content = message.content if hasattr(message, "content") else str(message)
        print(f"[{role}]: {content}")
        # 若 AI 消息包含 tool_calls，则额外打印其内容（工具名与参数）
        if message.type == "ai" and hasattr(message, "tool_calls") and message.tool_calls:
            print("[AI tool_calls]:")
            for tc in message.tool_calls:
                name = tc.get("name")
                args = tc.get("args")
                tc_id = tc.get("id")
                if tc_id:
                    print(f"- {name} (id={tc_id}) args={args}")
                else:
                    print(f"- {name} args={args}")


if __name__ == "__main__":
    main()