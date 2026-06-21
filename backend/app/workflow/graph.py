from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from app.workflow.state import WorkflowState
from app.agents.planner.planner_agent import get_planner_agent
from app.agents.repository_search.repository_search_agent import get_repository_search_agent
from app.agents.coding.coding_agent import get_coding_agent
from app.agents.reflection.reflection_agent import get_reflection_agent
from app.agents.debug.debug_agent import get_debug_agent
from app.agents.review.review_agent import get_review_agent
from app.services.test_runner_service import get_test_runner_service
from app.services.redis_service import get_redis_service
from app.db.models import SessionLocal, Issue, Plan, Log, AIResponse, WorkflowState as DBWorkflowState

# Agent and service instances
planner_agent = get_planner_agent()
repository_search_agent = get_repository_search_agent()
coding_agent = get_coding_agent()
reflection_agent = get_reflection_agent()
debug_agent = get_debug_agent()
review_agent = get_review_agent()
test_runner = get_test_runner_service()
redis_service = get_redis_service()
db = SessionLocal()

# Helper functions
def log_to_db(message, level="INFO"):
    log_entry = Log(message=message, level=level)
    db.add(log_entry)
    db.commit()

def cache_ai_response(prompt, response):
    response_entry = AIResponse(prompt=prompt, response=response)
    db.add(response_entry)
    db.commit()
    redis_service.set(f"ai_response:{hash(prompt)}", response, ex=3600)

# Nodes
def planner_node(state: WorkflowState):
    log_to_db("Planner node started.")
    # Cache repository summary
    redis_service.set(f"repo_summary:{state['repository_summary']}", state['repository_summary'], ex=3600)
    
    # Save issue to DB
    issue = Issue(github_issue=state["github_issue"])
    db.add(issue)
    db.commit()
    
    plan = planner_agent.run({"github_issue": state["github_issue"], "repository_summary": state["repository_summary"]})
    
    # Save plan to DB
    db_plan = Plan(issue_id=issue.id, plan_data=plan)
    db.add(db_plan)
    db.commit()
    
    cache_ai_response(f"plan:{state['github_issue']}", plan)
    log_to_db("Planner node finished.")
    return {"plan": plan}

def repository_search_node(state: WorkflowState):
    log_to_db("Repository search node started.")
    retrieved_code = repository_search_agent.run({"github_issue": state["github_issue"], "repository_summary": state["repository_summary"]})
    cache_ai_response(f"repo_search:{state['github_issue']}", retrieved_code)
    log_to_db("Repository search node finished.")
    return {"retrieved_code": retrieved_code}

def coding_node(state: WorkflowState):
    log_to_db("Coding node started.")
    generated_code = coding_agent.run({"github_issue": state["github_issue"], "plan": state["plan"], "retrieved_code": state["retrieved_code"]})
    cache_ai_response(f"code:{state['github_issue']}", generated_code)
    log_to_db("Coding node finished.")
    return {"generated_code": generated_code}

def testing_node(state: WorkflowState):
    log_to_db("Testing node started.")
    test_results = test_runner.run_tests()
    log_to_db(f"Test results: {test_results['report']['summary']}")
    log_to_db("Testing node finished.")
    return {"test_results": test_results}

def reflection_node(state: WorkflowState):
    log_to_db("Reflection node started.")
    reflection = reflection_agent.run({"github_issue": state["github_issue"], "generated_code": state["generated_code"], "test_failures": state["test_results"]})
    cache_ai_response(f"reflection:{state['github_issue']}", reflection)
    log_to_db("Reflection node finished.")
    return {"reflection": reflection}

def debug_node(state: WorkflowState):
    log_to_db("Debug node started.")
    debug_output = debug_agent.run({"reflection": state["reflection"], "original_code": state["generated_code"]})
    cache_ai_response(f"debug:{state['github_issue']}:{state['debug_retries']}", debug_output)
    log_to_db(f"Debug attempt {state['debug_retries'] + 1} finished.")
    return {"final_code": debug_output["final_code"], "debug_retries": state["debug_retries"] + 1}

def review_node(state: WorkflowState):
    log_to_db("Review node started.")
    code_to_review = state.get("final_code") or state.get("generated_code")
    review_report = review_agent.run({"modified_code": code_to_review})
    cache_ai_response(f"review:{state['github_issue']}", review_report)
    log_to_db("Review node finished.")
    return {"review_report": review_report}

# Conditional Edges
def should_reflect_or_review(state: WorkflowState):
    if state["test_results"]["report"]["summary"]["failed"] > 0:
        return "reflection"
    else:
        return "review"

def should_debug_or_fail(state: WorkflowState):
    if state["debug_retries"] < 3: # Max retries
        return "debug"
    else:
        log_to_db("Max debug retries reached. Workflow failed.", level="ERROR")
        return END

# Graph Definition
def create_main_workflow():
    # Using a database for checkpoints would be more robust
    memory = SqliteSaver.from_conn_string(":memory:")
    workflow = StateGraph(WorkflowState, checkpointer=memory)

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
    workflow.add_conditional_edges("testing", should_reflect_or_review, {
        "reflection": "reflection",
        "review": "review"
    })
    workflow.add_edge("reflection", "debug")
    workflow.add_conditional_edges("debug", should_debug_or_fail, {
        "debug": "testing", # Retry testing after debug
        "fail": END
    })
    workflow.add_edge("review", END) # Or to a GitHub node

    return workflow.compile()
