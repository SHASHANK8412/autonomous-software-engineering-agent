from langgraph.graph import StateGraph, END
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.services.gemini_service import get_gemini_service
from app.services.test_runner_service import get_test_runner_service

from .schemas import DebugInput, DebugOutput, CodingOutput
from .prompts import DEBUG_PROMPT

class DebugAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            template=DEBUG_PROMPT,
            input_variables=["reflection", "original_code"],
        )
        self.output_parser = JsonOutputParser(pydantic_object=CodingOutput)
        self.test_runner = get_test_runner_service()

    def _create_graph(self):
        graph = StateGraph(DebugInput)
        graph.add_node("debug", self._debug_node)
        graph.add_node("test", self._test_node)
        graph.set_entry_point("debug")
        graph.add_conditional_edges(
            "test",
            self._decide_to_finish,
            {"continue": "debug", "finish": END}
        )
        graph.add_edge("debug", "test")
        return graph.compile()

    def _debug_node(self, state: DebugInput):
        chain = self.prompt_template | self.llm | self.output_parser
        
        result = chain.invoke({
            "reflection": state.reflection.model_dump_json(),
            "original_code": state.original_code.model_dump_json()
        })
        
        return {"final_code": result}

    def _test_node(self, state: DebugInput):
        # In a real implementation, you would apply the code changes before running tests.
        # For this example, we'll simulate the test run.
        test_results = self.test_runner.run_tests() # This should target the modified code
        
        success = not test_results["report"]["summary"]["failed"]
        
        state['retries'] = state.get('retries', 0) + 1
        state['success'] = success
        
        return state

    def _decide_to_finish(self, state: DebugInput):
        if state['success'] or state['retries'] >= state['max_retries']:
            return "finish"
        else:
            return "continue"

    def run(self, debug_input: DebugInput):
        graph = self._create_graph()
        return graph.invoke(debug_input)

def get_debug_agent():
    gemini_service = get_gemini_service()
    return DebugAgent(gemini_service.model)
