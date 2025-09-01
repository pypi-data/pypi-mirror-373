"""
Built-in tools for Maximum Continual Training agent
"""

import json
from typing import Any, List, Dict, Optional
from maximum_continual.base_tools import Tool
from pydantic import BaseModel
from .local_python_executor import LocalPythonExecutor, CodeOutput


class FinalAnswerTool(Tool):
    """Tool for providing the final answer"""
    inputs = {
        "answer": {
            "type": "object",
            "description": "The final answer object"
        }
    }
    output_type = "object"
    description = "Provide the final answer to the user's question"
    name="final_answer"
    def __init__(self, final_answer_model: Optional[BaseModel] = None):
        self.final_answer_model = final_answer_model
        if self.final_answer_model:
            self.description = f"Provide the final answer to the user's question using the following model: {self.final_answer_model.model_json_schema()}"
        super().__init__()
    
    def forward(self, answer: Dict[str, Any]) -> BaseModel | Dict[str, Any]:
        """Process and return the final answer"""
        if self.final_answer_model:
            return self.final_answer_model.model_validate(answer)
        return answer


class CodeExecutorTool(Tool):
    """Tool for executing Python code using LocalPythonExecutor"""
    name= "code_executor"
    description = "Execute Python code with access to provided tools"
    inputs = {
       
        "thinking": {
            "type": "string",
            "description": "Thoughts about the code execution."
        },
         "code": {
            "type": "string",
            "description": "Python code to execute"
        },
    }
    output_type = "object"
    def __init__(self, 
                available_tools: List[Tool] = [],
                additional_authorized_imports: List[str] = [],
                final_answer_model: Optional[BaseModel] = None,
                max_print_outputs_length=10000,
                ):
        assert all(isinstance(tool, Tool) for tool in available_tools), "All elements must be instance of Tool (or a subclass)"
        self.tools = {tool.name: tool for tool in available_tools}
        print("#"*100, self.tools)
        if "final_answer" not in self.tools:
            self.tools["final_answer"] = FinalAnswerTool(final_answer_model=final_answer_model)
        self.max_print_outputs_length = max_print_outputs_length
        self.python_executor = LocalPythonExecutor(additional_authorized_imports=additional_authorized_imports,
                                                   max_print_outputs_length=max_print_outputs_length, 
        )
        self.python_executor.send_tools(self.tools)
        self.additional_authorized_imports = additional_authorized_imports
        self.name = "code_executor"
        self.description = "Execute Python code with access to provided tools"
        super().__init__()
        
    def forward(self, thinking: str, code: str) -> CodeOutput:
        """Execute Python code and return result"""
        print(thinking)
        print(code)
        result = self.python_executor(code)
        return result
                
