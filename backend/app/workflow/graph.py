import json

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.agents.coding.coding_agent import get_coding_agent
from app.agents.debug.debug_agent import get_debug_agent
from app.agents.planner.planner_agent import get_planner_agent
from app.agents.reflection.reflection_agent import get_reflection_agent
from app.agents.repository_search.repository_search_agent import get_repository_search_agent
from app.agents.review.review_agent import get_review_agent
from app.db.models import DBSessionLocal, Issue, Log, Plan
from app.services.redis_service import get_redis_service
from app.services.test_runner_service import get_test_runner_service
from app.services.workflow_event_service import get_workflow_event_service
from app.workflow.state import WorkflowState

workflow_events = get_workflow_event_service()
redis_service = get_redis_service()
test_runner = get_test_runner_service()

_planner_agent = None
_repository_search_agent = None
_coding_agent = None
_reflection_agent = None
_debug_agent = None
_review_agent = None


def _get_planner_agent():
    global _planner_agent
    if _planner_agent is None:
        _planner_agent = get_planner_agent()
    return _planner_agent


def _get_repository_search_agent():
    global _repository_search_agent
    if _repository_search_agent is None:
        _repository_search_agent = get_repository_search_agent()
    return _repository_search_agent


def _get_coding_agent():
    global _coding_agent
    if _coding_agent is None:
        _coding_agent = get_coding_agent()
    return _coding_agent


def _get_reflection_agent():
    global _reflection_agent
    if _reflection_agent is None:
        _reflection_agent = get_reflection_agent()
    return _reflection_agent


def _get_debug_agent():
    global _debug_agent
    if _debug_agent is None:
        _debug_agent = get_debug_agent()
    return _debug_agent


def _get_review_agent():
    global _review_agent
    if _review_agent is None:
        _review_agent = get_review_agent()
    return _review_agent


def _db_session():
    return DBSessionLocal()


def _store_log(message: str, level: str = "INFO") -> None:
    session = _db_session()
    try:
        session.add(Log(message=message, level=level))
        session.commit()
    finally:
        session.close()


def _store_issue_and_plan(github_issue: str, plan: dict) -> None:
    session = _db_session()
    try:
        issue = Issue(github_issue=github_issue)
        session.add(issue)
        session.commit()
        session.refresh(issue)
        session.add(Plan(issue_id=issue.id, plan_data=plan))
        session.commit()
    finally:
        session.close()


def _store_ai_response(prompt: str, response) -> None:
    payload = response.model_dump() if hasattr(response, "model_dump") else response
    workflow_events.log_ai_response(prompt, json.dumps(payload, default=str))
    redis_service.set(f"ai_response:{hash(prompt)}", payload, ex=3600)


def _advance(state: WorkflowState, agent: str, progress: int, message: str) -> None:
    workflow_events.update(
        workflow_id=state.get("workflow_id"),
        status=state.get("status") or "running",
        current_agent=agent,
        progress=progress,
        last_message=message,
        repository_summary=state.get("repository_summary"),
    )
    workflow_events.add_log(message)
    _store_log(message)


def planner_node(state: WorkflowState):
    _advance(state, "Planner", 10, "Planner node started.")
    workflow_events.set_repository_summary(state["repository_summary"])
    workflow_events.mark_issue(state["github_issue"])

    plan_state = _get_planner_agent().run({"github_issue": state["github_issue"], "repository_summary": state["repository_summary"]})
    plan = plan_state.get("plan") if isinstance(plan_state, dict) else plan_state
    serialized_plan = plan.model_dump() if hasattr(plan, "model_dump") else plan
    _store_issue_and_plan(state["github_issue"], serialized_plan)
    _store_ai_response(f"plan:{state['github_issue']}", serialized_plan)

    _advance(state, "Planner", 20, "Planner node finished.")
    return {"plan": plan}


def repository_search_node(state: WorkflowState):
    _advance(state, "Repository Search", 30, "Repository search node started.")
    retrieved_state = _get_repository_search_agent().run({"github_issue": state["github_issue"], "repository_summary": state["repository_summary"]})
    retrieved_code = retrieved_state.get("retrieved_code") if isinstance(retrieved_state, dict) else retrieved_state
    _store_ai_response(f"repo_search:{state['github_issue']}", retrieved_code)
    _advance(state, "Repository Search", 40, "Repository search node finished.")
    return {"retrieved_code": retrieved_code}


