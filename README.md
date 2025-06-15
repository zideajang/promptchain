# PromptChain

promptchain 定位是一个轻量级的 LLM-based 的框架 。面向人群为个人开发人员，想要快速开发 LLM based 应用，promptchain 作为 tinychain 的前身， 作为一个试探性的项目。转眼间过了大半年，周围的生态在这短短时间里发生很大变换，自己也在 Agent 框架上积攒了一些经验，所以才有底气重构并且也准备将细节分享给大家。

[Prompt Chain](assets/logo.png)


## 动态
- 对 deepseek 的支持，整个项目现在转向优先支持 Deepseek 模型系列，近期推出新功能都是先支持 deepseek 的模型系列，然后才会推出支持 ollama 平台上的模型
- 对 MCP 支持

作为这些代码开发人员角度逐行解释代码，作为视频稿件




首先从整体上，给出这些代码的一个共同点就是为了实现链式调用函数内部都实现 invoke 函数



不用过于拘泥细节对于每个函数整体概括，对于其中关键点以及其实现逻辑给出解释即可，注意解释连贯性，避免逐行解释。



以函数为单位，给出简单易懂口语化的解释说明


## 目标
是一个轻量级的 prompt chain，面向个人的 agent 框架，prompt chain 是 tinychain 的前身，主要目的用于探索 agent 实现路线 
这个prompt chain 框架目标是典型函数式编程的范例

## 特点
- 轻量级，低成本引入到现有的框架
- 支持多语言版本，例如 JavaScript、Typescript、java、go、rust、c、cpp 和 scala
- 在框架中遵从了一切都是函数的基本思想
- 是一个基于事件传递信息的框架


## 相关设计模式
- 状态机
- 观察者模式
- 责任链设计模式

```python
task [task agent[prompt | model | response] | agent[prompt | model | respone] outputcheck(target fn)-> task
```

- 最小执行单元就是 agent 



## 使用
```pyhton
response = build_model("llama3")("write read csv file in python")
```
```python
response = build_chat_model("llama3")("you are linux operating system")("ls command")
```

## 支持链式调用
```
chain | assistant_message | humam_message | model |print_markdown_tool
```
- 以`|` 连接多个操作(或者处理单元)
- 首先初始化 chain 
- assistant_messags Y

```python
async def main():
    system_message = SystemMessage(content="you are linux system")
    
    assistant_message = AIMessagePromptTemplate.from_template("you are very help assistant")
    humam_message = HumanMessagePromptTemplate.from_template("ls")

    model = ChatMessageModel("llama3")
    
    chain = ChainProcessor(Messages(messages=[system_message]))

    print_markdown_tool = PrintMarkdownTool(name="print markdown",description="print markdown")
    
    chain | assistant_message | humam_message | model |print_markdown_tool
    await chain.invoke()
    print(chain.messages)
```


为了增强 prompt 连续性，基于实际经验提出几种常用策略，
- inverse prompt
- snowball prompt

## 模块





# Function calling
## 目标
让大模型学会如何去使用工具，也就是增加大语言模型的自由度