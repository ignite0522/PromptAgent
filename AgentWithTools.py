import json
from typing import TypedDict, Annotated, Any, Literal

import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

dotenv.load_dotenv()


class GoogleSerperArgsSchema(BaseModel):
   query: str = Field(description="执行谷歌搜索的查询语句")


# 1.定义工具与工具列表
google_serper = GoogleSerperRun(
   name="google_serper",
   description=(
       "一个低成本的谷歌搜索API。"
       "当你需要回答有关时事的问题时，可以调用该工具。"
       "该工具的输入是搜索查询语句。"
   ),
   args_schema=GoogleSerperArgsSchema,
   api_wrapper=GoogleSerperAPIWrapper(),
)


class State(TypedDict):
   """图状态数据结构，类型为字典"""
   messages: Annotated[list, add_messages]


tools = [google_serper]
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key="sk-4c60e118b9874e4bb945567863620949",
    openai_api_base="https://api.deepseek.com",
    request_timeout=120,  # 超时设置，避免无限等待
)
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State, config: RunnableConfig | None = None) -> Any:
   """聊天机器人函数"""
   # 1.获取状态里存储的消息列表数据并传递给LLM
   ai_message = llm_with_tools.invoke(state["messages"])
   # 2.返回更新/生成的状态
   return {"messages": [ai_message]}


def tool_executor(state: State, config: RunnableConfig | None = None) -> Any:
   """工具调用执行节点"""
   # 1.构建工具名字映射字典
   tools_by_name = {tool.name: tool for tool in tools}

   # 2.提取最后一条消息里的工具调用信息
   tool_calls = state["messages"][-1].tool_calls

   # 3.循环遍历执行工具
   messages = []
   for tool_call in tool_calls:
       # 4.获取需要执行的工具
       tool = tools_by_name[tool_call["name"]]
       # 5.执行工具并将工具结果添加到消息列表中
       messages.append(ToolMessage(
           tool_call_id=tool_call["id"],
           content=json.dumps(tool.invoke(tool_call["args"])),
           name=tool_call["name"]
       ))

   # 6.返回更新的状态信息
   return {"messages": messages}


def route(state: State, config: RunnableConfig | None = None) -> Literal["tool_executor", "__end__"]:
   """动态选择工具执行亦或者结束"""
   # 1.获取生成的最后一条消息
   ai_message = state["messages"][-1]
   # 2.检测消息是否存在tool_calls参数，如果是则执行`工具路由`
   if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
       return "tool_executor"
   # 3.否则生成的内容是文本信息，则跳转到结束路由
   return END


# 1.创建状态图，并使用GraphState作为状态数据
graph_builder = StateGraph(State)

# 2.添加节点
graph_builder.add_node("llm", chatbot)
graph_builder.add_node("tool_executor", tool_executor)

# 3.添加边
graph_builder.add_edge(START, "llm")
graph_builder.add_edge("tool_executor", "llm")
graph_builder.add_conditional_edges("llm", route)

# 4.编译图为Runnable可运行组件
graph = graph_builder.compile()

# 5.调用图架构应用
print("开始执行...")
state = graph.invoke(
    {"messages": [("human", "成都今天天气如何？")]},
    config={"recursion_limit": 25},
)

# 打印完整 messages 列表
print("\n" + "=" * 50)
print("完整 messages：")
print("=" * 50)
print(state.get("messages", []))
