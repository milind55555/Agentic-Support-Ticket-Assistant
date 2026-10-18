import json
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from app.config import get_settings
from app.tools.support_tools import ALL_TOOLS

def get_llm():
    s = get_settings()
    if s.llm_provider == "bedrock":
        from langchain_aws import ChatBedrock
        return ChatBedrock(model_id=s.bedrock_model_id, region_name=s.aws_region)
    if s.llm_provider == "azure":
        from langchain_openai import AzureChatOpenAI
        return AzureChatOpenAI(azure_endpoint=s.azure_openai_endpoint, api_key=s.azure_openai_key,
                               azure_deployment=s.azure_openai_deployment)
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model=s.openai_model, api_key=s.openai_api_key)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda a, b: a + b]
    ticket_text: str
    classification: str
    kb_context: str
    draft_response: str
    approved: bool

def classify_node(state):
    llm = get_llm()
    prompt = f"Classify this support ticket into one of: vpn, account, billing, hardware, software, other. Ticket: {state['ticket_text']}. Reply only the category."
    cat = llm.invoke([HumanMessage(content=prompt)]).content.strip().lower()
    return {"classification": cat}

def retrieve_node(state):
    from app.rag.knowledge_base import get_retriever
    r = get_retriever(get_settings())
    docs = r.invoke(state["ticket_text"])
    ctx = "\n\n".join(d.page_content for d in docs)
    return {"kb_context": ctx}

def agent_node(state):
    llm = get_llm().bind_tools(ALL_TOOLS)
    sys = SystemMessage(content="You are an IT support agent. Use tools to look up tickets/services/customers. Use KB context. Draft a helpful response.")
    msgs = [sys, HumanMessage(content=f"Ticket: {state['ticket_text']}\nCategory: {state['classification']}\nKB:\n{state['kb_context']}")]
    if state.get("messages"):
        msgs = msgs + state["messages"]
    resp = llm.invoke(msgs)
    return {"messages": [resp]}

def should_continue(state):
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return "draft"

def draft_node(state):
    llm = get_llm()
    tool_results = "\n".join(m.content for m in state["messages"] if isinstance(m, AIMessage) is False and hasattr(m, "content"))
    prompt = f"Draft a customer-facing support response for ticket: {state['ticket_text']}\nContext: {state['kb_context']}\nTool results: {tool_results}"
    draft = llm.invoke([HumanMessage(content=prompt)]).content
    return {"draft_response": draft}

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("classify", classify_node)
    g.add_node("retrieve", retrieve_node)
    g.add_node("agent", agent_node)
    g.add_node("tools", ToolNode(ALL_TOOLS))
    g.add_node("draft", draft_node)
    g.set_entry_point("classify")
    g.add_edge("classify", "retrieve")
    g.add_edge("retrieve", "agent")
    g.add_conditional_edges("agent", should_continue, {"tools": "tools", "draft": "draft"})
    g.add_edge("tools", "agent")
    g.add_edge("draft", END)
    return g.compile()
