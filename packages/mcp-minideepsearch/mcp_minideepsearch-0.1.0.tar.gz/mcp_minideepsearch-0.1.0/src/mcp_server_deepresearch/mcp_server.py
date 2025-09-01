import argparse
import asyncio
import json
import time
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ValidationError, parse_obj_as

from langchain_deepseek import ChatDeepSeek
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch


# Initialize MCP server
mcp = FastMCP("MiniDeepResearch")

# -------- 1) Planner Chain --------
PLANNER_INSTRUCTIONS = (
    "你是一个研究助理，善于将用户的需求分解成网络搜索关键词。\n"
    "给定一个需求，请制定 2 个网络搜索查询，以最好地回答该需求。\n "
    "仅返回遵循以下模式的有效 JSON：\n"
    '{{"searches": [ {{"query": "示例", "reason": "原因"}} ]}}\n'
)

class WebSearchItem(BaseModel):
    query: str
    reason: str

class WebSearchPlan(BaseModel):
    searches: List[WebSearchItem]

# -------- 2) Search Agent --------
SEARCH_INSTRUCTIONS = (
    "你是一个研究助理。给定一个搜索词，搜索网络并生成摘要。请使用中文搜索词进行搜索 "
    "每个摘要包含2-3段，共300个字左右。仅返回摘要。"
)

# -------- 3) Writer Chain --------
WRITER_PROMPT = (
    "你是一位高级研究员，负责为研究查询撰写连贯的报告。"
    "您将获得原始查询和一些初步研究。\n\n"
    "① 先给出完整的大纲；\n"
    "② 然后生成正式报告。\n\n"
    "**写作要求**：\n"
    "• 报告使用 Markdown 格式；\n"
    "• 章节清晰，层次分明；\n"
    "• markdown_report部分至少包含2000中文字 （注意需要用中文进行回复）；\n"
    "• 内容丰富、论据充分，可加入引用和数据,允许分段、添加引用、表格等；\n"
    "• 最终仅返回 JSON：\n"
    '{{"short_summary": "...", "markdown_report": "...", "follow_up_questions": ["..."]}}'
)

class ReportData(BaseModel):
    short_summary: str
    markdown_report: str
    follow_up_questions: List[str]

def create_graph(deepseek_api_key: str, tavily_api_key: str):
    # -------- 环境与模型 --------
    model = ChatDeepSeek(model="deepseek-chat", api_key=deepseek_api_key)

    planner_prompt = ChatPromptTemplate.from_messages(
        [("system", PLANNER_INSTRUCTIONS), ("human", "{query}")]
    )

    planner_chain = (
        planner_prompt
        | model.with_structured_output(WebSearchPlan, method="json_mode")  # 强制 JSON
    )

    search_tool = TavilySearch(max_results=2, topic="general", tavily_api_key=tavily_api_key)
    search_agent = create_react_agent(
        model=model,
        prompt=SEARCH_INSTRUCTIONS,
        tools=[search_tool],
    )

    writer_prompt = ChatPromptTemplate.from_messages(
        [("system", WRITER_PROMPT), ("human", "{content}")]
    )
    writer_chain = (
        writer_prompt
        | model.with_structured_output(ReportData, method="json_mode")
    )

    # -------- LangGraph 节点 --------
    def planner_node(state: MessagesState) -> Command:
        user_query = state["messages"][-1].content
        raw = planner_chain.invoke({"query": user_query})

        # raw 可能已经是 WebSearchPlan，也可能是 dict（被解析过）
        try:
            plan = parse_obj_as(WebSearchPlan, raw)
        except ValidationError:
            # 若模型只返回 ["keyword1", ...]
            if isinstance(raw, dict) and isinstance(raw.get("searches"), list):
                plan = WebSearchPlan(
                    searches=[WebSearchItem(query=q, reason="") for q in raw["searches"]]
                )
            else:
                raise

        return Command(
            goto="search_node",
            update={
                "messages": [AIMessage(content=plan.model_dump_json())],  # JSON 字符串
                "plan": plan,  # 同时保存原生对象，后面也能直接用
            },
        )

    # ---------- search_node ----------

    def search_node(state: MessagesState) -> Command:
        plan_json = state["messages"][-1].content
        plan = WebSearchPlan.model_validate_json(plan_json)
        print(plan)

        summaries = []
        for item in plan.searches:
            # ❶ 用 HumanMessage
            print(f"searching: {item.query}")
            run = search_agent.invoke({"messages": [HumanMessage(content=item.query)]})

            # ❷ 取可读内容：最后一条 ToolMessage 或 AIMessage
            msgs = run["messages"]
            readable = next(
                (m for m in reversed(msgs) if isinstance(m, (ToolMessage, AIMessage))), msgs[-1]
            )
            summaries.append(f"## {item.query}\n\n{readable.content}")
            print(f"searching summary: \n\n{readable.content}")

            # 添加30秒延迟以避免调用过于频繁
            print("等待30秒以避免调用过于频繁...")
            time.sleep(30)

        combined = "\n\n".join(summaries)
        return Command(goto="writer_node",
                       update={"messages": [AIMessage(content=combined)]})

    # ---------- writer_node ----------
    def writer_node(state: MessagesState) -> Command:
        original_query = state["messages"][0].content
        combined_summary = state["messages"][-1].content

        writer_input = (
            f"原始问题：{original_query}\n\n"
            f"搜索摘要：\n{combined_summary}"
        )
        report: ReportData = writer_chain.invoke({"content": writer_input})

        return Command(
            goto=END,
            update={"messages": [AIMessage(content=json.dumps(report.dict(), ensure_ascii=False, indent=2))]},
        )

    # -------- 构建 & 运行 Graph --------
    builder = StateGraph(MessagesState)
    builder.add_node("planner_node", planner_node)
    builder.add_node("search_node", search_node)
    builder.add_node("writer_node", writer_node)

    builder.add_edge(START, "planner_node")
    builder.add_edge("planner_node", "search_node")
    builder.add_edge("search_node", "writer_node")
    builder.add_edge("writer_node", END)

    return builder.compile()

@mcp.tool()
def deep_research(query: str) -> Dict[str, Any]:
    """
    Perform deep research on a given topic using the LangGraph-based research agent.
    
    Args:
        query (str): The research topic or question

        
    Returns:
        Dict[str, Any]: Research report containing summary, markdown report, and follow-up questions
    """
    # Create graph with provided API keys
    research_graph = create_graph(DEEPSEEK_API_KEY, TAVILY_API_KEY)
    
    # Run the graph with the query
    result = research_graph.invoke({"messages": [{"role": "user", "content": query}]})
    
    # Extract the final result from messages
    final_message = result["messages"][-1]
    content = final_message.content
    
    # Try to parse as JSON directly
    try:
        report_data = json.loads(content)
    except json.JSONDecodeError:
        # If all else fails, return as plain text
        report_data = {
            "short_summary": "Research completed",
            "markdown_report": content,
            "follow_up_questions": []
        }
    
    return report_data

def main():
    parser = argparse.ArgumentParser(description="MiniDeepResearch MCP Server")
    parser.add_argument("--deepseek-api-key", type=str, required=True, help="DeepSeek API Key")
    parser.add_argument("--tavily-api-key", type=str, required=True, help="Tavily Search API Key")
    args = parser.parse_args()
    
    # Store API keys in global context for use by tools
    global DEEPSEEK_API_KEY, TAVILY_API_KEY
    DEEPSEEK_API_KEY = args.deepseek_api_key
    TAVILY_API_KEY = args.tavily_api_key
    
    # Run the MCP server
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()