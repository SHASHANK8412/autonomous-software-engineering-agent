from langgraph.graph import StateGraph, END
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.services.gemini_service import get_gemini_service

from .schemas import CodingInput, CodingOutput
from .prompts import CODING_PROMPT

class CodingAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            template=CODING_PROMPT,
            input_variables=["github_issue", "plan", "retrieved_code"],
        )
        self.output_parser = JsonOutputParser(pydantic_object=CodingOutput)

    def _create_graph(self):
        graph = StateGraph(CodingInput)
        graph.add_node("coding", self._coding_node)
        graph.set_entry_point("coding")
        graph.add_edge("coding", END)
        return graph.compile()

    def _coding_node(self, state: CodingInput):
        chain = self.prompt_template | self.llm | self.output_parser
        
        # In a real implementation, you would read the content of the files to be modified.
        # For this example, we'll just pass the retrieved code as a string.
        
        result = chain.invoke({
            "github_issue": state.github_issue,
            "plan": state.plan.model_dump_json(),
            "retrieved_code": state.retrieved_code.model_dump_json()
        })
        
        # Here you would apply the changes to the actual files.
        # For now, we just return the proposed modifications.
        return {"modified_files": result.get("modified_files", [])}

    def run(self, coding_input: CodingInput):
        graph = self._create_graph()
        return graph.invoke(coding_input)

def get_coding_agent():
    gemini_service = get_gemini_service()
    return CodingAgent(gemini_service.model)
