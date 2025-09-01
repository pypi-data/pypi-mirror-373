#!/usr/bin/env python
# coding=utf-8

# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import ast
import inspect
import json
import logging
import os
import sys
import tempfile
import textwrap
import types
import warnings
from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Any

from huggingface_hub import (
    CommitOperationAdd,
    create_commit,
    create_repo,
    hf_hub_download,
    metadata_update,
)

from ._function_type_hints_utils import (
    TypeHintParsingException,
    _convert_type_hints_to_json_schema,
    get_imports,
)
from .agent_types import AgentAudio, AgentImage, handle_agent_input_types, handle_agent_output_types
from .tool_validation import MethodChecker, validate_tool_attributes
from .utils import (
    BASE_BUILTIN_MODULES,
    _is_package_available,
    get_source,
    instance_to_source,
    is_valid_name,
)


if TYPE_CHECKING:
    import mcp


logger = logging.getLogger(__name__)


def validate_after_init(cls):
    original_init = cls.__init__

    @wraps(original_init)
    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.validate_arguments()

    cls.__init__ = new_init
    return cls


AUTHORIZED_TYPES = [
    "string",
    "boolean",
    "integer",
    "number",
    "image",
    "audio",
    "array",
    "object",
    "any",
    "null",
]

CONVERSION_DICT = {"str": "string", "int": "integer", "float": "number"}


class BaseTool(ABC):
    name: str

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        pass


