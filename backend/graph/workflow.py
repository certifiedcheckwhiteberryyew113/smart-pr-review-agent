from __future__ import annotations

from typing import Any

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from backend.agents.bug_hunter import hunt_bugs
from backend.agents.fix_drafter import draft_fix
from backend.agents.indexer import index_repository
from backend.agents.issue_raiser import raise_issues
from backend.agents.reviewer import review_pr
from backend.config import settings
from backend.models.state import WorkflowState


async def indexer_node(state: WorkflowState) -> dict[str, Any]:
    """Runs the indexing agent to populate RAG context."""
    return dict(await index_repository(state))


async def reviewer_node(state: WorkflowState) -> dict[str, Any]:
    """Runs the review agent to generate confidence-scored findings."""
    return dict(await review_pr(state))


async def bug_hunter_node(state: WorkflowState) -> dict[str, Any]:
    """Runs bug hunting using review findings and RAG."""
    return dict(await hunt_bugs(state))


async def issue_raiser_node(state: WorkflowState) -> dict[str, Any]:
    """Creates GitHub issues for detected bugs."""
    return dict(await raise_issues(state))


async def fix_drafter_node(state: WorkflowState) -> dict[str, Any]:
    """Drafts and applies a code fix with tests."""
    return dict(await draft_fix(state))


async def human_approval_node(state: WorkflowState) -> dict[str, Any]:
    """Interrupts execution until approval data is provided."""
    return dict(state)


async def end_node(state: WorkflowState) -> dict[str, Any]:
    """Formats the final workflow output."""
    return dict(state)


def _confidence_from_state(state: WorkflowState) -> float:
    """Extracts reviewer confidence from workflow state."""
    review_findings = state.get("review_findings", [])
    if not review_findings:
        return 0.0
    first = review_findings[0]
    try:
        return float(first.get("confidence", 0.0))
    except Exception:
        return 0.0


def route_after_reviewer(state: WorkflowState) -> str:
    """Routes to bug hunting when reviewer confidence is low."""
    if _confidence_from_state(state) < 0.7:
        return "bug_hunter"
    return "end_node"


def route_after_issues(state: WorkflowState) -> str:
    """Routes based on mode after issue creation."""
    if state["mode"] == "review_only":
        return "end_node"
    if state["mode"] == "human_in_loop":
        return "human_approval_node"
    return "fix_drafter"


def route_after_human_approval(state: WorkflowState) -> str:
    """Routes to fixing only when approval was granted."""
    if state.get("approval_status") == "approved":
        return "fix_drafter"
    return "end_node"


def build_graph() -> StateGraph[WorkflowState]:
    """Builds an uncompiled LangGraph workflow."""
    graph: StateGraph[WorkflowState] = StateGraph(WorkflowState)
    graph.add_node("indexer", indexer_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("bug_hunter", bug_hunter_node)
    graph.add_node("issue_raiser", issue_raiser_node)
    graph.add_node("fix_drafter", fix_drafter_node)
    graph.add_node("human_approval_node", human_approval_node)
    graph.add_node("end_node", end_node)
    graph.add_edge(START, "indexer")
    graph.add_edge("indexer", "reviewer")
    graph.add_conditional_edges(
        "reviewer",
        route_after_reviewer,
        path_map={"bug_hunter": "bug_hunter", "end_node": "end_node"},
    )
    graph.add_edge("bug_hunter", "issue_raiser")
    graph.add_conditional_edges(
        "issue_raiser",
        route_after_issues,
        path_map={
            "human_approval_node": "human_approval_node",
            "fix_drafter": "fix_drafter",
            "end_node": "end_node",
        },
    )
    graph.add_conditional_edges(
        "human_approval_node",
        route_after_human_approval,
        path_map={"fix_drafter": "fix_drafter", "end_node": "end_node"},
    )
    graph.add_edge("fix_drafter", "end_node")
    graph.add_edge("end_node", END)
    return graph


def get_compiled_graph():
    """Compiles the workflow with Postgres checkpointing and approval interrupts."""
    global _COMPILED_GRAPH, _CHECKPOINTER
    if _COMPILED_GRAPH is not None:
        return _COMPILED_GRAPH
    checkpointer = None
    if settings.database_url:
        try:
            checkpointer_iter = PostgresSaver.from_conn_string(settings.database_url)
            checkpointer = next(checkpointer_iter)
            checkpointer.setup()
        except Exception:
            checkpointer = None
    if checkpointer is None:
        checkpointer = MemorySaver()
    _CHECKPOINTER = checkpointer
    _COMPILED_GRAPH = build_graph().compile(
        checkpointer=checkpointer,
        interrupt_before=["human_approval_node"],
    )
    return _COMPILED_GRAPH


_CHECKPOINTER: PostgresSaver | None = None
_COMPILED_GRAPH: Any | None = None
