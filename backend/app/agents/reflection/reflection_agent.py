from langgraph.graph import StateGraph, END
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.services.gemini_service import get_gemini_service

from .schemas import ReflectionInput, ReflectionOutput
from .prompts import REFLECTION_PROMPT

class ReflectionAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            template=REFLECTION_PROMPT,
            input_variables=["github_issue", "generated_code", "test_failures"],
        )
        self.output_parser = JsonOutputParser(pydantic_object=ReflectionOutput)

    def _create_graph(self):
        graph = StateGraph(ReflectionInput)
        graph.add_node("reflection", self._reflection_node)
        graph.set_entry_point("reflection")
        graph.add_edge("reflection", END)
        return graph.compile()

    def _reflection_node(self, state: ReflectionInput):
        chain = self.prompt_template | self.llm | self.output_parser
        
        result = chain.invoke({
            "github_issue": state.github_issue,
            "generated_code": state.generated_code.model_dump_json(),
            "test_failures": state.test_failures.model_dump_json()
        })
        
        return result

    def run(self, reflection_input: ReflectionInput):
        graph = self._create_graph()
        return graph.invoke(reflection_input)

def get_reflection_agent():
    gemini_service = get_gemini_service()
    return ReflectionAgent(gemini_service.model)
