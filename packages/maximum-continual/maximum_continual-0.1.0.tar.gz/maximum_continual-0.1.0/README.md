# Maximum Continual

A clean API for continual learning with LoRA models using reward-based feedback [[memory:6774509]].

## Overview

Maximum Continual is a Python library that enables continuous learning for AI agents through:

- **Agent-based Architecture**: Uses a code execution agent with tool access
- **LoRA Integration**: Leverages Low-Rank Adaptation for efficient model fine-tuning
- **Modal Backend**: Scalable cloud-based model hosting and training
- **Reward-based Learning**: Updates models based on performance feedback
- **Tool System**: Extensible framework for custom tools and capabilities

## Quick Start

### Installation

The project uses Poetry for dependency management [[memory:6774508]]:

```bash
pip install -e .
```

### Basic Usage

```python
from maximum_continual import MaximumContinual, Tool, MessageT
from maximum_continual.system_prompt import fetch_default_system_prompt
from maximum_continual.types import PredictionResponseWithRewardT
from pydantic import BaseModel

# Define a custom tool
class WebSearchTool(Tool):
    name = "web_search"
    description = "Performs a web search and returns results"
    inputs = {"query": {"type": "string", "description": "Search query"}}
    output_type = "string"
    
    def forward(self, query: str) -> str:
        # Implementation here
        return "Search results..."

# Define response structure
class FinalAnswer(BaseModel):
    answer: str
    reasoning: str

# Initialize client
client = MaximumContinual(auto_deploy=True)

# Create and use a model
with client.init_model(model_id="my_model") as model:
    tools = [WebSearchTool()]
    
    # Make a prediction
    response = model.predict(
        messages=[
            MessageT(role="system", content=fetch_default_system_prompt(
                tools, 
                additional_authorized_imports=["os"], 
                final_answer_model=FinalAnswer
            )),
            MessageT(role="user", content="Search for information about Python")
        ],
        final_answer_model=FinalAnswer,
        tools=tools,
        additional_authorized_imports=["os"]
    )
    
    # Update model with reward feedback
    model.update([
        PredictionResponseWithRewardT(
            prediction=response,
            reward=1.0  # Positive reward for good performance
        )
    ])
```

## Architecture

### Core Components

#### 1. MaximumContinual Client
The main entry point that handles:
- Modal backend deployment and management
- Model lifecycle (initialization, loading, cleanup)
- Backend health monitoring

#### 2. Agent System
- **MaximumContinualAgent**: Orchestrates the agent loop
- **CodeExecutorTool**: Executes Python code with tool access
- **LocalPythonExecutor**: Sandboxed Python execution environment

#### 3. Backend Infrastructure
- **Modal Backend**: Cloud-based model hosting and LoRA training
- **vLLM Backend**: High-performance model inference
- **LoRA Management**: Dynamic adapter loading and unloading

#### 4. Tool System
- **Base Tools**: Foundation for creating custom tools
- **Tool Validation**: Ensures tool safety and compatibility
- **State Persistence**: Tools maintain state across executions

### How It Works

1. **Model Initialization**: Creates or loads an existing model with optional LoRA adapters
2. **Agent Loop**: 
   - Receives messages and available tools
   - Uses code executor to run Python code
   - Tools are accessible as Python functions within the execution environment
   - Iterates until final answer is provided
3. **Reward Learning**: Models are updated based on prediction quality feedback
4. **Continuous Improvement**: LoRA adapters fine-tune model behavior over time

## API Reference

### MaximumContinual

Main client class for interacting with the system.

```python
client = MaximumContinual(
    modal_app_name: str = "maximum-continual",
    auto_deploy: bool = True
)
```

**Parameters:**
- `modal_app_name`: Name for the Modal application
- `auto_deploy`: Whether to automatically deploy the Modal backend

### MaximumContinualModel

Model instance for making predictions and updates.

#### predict()