class Tool(BaseTool):
    """
    A base class for the functions used by the agent. Subclass this and implement the `forward` method as well as the
    following class attributes:

    - **description** (`str`) -- A short description of what your tool does, the inputs it expects and the output(s) it
      will return. For instance 'This is a tool that downloads a file from a `url`. It takes the `url` as input, and
      returns the text contained in the file'.
    - **name** (`str`) -- A performative name that will be used for your tool in the prompt to the agent. For instance
      `"text-classifier"` or `"image_generator"`.
    - **inputs** (`Dict[str, Dict[str, Union[str, type, bool]]]`) -- The dict of modalities expected for the inputs.
      It has one `type`key and a `description`key.
      This is used by `launch_gradio_demo` or to make a nice space from your tool, and also can be used in the generated
      description for your tool.
    - **output_type** (`type`) -- The type of the tool output. This is used by `launch_gradio_demo`
      or to make a nice space from your tool, and also can be used in the generated description for your tool.
    - **output_schema** (`Dict[str, Any]`, *optional*) -- The JSON schema defining the expected structure of the tool output.
      This can be included in system prompts to help agents understand the expected output format. Note: This is currently
      used for informational purposes only and does not perform actual output validation.

    You can also override the method [`~Tool.setup`] if your tool has an expensive operation to perform before being
    usable (such as loading a model). [`~Tool.setup`] will be called the first time you use your tool, but not at
    instantiation.
    """

    name: str
    description: str
    inputs: dict[str, dict[str, str | type | bool]]
    output_type: str
    output_schema: dict[str, Any] | None = None

    def __init__(self, *args, **kwargs):
        self.is_initialized = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        validate_after_init(cls)

    def validate_arguments(self):
        required_attributes = {
            "description": str,
            "name": str,
            "inputs": dict,
            "output_type": str,
        }
        # Validate class attributes
        for attr, expected_type in required_attributes.items():
            attr_value = getattr(self, attr, None)
            if attr_value is None:
                raise TypeError(f"You must set an attribute {attr}.")
            if not isinstance(attr_value, expected_type):
                raise TypeError(
                    f"Attribute {attr} should have type {expected_type.__name__}, got {type(attr_value)} instead."
                )

        # Validate optional output_schema attribute
        output_schema = getattr(self, "output_schema", None)
        if output_schema is not None and not isinstance(output_schema, dict):
            raise TypeError(f"Attribute output_schema should have type dict, got {type(output_schema)} instead.")

        # - Validate name
        if not is_valid_name(self.name):
            raise Exception(
                f"Invalid Tool name '{self.name}': must be a valid Python identifier and not a reserved keyword"
            )
        # Validate inputs
        for input_name, input_content in self.inputs.items():
            assert isinstance(input_content, dict), f"Input '{input_name}' should be a dictionary."
            assert "type" in input_content and "description" in input_content, (
                f"Input '{input_name}' should have keys 'type' and 'description', has only {list(input_content.keys())}."
            )
            # Get input_types as a list, whether from a string or list
            if isinstance(input_content["type"], str):
                input_types = [input_content["type"]]
            elif isinstance(input_content["type"], list):
                input_types = input_content["type"]
                # Check if all elements are strings
                if not all(isinstance(t, str) for t in input_types):
                    raise TypeError(
                        f"Input '{input_name}': when type is a list, all elements must be strings, got {input_content['type']}"
                    )
            else:
                raise TypeError(
                    f"Input '{input_name}': type must be a string or list of strings, got {type(input_content['type']).__name__}"
                )
            # Check all types are authorized
            invalid_types = [t for t in input_types if t not in AUTHORIZED_TYPES]
            if invalid_types:
                raise ValueError(f"Input '{input_name}': types {invalid_types} must be one of {AUTHORIZED_TYPES}")
        # Validate output type
        assert getattr(self, "output_type", None) in AUTHORIZED_TYPES

        # Validate forward function signature, except for Tools that use a "generic" signature (PipelineTool, SpaceToolWrapper, LangChainToolWrapper)
        if not (
            hasattr(self, "skip_forward_signature_validation")
            and getattr(self, "skip_forward_signature_validation") is True
        ):
            signature = inspect.signature(self.forward)
            actual_keys = set(key for key in signature.parameters.keys() if key != "self")
            expected_keys = set(self.inputs.keys())
            if actual_keys != expected_keys:
                raise Exception(
                    f"In tool '{self.name}', 'forward' method parameters were {actual_keys}, but expected {expected_keys}. "
                    f"It should take 'self' as its first argument, then its next arguments should match the keys of tool attribute 'inputs'."
                )

            json_schema = _convert_type_hints_to_json_schema(self.forward, error_on_missing_type_hints=False)[
                "properties"
            ]  # This function will not raise an error on missing docstrings, contrary to get_json_schema
            for key, value in self.inputs.items():
                assert key in json_schema, (
                    f"Input '{key}' should be present in function signature, found only {json_schema.keys()}"
                )
                if "nullable" in value:
                    assert "nullable" in json_schema[key], (
                        f"Nullable argument '{key}' in inputs should have key 'nullable' set to True in function signature."
                    )
                if key in json_schema and "nullable" in json_schema[key]:
                    assert "nullable" in value, (
                        f"Nullable argument '{key}' in function signature should have key 'nullable' set to True in inputs."
                    )

    def forward(self, *args, **kwargs):
        raise NotImplementedError("Write this method in your subclass of `Tool`.")

    def __call__(self, *args, sanitize_inputs_outputs: bool = False, **kwargs):
        if not self.is_initialized:
            self.setup()

        # Handle the arguments might be passed as a single dictionary
        if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], dict):
            potential_kwargs = args[0]

            # If the dictionary keys match our input parameters, convert it to kwargs
            if all(key in self.inputs for key in potential_kwargs):
                args = ()
                kwargs = potential_kwargs

        if sanitize_inputs_outputs:
            args, kwargs = handle_agent_input_types(*args, **kwargs)
        outputs = self.forward(*args, **kwargs)
        if sanitize_inputs_outputs:
            outputs = handle_agent_output_types(outputs, self.output_type)
        return outputs

    def setup(self):
        """
        Overwrite this method here for any operation that is expensive and needs to be executed before you start using
        your tool. Such as loading a big model.
        """
        self.is_initialized = True

    def to_code_prompt(self) -> str:
        args_signature = ", ".join(f"{arg_name}: {arg_schema['type']}" for arg_name, arg_schema in self.inputs.items())

        # Use dict type for tools with output schema to indicate structured return
        has_schema = hasattr(self, "output_schema") and self.output_schema is not None
        output_type = "dict" if has_schema else self.output_type
        tool_signature = f"({args_signature}) -> {output_type}"
        tool_doc = self.description

        # Add an important note for smaller models (e.g. Mistral Small, Gemma 3, etc.) to properly handle structured output.
        if has_schema:
            tool_doc += "\n\nImportant: This tool returns structured output! Use the JSON schema below to directly access fields like result['field_name']. NO print() statements needed to inspect the output!"

        # Add arguments documentation
        if self.inputs:
            args_descriptions = "\n".join(
                f"{arg_name}: {arg_schema['description']}" for arg_name, arg_schema in self.inputs.items()
            )
            args_doc = f"Args:\n{textwrap.indent(args_descriptions, '    ')}"
            tool_doc += f"\n\n{args_doc}"

        # Add returns documentation with output schema if it exists
        if has_schema:
            formatted_schema = json.dumps(self.output_schema, indent=4)
            indented_schema = textwrap.indent(formatted_schema, "        ")
            returns_doc = f"\nReturns:\n    dict (structured output): This tool ALWAYS returns a dictionary that strictly adheres to the following JSON schema:\n{indented_schema}"
            tool_doc += f"\n{returns_doc}"

        tool_doc = f'"""{tool_doc}\n"""'
        return f"def {self.name}{tool_signature}:\n{textwrap.indent(tool_doc, '    ')}"

    def to_tool_calling_prompt(self) -> str:
        return f"{self.name}: {self.description}\n    Takes inputs: {self.inputs}\n    Returns an output of type: {self.output_type}"

    def to_dict(self) -> dict:
        """Returns a dictionary representing the tool"""
        class_name = self.__class__.__name__
        if type(self).__name__ == "SimpleTool":
            # Check that imports are self-contained
            source_code = get_source(self.forward).replace("@tool", "")
            forward_node = ast.parse(source_code)
            # If tool was created using '@tool' decorator, it has only a forward pass, so it's simpler to just get its code
            method_checker = MethodChecker(set())
            method_checker.visit(forward_node)

            if len(method_checker.errors) > 0:
                errors = [f"- {error}" for error in method_checker.errors]
                raise (ValueError(f"SimpleTool validation failed for {self.name}:\n" + "\n".join(errors)))

            forward_source_code = get_source(self.forward)
            tool_code = textwrap.dedent(
                f"""
            from smolagents import Tool
            from typing import Any, Optional

            class {class_name}(Tool):
                name = "{self.name}"
                description = {json.dumps(textwrap.dedent(self.description).strip())}
                inputs = {repr(self.inputs)}
                output_type = "{self.output_type}"
            """
            ).strip()

            # Add output_schema if it exists
            if hasattr(self, "output_schema") and self.output_schema is not None:
                tool_code += f"\n                output_schema = {repr(self.output_schema)}"
            import re

            def add_self_argument(source_code: str) -> str:
                """Add 'self' as first argument to a function definition if not present."""
                pattern = r"def forward\(((?!self)[^)]*)\)"

                def replacement(match):
                    args = match.group(1).strip()
                    if args:  # If there are other arguments
                        return f"def forward(self, {args})"
                    return "def forward(self)"

                return re.sub(pattern, replacement, source_code)

            forward_source_code = forward_source_code.replace(self.name, "forward")
            forward_source_code = add_self_argument(forward_source_code)
            forward_source_code = forward_source_code.replace("@tool", "").strip()
            tool_code += "\n\n" + textwrap.indent(forward_source_code, "    ")

        else:  # If the tool was not created by the @tool decorator, it was made by subclassing Tool
            if type(self).__name__ in [
                "SpaceToolWrapper",
                "LangChainToolWrapper",
                "GradioToolWrapper",
            ]:
                raise ValueError(
                    "Cannot save objects created with from_space, from_langchain or from_gradio, as this would create errors."
                )

            validate_tool_attributes(self.__class__)

            tool_code = "from typing import Any, Optional\n" + instance_to_source(self, base_cls=Tool)

        requirements = {el for el in get_imports(tool_code) if el not in sys.stdlib_module_names} | {"smolagents"}

        tool_dict = {"name": self.name, "code": tool_code, "requirements": sorted(requirements)}

        # Add output_schema if it exists
        if hasattr(self, "output_schema") and self.output_schema is not None:
            tool_dict["output_schema"] = self.output_schema

        return tool_dict

    @classmethod
    def from_dict(cls, tool_dict: dict[str, Any], **kwargs) -> "Tool":
        """
        Create tool from a dictionary representation.

        Args:
            tool_dict (`dict[str, Any]`): Dictionary representation of the tool.
            **kwargs: Additional keyword arguments to pass to the tool's constructor.

        Returns:
            `Tool`: Tool object.
        """
        if "code" not in tool_dict:
            raise ValueError("Tool dictionary must contain 'code' key with the tool source code")

        tool = cls.from_code(tool_dict["code"], **kwargs)

        # Set output_schema if it exists in the dictionary
        if "output_schema" in tool_dict:
            tool.output_schema = tool_dict["output_schema"]

        return tool

    def save(self, output_dir: str | Path, tool_file_name: str = "tool", make_gradio_app: bool = True):
        """
        Saves the relevant code files for your tool so it can be pushed to the Hub. This will copy the code of your
        tool in `output_dir` as well as autogenerate:

        - a `{tool_file_name}.py` file containing the logic for your tool.
        If you pass `make_gradio_app=True`, this will also write:
        - an `app.py` file providing a UI for your tool when it is exported to a Space with `tool.push_to_hub()`
        - a `requirements.txt` containing the names of the modules used by your tool (as detected when inspecting its
          code)

        Args:
            output_dir (`str` or `Path`): The folder in which you want to save your tool.
            tool_file_name (`str`, *optional*): The file name in which you want to save your tool.
            make_gradio_app (`bool`, *optional*, defaults to True): Whether to also export a `requirements.txt` file and Gradio UI.
        """
        # Ensure output directory exists
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        # Save tool file
        self._write_file(output_path / f"{tool_file_name}.py", self._get_tool_code())
        if make_gradio_app:
            #  Save app file
            self._write_file(output_path / "app.py", self._get_gradio_app_code(tool_module_name=tool_file_name))
            # Save requirements file
            self._write_file(output_path / "requirements.txt", self._get_requirements())

    def _write_file(self, file_path: Path, content: str) -> None:
        """Writes content to a file with UTF-8 encoding."""
        file_path.write_text(content, encoding="utf-8")

    def push_to_hub(
        self,
        repo_id: str,
        commit_message: str = "Upload tool",
        private: bool | None = None,
        token: bool | str | None = None,
        create_pr: bool = False,
    ) -> str:
        """
        Upload the tool to the Hub.

        Parameters:
            repo_id (`str`):
                The name of the repository you want to push your tool to. It should contain your organization name when
                pushing to a given organization.
            commit_message (`str`, *optional*, defaults to `"Upload tool"`):
                Message to commit while pushing.
            private (`bool`, *optional*):
                Whether to make the repo private. If `None` (default), the repo will be public unless the organization's default is private. This value is ignored if the repo already exists.
            token (`bool` or `str`, *optional*):
                The token to use as HTTP bearer authorization for remote files. If unset, will use the token generated
                when running `huggingface-cli login` (stored in `~/.huggingface`).
            create_pr (`bool`, *optional*, defaults to `False`):
                Whether to create a PR with the uploaded files or directly commit.
        """
        # Initialize repository
        repo_id = self._initialize_hub_repo(repo_id, token, private)
        # Prepare files for commit
        additions = self._prepare_hub_files()
        # Create commit
        return create_commit(
            repo_id=repo_id,
            operations=additions,
            commit_message=commit_message,
            token=token,
            create_pr=create_pr,
            repo_type="space",
        )

    @staticmethod
    def _initialize_hub_repo(repo_id: str, token: bool | str | None, private: bool | None) -> str:
        """Initialize repository on Hugging Face Hub."""
        repo_url = create_repo(
            repo_id=repo_id,
            token=token,
            private=private,
            exist_ok=True,
            repo_type="space",
            space_sdk="gradio",
        )
        metadata_update(repo_url.repo_id, {"tags": ["smolagents", "tool"]}, repo_type="space", token=token)
        return repo_url.repo_id

    def _prepare_hub_files(self) -> list:
        """Prepare files for Hub commit."""
        additions = [
            # Add tool code
            CommitOperationAdd(
                path_in_repo="tool.py",
                path_or_fileobj=self._get_tool_code().encode(),
            ),
            # Add Gradio app
            CommitOperationAdd(
                path_in_repo="app.py",
                path_or_fileobj=self._get_gradio_app_code().encode(),
            ),
            # Add requirements
            CommitOperationAdd(
                path_in_repo="requirements.txt",
                path_or_fileobj=self._get_requirements().encode(),
            ),
        ]
        return additions

    def _get_tool_code(self) -> str:
        """Get the tool's code."""
        return self.to_dict()["code"]

    def _get_gradio_app_code(self, tool_module_name: str = "tool") -> str:
        """Get the Gradio app code."""
        class_name = self.__class__.__name__
        return textwrap.dedent(
            f"""\
            from smolagents import launch_gradio_demo
            from {tool_module_name} import {class_name}

            tool = {class_name}()
            launch_gradio_demo(tool)
            """
        )

    def _get_requirements(self) -> str:
        """Get the requirements."""
        return "\n".join(self.to_dict()["requirements"])

    @classmethod
    def from_hub(
        cls,
        repo_id: str,
        token: str | None = None,
        trust_remote_code: bool = False,
        **kwargs,
    ):
        """
        Loads a tool defined on the Hub.

        <Tip warning={true}>

        Loading a tool from the Hub means that you'll download the tool and execute it locally.
        ALWAYS inspect the tool you're downloading before loading it within your runtime, as you would do when
        installing a package using pip/npm/apt.

        </Tip>

        Args:
            repo_id (`str`):
                The name of the Space repo on the Hub where your tool is defined.
            token (`str`, *optional*):
                The token to identify you on hf.co. If unset, will use the token generated when running
                `huggingface-cli login` (stored in `~/.huggingface`).
            trust_remote_code(`str`, *optional*, defaults to False):
                This flags marks that you understand the risk of running remote code and that you trust this tool.
                If not setting this to True, loading the tool from Hub will fail.
            kwargs (additional keyword arguments, *optional*):
                Additional keyword arguments that will be split in two: all arguments relevant to the Hub (such as
                `cache_dir`, `revision`, `subfolder`) will be used when downloading the files for your tool, and the
                others will be passed along to its init.
        """
        if not trust_remote_code:
            raise ValueError(
                "Loading a tool from Hub requires to acknowledge you trust its code: to do so, pass `trust_remote_code=True`."
            )

        # Get the tool's tool.py file.
        tool_file = hf_hub_download(
            repo_id,
            "tool.py",
            token=token,
            repo_type="space",
            cache_dir=kwargs.get("cache_dir"),
            force_download=kwargs.get("force_download"),
            proxies=kwargs.get("proxies"),
            revision=kwargs.get("revision"),
            subfolder=kwargs.get("subfolder"),
            local_files_only=kwargs.get("local_files_only"),
        )

        tool_code = Path(tool_file).read_text()
        return Tool.from_code(tool_code, **kwargs)

    @classmethod
    def from_code(cls, tool_code: str, **kwargs):
        module = types.ModuleType("dynamic_tool")

        exec(tool_code, module.__dict__)

        # Find the Tool subclass
        tool_class = next(
            (
                obj
                for _, obj in inspect.getmembers(module, inspect.isclass)
                if issubclass(obj, Tool) and obj is not Tool
            ),
            None,
        )

        if tool_class is None:
            raise ValueError("No Tool subclass found in the code.")

        if not isinstance(tool_class.inputs, dict):
            tool_class.inputs = ast.literal_eval(tool_class.inputs)

        # Handle output_schema if it exists and is a string representation
        if hasattr(tool_class, "output_schema") and isinstance(tool_class.output_schema, str):
            tool_class.output_schema = ast.literal_eval(tool_class.output_schema)

        return tool_class(**kwargs)

    @staticmethod
    def from_space(
        space_id: str,
        name: str,
        description: str,
        api_name: str | None = None,
        token: str | None = None,
    ):
        """
        Creates a [`Tool`] from a Space given its id on the Hub.

        Args:
            space_id (`str`):
                The id of the Space on the Hub.
            name (`str`):
                The name of the tool.
            description (`str`):
                The description of the tool.
            api_name (`str`, *optional*):
                The specific api_name to use, if the space has several tabs. If not precised, will default to the first available api.
            token (`str`, *optional*):
                Add your token to access private spaces or increase your GPU quotas.
        Returns:
            [`Tool`]:
                The Space, as a tool.

        Examples:
        ```py
        >>> image_generator = Tool.from_space(
        ...     space_id="black-forest-labs/FLUX.1-schnell",
        ...     name="image-generator",
        ...     description="Generate an image from a prompt"
        ... )
        >>> image = image_generator("Generate an image of a cool surfer in Tahiti")
        ```
        ```py
        >>> face_swapper = Tool.from_space(
        ...     "tuan2308/face-swap",
        ...     "face_swapper",
        ...     "Tool that puts the face shown on the first image on the second image. You can give it paths to images.",
        ... )
        >>> image = face_swapper('./aymeric.jpeg', './ruth.jpg')
        ```
        """
        from gradio_client import Client, handle_file

        class SpaceToolWrapper(Tool):
            skip_forward_signature_validation = True

            def __init__(
                self,
                space_id: str,
                name: str,
                description: str,
                api_name: str | None = None,
                token: str | None = None,
            ):
                self.name = name
                self.description = description
                self.client = Client(space_id, hf_token=token)
                space_api = self.client.view_api(return_format="dict", print_info=False)
                assert isinstance(space_api, dict)
                space_description = space_api["named_endpoints"]

                # If api_name is not defined, take the first of the available APIs for this space
                if api_name is None:
                    api_name = list(space_description.keys())[0]
                    warnings.warn(
                        f"Since `api_name` was not defined, it was automatically set to the first available API: `{api_name}`."
                    )
                self.api_name = api_name

                try:
                    space_description_api = space_description[api_name]
                except KeyError:
                    raise KeyError(f"Could not find specified {api_name=} among available api names.")
                self.inputs = {}
                for parameter in space_description_api["parameters"]:
                    parameter_type = parameter["type"]["type"]
                    if parameter_type == "object":
                        parameter_type = "any"
                    self.inputs[parameter["parameter_name"]] = {
                        "type": parameter_type,
                        "description": parameter["python_type"]["description"],
                        "nullable": parameter["parameter_has_default"],
                    }
                output_component = space_description_api["returns"][0]["component"]
                if output_component == "Image":
                    self.output_type = "image"
                elif output_component == "Audio":
                    self.output_type = "audio"
                else:
                    self.output_type = "any"
                self.is_initialized = True

            def sanitize_argument_for_prediction(self, arg):
                from gradio_client.utils import is_http_url_like
                from PIL.Image import Image

                if isinstance(arg, Image):
                    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                    arg.save(temp_file.name)
                    arg = temp_file.name
                if (
                    (isinstance(arg, str) and os.path.isfile(arg))
                    or (isinstance(arg, Path) and arg.exists() and arg.is_file())
                    or is_http_url_like(arg)
                ):
                    arg = handle_file(arg)
                return arg

            def forward(self, *args, **kwargs):
                # Preprocess args and kwargs:
                args = list(args)
                for i, arg in enumerate(args):
                    args[i] = self.sanitize_argument_for_prediction(arg)
                for arg_name, arg in kwargs.items():
                    kwargs[arg_name] = self.sanitize_argument_for_prediction(arg)

                output = self.client.predict(*args, api_name=self.api_name, **kwargs)
                if isinstance(output, tuple) or isinstance(output, list):
                    if isinstance(output[1], str):
                        raise ValueError("The space returned this message: " + output[1])
                    output = output[
                        0
                    ]  # Sometime the space also returns the generation seed, in which case the result is at index 0
                IMAGE_EXTENTIONS = [".png", ".jpg", ".jpeg", ".gif", ".webp"]
                AUDIO_EXTENTIONS = [".mp3", ".wav", ".ogg", ".m4a", ".flac"]
                if isinstance(output, str) and any([output.endswith(ext) for ext in IMAGE_EXTENTIONS]):
                    output = AgentImage(output)
                elif isinstance(output, str) and any([output.endswith(ext) for ext in AUDIO_EXTENTIONS]):
                    output = AgentAudio(output)
                return output

        return SpaceToolWrapper(
            space_id=space_id,
            name=name,
            description=description,
            api_name=api_name,
            token=token,
        )

    @staticmethod
    def from_gradio(gradio_tool):
        """
        Creates a [`Tool`] from a gradio tool.
        """
        import inspect

        class GradioToolWrapper(Tool):
            def __init__(self, _gradio_tool):
                self.name = _gradio_tool.name
                self.description = _gradio_tool.description
                self.output_type = "string"
                self._gradio_tool = _gradio_tool
                func_args = list(inspect.signature(_gradio_tool.run).parameters.items())
                self.inputs = {
                    key: {"type": CONVERSION_DICT[value.annotation], "description": ""} for key, value in func_args
                }
                self.forward = self._gradio_tool.run

        return GradioToolWrapper(gradio_tool)

    @staticmethod
    def from_langchain(langchain_tool):
        """
        Creates a [`Tool`] from a langchain tool.
        """

        class LangChainToolWrapper(Tool):
            skip_forward_signature_validation = True

            def __init__(self, _langchain_tool):
                self.name = _langchain_tool.name.lower()
                self.description = _langchain_tool.description
                self.inputs = _langchain_tool.args.copy()
                for input_content in self.inputs.values():
                    if "title" in input_content:
                        input_content.pop("title")
                    input_content["description"] = ""
                self.output_type = "string"
                self.langchain_tool = _langchain_tool
                self.is_initialized = True

            def forward(self, *args, **kwargs):
                tool_input = kwargs.copy()
                for index, argument in enumerate(args):
                    if index < len(self.inputs):
                        input_key = next(iter(self.inputs))
                        tool_input[input_key] = argument
                return self.langchain_tool.run(tool_input)

        return LangChainToolWrapper(langchain_tool)
