from langgraph.graph import StateGraph, END
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.services.gemini_service import get_gemini_service

from .schemas import ExecutionPlan, PlannerInput
from .prompts import PLANNER_PROMPT

class PlannerAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            template=PLANNER_PROMPT,
            input_variables=["github_issue", "repository_summary"],
        )
        self.output_parser = JsonOutputParser(pydantic_object=ExecutionPlan)

    def _create_graph(self):
        graph = StateGraph(PlannerInput)
        graph.add_node("planner", self._planner_node)
        graph.set_entry_point("planner")
        graph.add_edge("planner", END)
        return graph.compile()

    def _planner_node(self, state: PlannerInput):
        chain = self.prompt_template | self.llm | self.output_parser
        result = chain.invoke({
            "github_issue": state.github_issue,
            "repository_summary": state.repository_summary
        })
        return {"plan": result}

    def run(self, planner_input: PlannerInput):
        graph = self._create_graph()
        return graph.invoke(planner_input)

def get_planner_agent():
    gemini_service = get_gemini_service()
    return PlannerAgent(gemini_service.model)