```python
response = model.predict(
    messages: List[MessageT],
    tools: List[Tool] = [],
    additional_authorized_imports: List[str] = [],
    final_answer_model: Optional[BaseModel] = None,
    **kwargs
) -> PredictionResponseT
```

**Parameters:**
- `messages`: Conversation history
- `tools`: Available tools for the agent
- `additional_authorized_imports`: Python modules the agent can import
- `final_answer_model`: Pydantic model for structured responses

#### update()

```python
model.update(predictions: List[PredictionResponseWithRewardT]) -> None
```

Updates the model with reward feedback to improve future performance.

### Tool Creation

Create custom tools by extending the `Tool` class:

```python
class CustomTool(Tool):
    name = "custom_tool"
    description = "Description of what the tool does"
    inputs = {
        "param1": {"type": "string", "description": "Parameter description"},
        "param2": {"type": "integer", "description": "Another parameter"}
    }
    output_type = "string"
    
    def forward(self, param1: str, param2: int) -> str:
        # Tool implementation
        return "Result"
```

## Types

### Core Types

```python
class MessageT(BaseModel):
    """Chat message format"""
    role: str
    content: str
    tool_calls: Optional[List[ToolCallT]] = None
    tool_call_id: Optional[str] = None

class PredictionResponseT(BaseModel):
    """Response from prediction"""
    final_response: BaseModel
    messages: List[MessageT]
    metadata: Optional[Dict[str, Any]] = None

class PredictionResponseWithRewardT(BaseModel):
    """Prediction with reward feedback"""
    prediction: PredictionResponseT
    reward: float
```

## Advanced Usage

### Custom System Prompts

```python
from maximum_continual.system_prompt import fetch_default_system_prompt

system_prompt = fetch_default_system_prompt(
    tools=my_tools,
    authorized_imports=["requests", "json", "pandas"],
    final_answer_model=MyResponseModel
)
```

### State Persistence

The code execution environment maintains state across calls:

```python
# First execution: define variables
code1 = "data = {'count': 0}"

# Second execution: use previous variables  
code2 = "data['count'] += 1; print(data)"
```

### Error Handling

Tools should implement proper error handling:

```python
class SafeTool(Tool):
    def forward(self, input_data: str) -> str:
        try:
            # Tool logic here
            return result
        except Exception as e:
            return f"Error: {str(e)}"
```

## Examples

### Web Search Agent

See `basic_example.py` for a complete example of building a web search agent with reward-based learning.

### Multi-Tool Agent

```python
tools = [
    WebSearchTool(),
    DataAnalysisTool(), 
    FileProcessorTool()
]

response = model.predict(
    messages=[system_msg, user_msg],
    tools=tools,
    final_answer_model=MyAnswer
)
```

### Custom Reward Functions

```python
def calculate_reward(response: PredictionResponseT, expected: str) -> float:
    # Custom reward logic
    accuracy = calculate_accuracy(response.final_response, expected)
    return float(accuracy)

# Apply rewards
model.update([
    PredictionResponseWithRewardT(
        prediction=response,
        reward=calculate_reward(response, ground_truth)
    )
])
```

## Modal Backend

The system automatically deploys and manages a Modal backend for:
- Model hosting with vLLM
- LoRA adapter training and storage  
- Scalable inference serving

Authentication required:
```bash
modal setup
```

## Development

### Testing

```bash
pytest tests/
```

### Code Quality

```bash
black maximum_continual/
ruff check maximum_continual/
mypy maximum_continual/
```

## Requirements

- Python ≥3.12, <3.13
- Modal account and authentication
- CUDA-compatible GPU (for model training)

## Dependencies

Key dependencies include:
- `modal`: Cloud compute platform
- `transformers`: Hugging Face model library
- `smolagents`: Agent framework and code executor
- `litellm`: Model inference abstraction
- `vllm`: High-performance model serving
- `pydantic`: Data validation and serialization

