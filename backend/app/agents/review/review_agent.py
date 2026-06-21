from langgraph.graph import StateGraph, END
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.services.gemini_service import get_gemini_service

from .schemas import ReviewInput, ReviewReport
from .prompts import REVIEW_PROMPT

class ReviewAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            template=REVIEW_PROMPT,
            input_variables=["modified_code"],
        )
        self.output_parser = JsonOutputParser(pydantic_object=ReviewReport)

    def _create_graph(self):
        graph = StateGraph(ReviewInput)
        graph.add_node("review", self._review_node)
        graph.set_entry_point("review")
        graph.add_edge("review", END)
        return graph.compile()

    def _review_node(self, state: ReviewInput):
        chain = self.prompt_template | self.llm | self.output_parser
        
        result = chain.invoke({
            "modified_code": state.modified_code.model_dump_json()
        })
        
        return {"suggestions": result.get("suggestions", [])}

    def run(self, review_input: ReviewInput):
        graph = self._create_graph()
        return graph.invoke(review_input)

def get_review_agent():
    gemini_service = get_gemini_service()
    return ReviewAgent(gemini_service.model)