def coding_node(state: WorkflowState):
    _advance(state, "Coding", 50, "Coding node started.")
    generated_state = _get_coding_agent().run({"github_issue": state["github_issue"], "plan": state["plan"], "retrieved_code": state["retrieved_code"]})
    generated_code = generated_state.get("modified_files") if isinstance(generated_state, dict) else generated_state
    _store_ai_response(f"code:{state['github_issue']}", generated_code)
    _advance(state, "Coding", 60, "Coding node finished.")
    return {"generated_code": {"modified_files": generated_code} if not isinstance(generated_code, dict) else generated_code}


def testing_node(state: WorkflowState):
    _advance(state, "Testing", 70, "Testing node started.")
    test_results = test_runner.run_tests()
    _store_log(f"Test results: {test_results.get('report', {}).get('summary', {})}")
    _advance(state, "Testing", 75, "Testing node finished.")
    return {"test_results": test_results}


def reflection_node(state: WorkflowState):
    _advance(state, "Reflection", 80, "Reflection node started.")
    reflection_state = _get_reflection_agent().run({"github_issue": state["github_issue"], "generated_code": state["generated_code"], "test_failures": state["test_results"]})
    reflection = reflection_state.get("reflection") if isinstance(reflection_state, dict) else reflection_state
    _store_ai_response(f"reflection:{state['github_issue']}", reflection)
    _advance(state, "Reflection", 85, "Reflection node finished.")
    return {"reflection": reflection}


def debug_node(state: WorkflowState):
    retries = state.get("debug_retries", 0)
    _advance(state, "Debug", 88, f"Debug attempt {retries + 1} started.")
    debug_state = _get_debug_agent().run({"reflection": state["reflection"], "original_code": state["generated_code"]})
    final_code = debug_state.get("final_code") if isinstance(debug_state, dict) else debug_state
    retry_count = debug_state.get("retries", retries + 1) if isinstance(debug_state, dict) else retries + 1
    _store_ai_response(f"debug:{state['github_issue']}:{retry_count}", final_code)
    _advance(state, "Debug", 92, f"Debug attempt {retry_count} finished.")
    return {"final_code": final_code, "debug_retries": retry_count}


def review_node(state: WorkflowState):
    _advance(state, "Review", 95, "Review node started.")
    code_to_review = state.get("final_code") or state.get("generated_code")
    review_state = _get_review_agent().run({"modified_code": code_to_review})
    review_report = review_state.get("suggestions") if isinstance(review_state, dict) else review_state
    _store_ai_response(f"review:{state['github_issue']}", review_report)
    _advance(state, "Review", 100, "Review node finished.")
    workflow_events.update(status="completed", current_agent="Review", progress=100, last_message="Workflow completed")
    return {"review_report": review_report}


def should_reflect_or_review(state: WorkflowState):
    failed = state["test_results"]["report"]["summary"]["failed"]
    return "reflection" if failed > 0 else "review"


def should_debug_or_finish(state: WorkflowState):
    return "retry" if state.get("debug_retries", 0) < 3 else "finish"


def create_main_workflow():
    workflow = StateGraph(WorkflowState, checkpointer=MemorySaver())

    workflow.add_node("planner", planner_node)
    workflow.add_node("repository_search", repository_search_node)
    workflow.add_node("coding", coding_node)
    workflow.add_node("testing", testing_node)
    workflow.add_node("reflection", reflection_node)
    workflow.add_node("debug", debug_node)
    workflow.add_node("review", review_node)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "repository_search")
    workflow.add_edge("repository_search", "coding")
    workflow.add_edge("coding", "testing")
    workflow.add_conditional_edges("testing", should_reflect_or_review, {"reflection": "reflection", "review": "review"})
    workflow.add_edge("reflection", "debug")
    workflow.add_conditional_edges("debug", should_debug_or_finish, {"retry": "testing", "finish": END})
    workflow.add_edge("review", END)

    return workflow.compile()
