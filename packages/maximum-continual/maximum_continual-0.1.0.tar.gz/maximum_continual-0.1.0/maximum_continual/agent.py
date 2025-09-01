"""
Agentic Workflow for Maximum Continual Training

Implements the agent loop using smolagents LocalPythonExecutor.
"""
from rich.text import Text
import json
from typing import Callable, List, Dict, Any, Optional
from maximum_continual.backend.vllm_backend import AbstractInferenceModel, LiteLLMModel
from pydantic import BaseModel
from .base_tools import Tool
from .types import BaseMaximumContinualModel, MessageT, PredictionResponseT
from .tools import CodeExecutorTool, FinalAnswerTool

class ProcessCodeOutputResponseT(BaseModel):
    """Response from the process_code_output function"""
    observations: str
    final_output: BaseModel | None = None
    is_final_answer: bool

class FinalAnswerResponseT(BaseModel):
    final_output : BaseModel
    observations: str

class ObservationResponseT(BaseModel):
    observations: str


class MaximumContinualAgent:
    """Agent that handles the agentic workflow loop"""
    
    def process_code_output(self,code_executor: CodeExecutorTool,**kwargs: dict) -> ProcessCodeOutputResponseT:
        final_answer = False
        try:
            code_output = code_executor.forward(**kwargs)
            final_answer = code_output.is_final_answer
            execution_outputs_console = []
            if len(code_output.logs) > 0:
                execution_outputs_console += [
                    Text("Execution logs:", style="bold"),
                    Text(code_output.logs),
                ]
            observation = "Execution logs:\n" + code_output.logs
        except Exception as e:
            observation = "Exception: " + str(e)
            if hasattr(code_executor.python_executor, "state") and "_print_outputs" in code_executor.python_executor.state:
                execution_logs = str(code_executor.python_executor.state["_print_outputs"])
                if len(execution_logs) > 0:
                    execution_outputs_console = [
                        Text("Execution logs:", style="bold"),
                        Text(execution_logs),
                    ]
                observation += "Execution logs:\n" + execution_logs
            error_msg = str(e)
            print(error_msg)
            if "Import of " in error_msg and " is not allowed" in error_msg:
                raise Exception(f"Code execution failed due to an unauthorized import - Consider passing said import under `additional_authorized_imports` when initializing your CodeAgent.")
        if final_answer:
            return FinalAnswerResponseT(final_output=code_output.output, observations=observation)
        else:
            return ObservationResponseT(observations=observation)
    
    def run_agent_loop(
        self,
        messages: List[MessageT],
        tools: List[Tool],
        additional_authorized_imports: List[str],
        final_answer_model: Optional[BaseModel],
        vllm_backend: AbstractInferenceModel,
        model_id: str,
        logger: Callable[[MessageT], None],
        max_iterations: int = 10,
        serial_only: bool = True,
        max_print_outputs_length=10000,
        **kwargs
    ) -> PredictionResponseT:
        """Run the agent loop until final answer is reached"""
        print("$"*100, "Running agent loop", tools)
        # Create built-in tools
        code_executor = CodeExecutorTool(
            available_tools=tools, 
        additional_authorized_imports=additional_authorized_imports, 
        final_answer_model=final_answer_model,
        max_print_outputs_length=max_print_outputs_length)
        # Create tool list for the model
        available_tools = [code_executor]
        # Keep track of conversation
        conversation = messages.copy()
        
        for iteration in range(max_iterations):
            # Get prediction from vLLM backend
            latest_message = vllm_backend.predict(
                messages=conversation,
                tools=available_tools,
                final_answer_model=final_answer_model,
                model_id=model_id,
                serial_only=serial_only,
                **kwargs
            )
            logger(latest_message)
            conversation.append(latest_message)
            
            # Check if model wants to use tools
            if latest_message.tool_calls:
                tool_results = []
                
                for tool_call in latest_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = tool_call.function.arguments
                    
                    # Find and execute the tool
                    tool_result = None
                    if code_executor.name == function_name:
                        tool_result_obj = self.process_code_output(code_executor, **function_args)
                        print("tool_result_obj", tool_result_obj)
                        with open("tool_result_obj.json", "w") as f:
                            f.write(tool_result_obj.model_dump_json(indent=4))
                        if isinstance(tool_result_obj, FinalAnswerResponseT):
                            return PredictionResponseT(
                                final_response=tool_result_obj.final_output,
                                messages=conversation,
                                metadata={
                                    "iterations": iteration + 1,
                                    "model_id": model_id,
                                    "max_iterations_reached": True,
                                }
                            )
                        tool_result = tool_result_obj.observations
                    
                    if tool_result is None:
                        tool_result = f"Unknown tool: {function_name}"
                    
                    # Add tool result to conversation
                    tool_response = MessageT(
                        role="tool",
                        content=str(tool_result),
                        tool_call_id=tool_call.id or ""
                    )
                    conversation.append(tool_response)
                    tool_results.append(tool_result)
                    logger(tool_response)
            
            else:
                # No tool calls - check if this is a final response
                if iteration == max_iterations - 1:
                    # Max iterations reached, return current state
                    final_response = {"content": latest_message.content}
                    if final_answer_model:
                        try:
                            final_response = final_answer_model.parse_obj({"content": latest_message.content})
                        except Exception:
                            pass
                    
                    return PredictionResponseT(
                        final_response=final_response,
                        messages=conversation,
                        metadata={
                            "iterations": iteration + 1,
                            "model_id": model_id,
                            "lora_path": vllm_backend.get_latest_lora_path(model_id),
                            "max_iterations_reached": True,
                        }
                    )
        raise ValueError("No final answer generated")
