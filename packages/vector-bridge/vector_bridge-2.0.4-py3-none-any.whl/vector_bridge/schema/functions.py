import ast
import builtins
import importlib.util
import inspect
import json
import os
import site
import sys
from datetime import datetime
from enum import Enum
from typing import (Any, Dict, List, Literal, Optional, TypeVar, Union,
                    get_args, get_origin, get_type_hints)

from pydantic import BaseModel, Field
from stdlib_list import stdlib_list

from vector_bridge import VectorBridgeClient
from vector_bridge.schema.helpers.enums import GPTActions

T = TypeVar("T")


class FunctionsSorting(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"


class FunctionPropertyStorageStructure(BaseModel):
    name: str
    description: str
    type: str = Field(default="string")
    items: Dict[str, Any] = Field(default_factory=dict)
    enum: List[str] = []
    required: bool = Field(default=False)


class FunctionParametersStorageStructure(BaseModel):
    properties: List[FunctionPropertyStorageStructure]


class Overrides(BaseModel):
    model: Optional[str] = Field(default=None)
    system_prompt: Optional[str] = Field(default=None)
    message_prompt: Optional[str] = Field(default=None)
    knowledge_prompt: Optional[str] = Field(default=None)
    max_tokens: Optional[int] = Field(default=None)
    frequency_penalty: Optional[float] = Field(default=None)
    presence_penalty: Optional[float] = Field(default=None)
    temperature: Optional[float] = Field(default=None)


class FunctionUpdate(BaseModel):
    description: str
    accessible_by_ai: bool = Field(default=True)
    function_parameters: FunctionParametersStorageStructure
    overrides: Overrides = Field(default=Overrides())


class SemanticSearchFunctionUpdate(FunctionUpdate):
    function_action: GPTActions = GPTActions.SEARCH
    vector_schema: str


class SimilarSearchFunctionUpdate(FunctionUpdate):
    function_action: GPTActions = GPTActions.SIMILAR
    vector_schema: str


class SummaryFunctionUpdate(FunctionUpdate):
    function_action: GPTActions = GPTActions.SUMMARY


class JsonFunctionUpdate(FunctionUpdate):
    function_action: GPTActions = GPTActions.JSON


class CodeExecuteFunctionUpdate(FunctionUpdate):
    function_action: GPTActions = GPTActions.CODE_EXEC
    code: str


class Function(BaseModel):
    function_id: str
    function_name: str
    integration_id: str
    description: str
    accessible_by_ai: bool = Field(default=True)
    function_parameters: FunctionParametersStorageStructure
    overrides: Overrides = Field(default=Overrides())
    system_required: bool = Field(default=False)
    created_at: datetime = Field(default=None)
    created_by: str = Field(default="")
    updated_at: datetime = Field(default=None)
    updated_by: str = Field(default="")

    @property
    def uuid(self):
        return self.function_id

    @classmethod
    def to_valid_subclass(
        cls, data: dict
    ) -> Union[
        None,
        "OtherFunction",
        "CodeExecuteFunction",
        "SummaryFunction",
        "SemanticSearchFunction",
        "SimilarSearchFunction",
        "JsonFunction",
        "ForwardToAgentFunction",
    ]:
        function_action = data["function_action"]
        if function_action == GPTActions.SEARCH:
            return SemanticSearchFunction.model_validate(data)
        elif function_action == GPTActions.SIMILAR:
            return SimilarSearchFunction.model_validate(data)
        elif function_action == GPTActions.SUMMARY:
            return SummaryFunction.model_validate(data)
        elif function_action == GPTActions.JSON:
            return JsonFunction.model_validate(data)
        elif function_action == GPTActions.CODE_EXEC:
            return CodeExecuteFunction.model_validate(data)
        elif function_action == GPTActions.FORWARD_TO_AGENT:
            return ForwardToAgentFunction.model_validate(data)
        elif function_action == GPTActions.OTHER:
            return OtherFunction.model_validate(data)

    def update_function(
        self,
        client: VectorBridgeClient,
        function_data: Union[
            SemanticSearchFunctionUpdate,
            SimilarSearchFunctionUpdate,
            SummaryFunctionUpdate,
            JsonFunctionUpdate,
            CodeExecuteFunctionUpdate,
        ],
    ) -> "Function":
        return client.admin.functions.update_function(
            function_id=self.function_id,
            function_data=function_data,
        )

    def delete_function(self, client: VectorBridgeClient) -> None:
        return client.admin.functions.delete_function(
            function_id=self.function_id,
        )

    async def a_update_function(
        self,
        client: VectorBridgeClient,
        function_data: Union[
            SemanticSearchFunctionUpdate,
            SimilarSearchFunctionUpdate,
            SummaryFunctionUpdate,
            JsonFunctionUpdate,
            CodeExecuteFunctionUpdate,
        ],
    ) -> "Function":
        return await client.admin.functions.update_function(
            function_id=self.function_id,
            function_data=function_data,
        )

    async def a_delete_function(self, client: VectorBridgeClient) -> None:
        return await client.admin.functions.delete_function(
            function_id=self.function_id,
        )


class SemanticSearchFunction(Function):
    function_action: GPTActions = GPTActions.SEARCH
    vector_schema: str


class SimilarSearchFunction(Function):
    function_action: GPTActions = GPTActions.SIMILAR
    vector_schema: str


class SummaryFunction(Function):
    function_action: GPTActions = GPTActions.SUMMARY


class JsonFunction(Function):
    function_action: GPTActions = GPTActions.JSON


class CodeExecuteFunction(Function):
    function_action: GPTActions = GPTActions.CODE_EXEC
    code: str


class ForwardToAgentFunction(Function):
    function_action: GPTActions = GPTActions.FORWARD_TO_AGENT


class OtherFunction(Function):
    function_action: GPTActions = GPTActions.OTHER


class FunctionCreate(BaseModel):
    function_name: str
    description: str
    accessible_by_ai: bool = Field(default=True)
    function_parameters: FunctionParametersStorageStructure
    overrides: Overrides = Field(default=Overrides())


class SemanticSearchFunctionCreate(FunctionCreate):
    function_action: GPTActions = GPTActions.SEARCH
    vector_schema: str


class SimilarSearchFunctionCreate(FunctionCreate):
    function_action: GPTActions = GPTActions.SIMILAR
    vector_schema: str


class SummaryFunctionCreate(FunctionCreate):
    function_action: GPTActions = GPTActions.SUMMARY


class JsonFunctionCreate(FunctionCreate):
    function_action: GPTActions = GPTActions.JSON


class CodeExecuteFunctionCreate(FunctionCreate):
    function_action: GPTActions = GPTActions.CODE_EXEC
    code: str


class PaginatedFunctions(BaseModel):
    functions: List[
        Union[
            SemanticSearchFunction,
            SimilarSearchFunction,
            SummaryFunction,
            JsonFunction,
            CodeExecuteFunction,
            ForwardToAgentFunction,
            OtherFunction,
        ]
    ] = Field(default_factory=list)
    limit: int
    last_evaluated_key: Optional[str] = None
    has_more: bool = False

    @classmethod
    def resolve_functions(cls, data: dict) -> "PaginatedFunctions":
        functions = [Function.to_valid_subclass(func) for func in data["functions"]]
        data["functions"] = functions
        return PaginatedFunctions(**data)


class FunctionExtractor:
    def __init__(self, func):
        self.func = func
        self.module = inspect.getmodule(func)
        self.module_source = inspect.getsource(self.module)
        self.tree = ast.parse(self.module_source)
        self.func_name = func.__name__
        self.collected_funcs = {}
        self.collected_classes = {}
        self.collected_imports = set()
        self.collected_globals = {}
        self.builtin_names = set(dir(builtins))
        self.visited = set()

        # Get function signature and docstring
        self.signature = inspect.signature(func)
        self.docstring = inspect.getdoc(func) or ""

        # Parameter metadata will be stored here
        self.param_metadata = {}

        # Check if all parameters have type annotations
        for param_name, param in self.signature.parameters.items():
            if param.annotation is inspect.Parameter.empty:
                raise TypeError(f"Parameter '{param_name}' in function '{func.__name__}' must have a type annotation")

        # Parse docstring to extract parameter descriptions
        self._parse_docstring()

    def _parse_docstring(self):
        """Parse the function docstring to extract parameter descriptions."""
        if not self.docstring:
            raise ValueError(f"Function '{self.func_name}' must have a docstring with parameter descriptions")

        # First, get the function description (everything before the first empty line or section marker)
        description_lines = []
        param_descriptions = {}
        lines = self.docstring.split("\n")

        # Process the docstring line by line
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check if this is the end of the description section
            if not line or line == "Args:" or line.startswith(":param "):
                break

            description_lines.append(line)
            i += 1

        self.func_description = " ".join(description_lines).strip()

        # --- Google-style docstring parsing ---
        # Find the Args section
        args_section_idx = -1
        for j, line in enumerate(lines):
            if line.strip() == "Args:":
                args_section_idx = j
                break

        if args_section_idx >= 0:
            # Process the Args section
            i = args_section_idx + 1
            current_param = None
            current_desc = ""

            while i < len(lines):
                line = lines[i]

                # Check if we've reached the end of the Args section
                if not line.strip() or line.strip().startswith(("Returns:", "Raises:")):
                    if current_param:
                        param_descriptions[current_param] = current_desc.strip()
                    break

                # Check if this is a new parameter definition
                if line.strip() and line.lstrip() != line:  # It's indented
                    # If it's a parameter line (contains : and has a word before it)
                    if ":" in line.strip():
                        # If we were processing a parameter, save it
                        if current_param:
                            param_descriptions[current_param] = current_desc.strip()

                        # Start processing new parameter
                        parts = line.strip().split(":", 1)
                        current_param = parts[0].strip()
                        current_desc = parts[1].strip()
                    else:
                        # It's a continuation of the current description
                        if current_param:
                            current_desc += " " + line.strip()

                i += 1

            # Save the last parameter if we have one
            if current_param and current_param not in param_descriptions:
                param_descriptions[current_param] = current_desc.strip()

        # --- reStructuredText style docstring parsing ---
        # Look for :param name: descriptions
        for i, line in enumerate(lines):
            line = line.strip()
            # Match :param parameter_name: description
            if line.startswith(":param "):
                parts = line[7:].split(":", 1)  # Split after ":param "
                if len(parts) == 2:
                    param_name = parts[0].strip()
                    description = parts[1].strip()

                    # Check for multi-line descriptions
                    j = i + 1
                    while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith(":"):
                        description += " " + lines[j].strip()
                        j += 1

                    param_descriptions[param_name] = description

        # Ensure every parameter has a description
        for param_name in self.signature.parameters:
            if param_name not in param_descriptions:
                raise ValueError(
                    f"Parameter '{param_name}' in function '{self.func_name}' must have a description in the docstring"
                )

            self.param_metadata[param_name] = {"description": param_descriptions[param_name]}

    def extract(self, include_main=True):
        # Step 1: Collect top-level imports
        self._collect_imports()

        # Always include necessary imports for environment variables and type handling
        if include_main:
            # Add the import for parse functions
            self.collected_imports.add("from vector_bridge.schema.functions import parse_env_var")

        # Step 2: Collect the main function and its dependencies
        self._collect_function(self.func_name)

        # Step 3: Compose full code
        self._sort_imports()
        imports_code = "\n".join(self.collected_imports)

        globals_code = "\n".join(self.collected_globals.values())
        classes_code = "\n\n".join(self.collected_classes.values())
        functions_code = "\n\n".join(self.collected_funcs.values())

        parts = []
        if imports_code:
            parts.append(imports_code + "\n")
        if globals_code:
            parts.append(globals_code + "\n")
        if classes_code:
            parts.append(classes_code + "\n")
        if functions_code:
            parts.append(functions_code + "\n")

        full_code = "\n\n".join(parts)

        # Add main entry point if requested
        if include_main:
            main_block = self._generate_main_entry_point()
            full_code = f"{full_code}\n{main_block}"

        return full_code

    def _collect_imports(self):
        """Collect all imports from the module."""
        for node in ast.iter_child_nodes(self.tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                lines = self.module_source.splitlines()
                import_line = lines[node.lineno - 1 : node.end_lineno]
                self.collected_imports.add("\n".join(import_line))

    def _get_node_source(self, node):
        """Extract the source code for a node."""
        lines = self.module_source.splitlines()
        return "\n".join(lines[node.lineno - 1 : node.end_lineno])

    def _collect_function(self, func_name):
        """Collect a function and its dependencies."""
        if func_name in self.visited or func_name in self.builtin_names:
            return

        self.visited.add(func_name)

        # Find the function definition in the AST
        for node in self.tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                # Get function source code
                func_source = self._get_node_source(node)
                self.collected_funcs[func_name] = func_source

                # Collect dependencies
                self._find_dependencies_in_node(node)
                return

    def _collect_class(self, class_name):
        """Collect a class and its dependencies."""
        if class_name in self.visited or class_name in self.builtin_names:
            return

        self.visited.add(class_name)

        # Find the class definition in the AST
        for node in self.tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                # Get class source code
                class_source = self._get_node_source(node)
                self.collected_classes[class_name] = class_source

                # Collect base class dependencies
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        self._collect_dependency(base.id)

                # Collect dependencies from the class body
                self._find_dependencies_in_node(node)
                return

    def _collect_global(self, var_name):
        """Collect a global variable definition, with special handling for VectorBridgeClient."""
        if var_name in self.visited or var_name in self.builtin_names:
            return

        self.visited.add(var_name)

        for node in self.tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == var_name:
                        # Check if the assignment is to VectorBridgeClient(...)
                        if (
                            isinstance(node.value, ast.Call)
                            and isinstance(node.value.func, ast.Name)
                            and node.value.func.id == "VectorBridgeClient"
                        ):
                            # Extract base_url if it's in the call
                            base_url_arg = None
                            for kw in node.value.keywords:
                                if kw.arg == "base_url":
                                    if isinstance(kw.value, ast.Constant):  # e.g., a string
                                        base_url_arg = repr(kw.value.value)
                                    elif isinstance(kw.value, ast.Name):
                                        base_url_arg = kw.value.id
                                    else:
                                        base_url_arg = ast.unparse(kw.value)  # fallback for complex values

                            # Build the updated code with base_url if available
                            client_init = f"{target.id} = VectorBridgeClient("
                            args_list = []

                            if base_url_arg:
                                args_list.append(f"base_url={base_url_arg}")

                            args_list.append('integration_name=os.getenv("integration_name")')
                            client_init += ", ".join(args_list)
                            client_init += ")"

                            # Add access_token line
                            access_token_line = f'{target.id}.access_token = os.getenv("token")'

                            # Combine and store
                            updated_code = f"{client_init}\n{access_token_line}"
                            self.collected_globals[var_name] = updated_code
                        else:
                            # Default behavior
                            global_source = self._get_node_source(node)
                            self.collected_globals[var_name] = global_source

                        # Also collect any dependencies in the value expression
                        self._find_dependencies_in_node(node.value)
                        return

    def _find_dependencies_in_node(self, node):
        """Find all dependencies in an AST node."""
        for child in ast.walk(node):
            # Function calls
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    # Direct function call: function_name()
                    self._collect_dependency(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    # Method call: object.method()
                    if isinstance(child.func.value, ast.Name):
                        self._collect_dependency(child.func.value.id)

            # Variable references
            elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                # Skip function arguments and common local variables
                if self._is_global_reference(node, child.id):
                    self._collect_dependency(child.id)

    def _is_global_reference(self, func_node, name):
        """Check if a name is likely a global reference."""
        # Skip builtins
        if name in self.builtin_names:
            return False

        # Skip common local variable names
        if name in ("self", "cls", "args", "kwargs"):
            return False

        # Find the closest function definition
        current_func = None
        for node in ast.walk(func_node):
            if isinstance(node, ast.FunctionDef):
                current_func = node
                break

        if current_func:
            # Skip function arguments
            arg_names = [arg.arg for arg in current_func.args.args]
            if name in arg_names:
                return False

        return True

    def _collect_dependency(self, name):
        """Determine the type of dependency and collect it."""
        # Check if it's a function
        for node in self.tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == name:
                self._collect_function(name)
                return

        # Check if it's a class
        for node in self.tree.body:
            if isinstance(node, ast.ClassDef) and node.name == name:
                self._collect_class(name)
                return

        # Check if it's a global variable
        for node in self.tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == name:
                        self._collect_global(name)
                        return

    def _sort_imports(self):
        """Sort collected imports like isort, dynamically categorizing them."""

        std_lib_imports = []
        third_party_imports = []
        local_imports = []

        # Get standard library module names for the current Python version
        std_libs = set(stdlib_list(f"{sys.version_info.major}.{sys.version_info.minor}"))

        # Get third-party site-packages paths
        site_packages_dirs = site.getsitepackages()

        for import_stmt in self.collected_imports:
            # Skip 'from x import *' style
            if "*" in import_stmt:
                continue

            try:
                module_name = import_stmt.split()[1].split(".")[0].rstrip(",")
            except IndexError:
                continue

            if module_name in std_libs:
                std_lib_imports.append(import_stmt)
            else:
                # Try to locate module spec to determine if it's third-party
                spec = importlib.util.find_spec(module_name)
                if spec and spec.origin:
                    if any(spec.origin.startswith(path) for path in site_packages_dirs):
                        third_party_imports.append(import_stmt)
                    else:
                        local_imports.append(import_stmt)
                else:
                    local_imports.append(import_stmt)

        # Sort each group
        std_lib_imports.sort()
        third_party_imports.sort()
        local_imports.sort()

        # Replace the collected imports with sorted ones
        sorted_imports = []
        if std_lib_imports:
            sorted_imports.extend(std_lib_imports)
            sorted_imports.append("")
        if third_party_imports:
            sorted_imports.extend(third_party_imports)
            sorted_imports.append("")
        if local_imports:
            sorted_imports.extend(local_imports)

        # Clean up any trailing blank line
        if sorted_imports and sorted_imports[-1] == "":
            sorted_imports.pop()

        self.collected_imports = sorted_imports

    def _python_type_to_property_type(self, py_type):
        """
        Convert Python type annotation to OpenAI function property type format.

        Args:
            py_type: Python type annotation

        Returns:
            Tuple of (type_string, items_dict, enum_list)
        """
        # Check for None/NoneType
        if py_type is type(None):
            return "null", {}, []

        # Handle primitive types
        if py_type is str:
            return "string", {}, []
        elif py_type is int:
            return "integer", {}, []
        elif py_type is float:
            return "number", {}, []
        elif py_type is bool:
            return "boolean", {}, []

        # Handle lists and arrays
        elif py_type is list or get_origin(py_type) is list:
            # Default to array of strings if no item type is specified
            if not hasattr(py_type, "__args__") or not py_type.__args__:
                return "array", {"type": "string"}, []

            # Get the item type from the list's type parameter
            item_type = get_args(py_type)[0] if get_args(py_type) else Any

            # Special handling for Pydantic models and similar classes
            if isinstance(item_type, type) and hasattr(item_type, "__annotations__"):
                # Extract properties from the model
                properties = {}

                # Try to get field descriptions from Pydantic model
                field_descriptions = self._extract_pydantic_field_descriptions(item_type)

                for field_name, field_type in item_type.__annotations__.items():
                    field_type_str, field_items, field_enum = self._python_type_to_property_type(field_type)

                    # Create property with type info
                    prop = {"type": field_type_str}

                    # Add description if available
                    if field_name in field_descriptions:
                        prop["description"] = field_descriptions[field_name]

                    # Add additional schema information
                    if field_items:
                        prop["items"] = field_items
                    if field_enum:
                        prop["enum"] = field_enum

                    properties[field_name] = prop

                # Return array of objects with specific properties
                return "array", {"type": "object", "properties": properties}, []

            # Regular type handling for non-model types
            item_type_str, item_items, item_enum = self._python_type_to_property_type(item_type)
            items_dict = {"type": item_type_str}

            # If the items have their own items (nested array) or enum, include those
            if item_items:
                items_dict["items"] = item_items
            if item_enum:
                items_dict["enum"] = item_enum

            return "array", items_dict, []

        # Handle dictionaries
        elif py_type is dict or get_origin(py_type) is dict:
            # Check if we have key and value types specified
            if hasattr(py_type, "__args__") and len(py_type.__args__) == 2:
                key_type, value_type = py_type.__args__

                # OpenAI expects object keys to be strings
                if key_type is not str:
                    print(f"Warning: Dictionary keys should be strings, got {key_type}")

                # Get the value type
                value_type_str, value_items, value_enum = self._python_type_to_property_type(value_type)

                additional_properties = {"type": value_type_str}
                if value_items:
                    additional_properties["items"] = value_items
                if value_enum:
                    additional_properties["enum"] = value_enum

                # For dictionaries, we don't use the items field, but we could return
                # additionalProperties to provide more info about the schema
                return "object", {"additionalProperties": additional_properties}, []

            return "object", {}, []

        # Handle Union types (including Optional)
        elif get_origin(py_type) is Union:
            # Check if this is Optional[X] (Union[X, None])
            args = get_args(py_type)
            if type(None) in args and len(args) == 2:
                # Get the non-None type
                other_type = next(arg for arg in args if arg is not type(None))
                type_str, items_dict, enum_list = self._python_type_to_property_type(other_type)
                return type_str, items_dict, enum_list

            # For general unions, we can't represent them precisely in OpenAI's schema
            # So we'll use the first type as a fallback
            first_type = args[0]
            type_str, items_dict, enum_list = self._python_type_to_property_type(first_type)
            return type_str, items_dict, enum_list

        # Handle Literal types (enums)
        elif get_origin(py_type) is Literal:
            enum_values = []
            for arg in get_args(py_type):
                # Convert all literal values to strings
                enum_values.append(str(arg))
            return "string", {}, enum_values

        # Handle Enum classes
        elif isinstance(py_type, type) and issubclass(py_type, Enum):
            enum_values = [e.name for e in py_type]
            return "string", {}, enum_values

        # Handle Pydantic models and classes with annotations
        elif isinstance(py_type, type) and hasattr(py_type, "__annotations__"):
            properties = {}

            # Try to get field descriptions from Pydantic model
            field_descriptions = self._extract_pydantic_field_descriptions(py_type)

            for field_name, field_type in py_type.__annotations__.items():
                field_type_str, field_items, field_enum = self._python_type_to_property_type(field_type)

                # Create property with type info
                prop = {"type": field_type_str}

                # Add description if available
                if field_name in field_descriptions:
                    prop["description"] = field_descriptions[field_name]

                # Add additional schema information
                if field_items:
                    prop["items"] = field_items
                if field_enum:
                    prop["enum"] = field_enum

                properties[field_name] = prop

            return "object", {"properties": properties}, []

        # Default to string for other types
        else:
            type_name = getattr(py_type, "__name__", str(py_type))
            print(f"Warning: Unsupported type {type_name}, defaulting to string")
            return "string", {}, []

    def _extract_pydantic_field_descriptions(self, model_class):
        """
        Extract field descriptions from a Pydantic model.

        Handles both Pydantic v1 and v2 models.

        Args:
            model_class: The Pydantic model class

        Returns:
            Dict mapping field names to their descriptions
        """
        descriptions = {}

        # For Pydantic v1 models
        if hasattr(model_class, "__fields__"):
            for field_name, field in model_class.__fields__.items():
                # Try to get description from field_info
                if hasattr(field, "field_info") and hasattr(field.field_info, "description"):
                    if field.field_info.description:
                        descriptions[field_name] = field.field_info.description
                # Alternative way to get description
                elif hasattr(field, "description") and field.description:
                    descriptions[field_name] = field.description

        # For Pydantic v2 models
        elif hasattr(model_class, "model_fields"):
            for field_name, field in model_class.model_fields.items():
                if hasattr(field, "description") and field.description:
                    descriptions[field_name] = field.description

        # Try to get schema if model has schema() method
        elif hasattr(model_class, "schema") and callable(getattr(model_class, "schema")):
            try:
                schema = model_class.schema()
                if "properties" in schema:
                    for field_name, field_schema in schema["properties"].items():
                        if "description" in field_schema:
                            descriptions[field_name] = field_schema["description"]
            except Exception as e:
                print(f"Warning: Failed to get schema from model: {e}")

        # For Field objects directly in class variables
        for field_name, field_value in model_class.__dict__.items():
            if field_name in model_class.__annotations__:
                # Check if it's a Field with description
                if hasattr(field_value, "description") and field_value.description:
                    descriptions[field_name] = field_value.description
                # For Pydantic Field objects
                elif hasattr(field_value, "default_factory") and hasattr(field_value, "description"):
                    descriptions[field_name] = field_value.description

        return descriptions

    def get_function_metadata(self):
        """Generate function metadata according to the specified model structure."""
        # Get type hints for parameters
        type_hints = get_type_hints(self.func)

        # Prepare properties list
        properties = []

        # Process each parameter
        for param_name, param in self.signature.parameters.items():
            py_type = type_hints.get(param_name, Any)
            type_str, items, enum_values = self._python_type_to_property_type(py_type)

            # Determine if parameter is required
            required = param.default is inspect.Parameter.empty

            # Get description from parsed docstring
            description = self.param_metadata.get(param_name, {}).get("description", "")

            # Create property object
            prop = {
                "name": param_name,
                "description": description,
                "type": type_str,
                "required": required,
            }

            # Add items if present
            if items:
                prop["items"] = items

            # Add enum if present
            if enum_values:
                prop["enum"] = enum_values

            properties.append(prop)

        # Build the full structure
        metadata = {
            "function_name": self.func_name,
            "description": self.func_description,
            "accessible_by_ai": True,
            "function_parameters": {"properties": properties},
            "code": self.extract(include_main=True),
        }

        return metadata

    def _generate_main_entry_point(self):
        """Generate code for the main entry point with parameters from kwargs."""
        type_hints = get_type_hints(self.func)
        param_parsers = []

        for param_name, param in self.signature.parameters.items():
            py_type = type_hints.get(param_name, Any)
            is_required = param.default is inspect.Parameter.empty

            # Get default value representation
            default_repr = "None"
            if not is_required:
                if isinstance(param.default, str):
                    default_repr = f'"{param.default}"'
                elif isinstance(param.default, Enum):
                    default_repr = f'"{param.default.value}"'
                else:
                    default_repr = str(param.default)

            origin_type = get_origin(py_type)

            # Handle Optional[List[...]] types
            if origin_type is Union:
                args = get_args(py_type)
                if type(None) in args and len(args) == 2:
                    non_none_type = next(arg for arg in args if arg is not type(None))
                    if get_origin(non_none_type) is list:
                        # Handle list items
                        item_type = get_args(non_none_type)[0]
                        list_parser = [
                            f'{param_name}_data = kwargs.get("{param_name}", {default_repr})',
                            f"{param_name} = [] if {param_name}_data is None else [",
                        ]
                        if hasattr(item_type, "__annotations__"):
                            list_parser[-1] += f"{item_type.__name__}(**item) for item in {param_name}_data]"
                        else:
                            list_parser[-1] += f"item for item in {param_name}_data]"
                        param_parsers.extend(list_parser)
                        continue

            # List handling
            if py_type is list or origin_type is list:
                # Get list item type
                item_type = get_args(py_type)[0] if get_args(py_type) else Any
                if is_required:
                    param_parsers.append(f'if "{param_name}" not in kwargs:')
                    param_parsers.append(f'    raise ValueError("Missing required parameter: {param_name}")')
                    param_parsers.append(f'{param_name}_data = kwargs["{param_name}"]')
                else:
                    param_parsers.append(f'{param_name}_data = kwargs.get("{param_name}", {default_repr})')

                if hasattr(item_type, "__annotations__"):
                    param_parsers.append(f"{param_name} = [{item_type.__name__}(**item) for item in {param_name}_data]")
                else:
                    param_parsers.append(f"{param_name} = {param_name}_data")
                continue

            # Enum handling
            if isinstance(py_type, type) and issubclass(py_type, Enum):
                if is_required:
                    param_parsers.append(f'if "{param_name}" not in kwargs:')
                    param_parsers.append(f'    raise ValueError("Missing required parameter: {param_name}")')
                    param_parsers.append(f'{param_name}_val = kwargs["{param_name}"]')
                else:
                    param_parsers.append(f'{param_name}_val = kwargs.get("{param_name}", {default_repr})')
                param_parsers.append(f"{param_name} = {py_type.__name__}({param_name}_val)")
                continue

            # Union/Optional handling
            if origin_type is Union:
                args = get_args(py_type)
                if type(None) in args:
                    non_none_type = next(arg for arg in args if arg is not type(None))
                    type_name = getattr(non_none_type, "__name__", "Any")
                    if is_required:
                        param_parsers.append(f'if "{param_name}" not in kwargs:')
                        param_parsers.append(f'    raise ValueError("Missing required parameter: {param_name}")')
                        param_parsers.append(f'{param_name} = kwargs["{param_name}"]')
                    else:
                        param_parsers.append(f'{param_name} = kwargs.get("{param_name}", {default_repr})')
                    continue

            # Base case: simple type handling
            if is_required:
                param_parsers.append(f'if "{param_name}" not in kwargs:')
                param_parsers.append(f'    raise ValueError("Missing required parameter: {param_name}")')
                param_parsers.append(f'{param_name} = kwargs["{param_name}"]')
            else:
                param_parsers.append(f'{param_name} = kwargs.get("{param_name}", {default_repr})')

        param_parser_code = "\n    ".join(param_parsers)
        func_args = ", ".join(f"{name}={name}" for name in self.signature.parameters.keys())

        main_block = f"""
def run(**kwargs):
    # Parse parameters from kwargs
    {param_parser_code}

    # Call the main function
    result = {self.func_name}({func_args})
    return result
    """
        return main_block


def parse_env_var(var_name: str, var_type: str, default: Any = None, required: bool = False) -> Any:
    """
    Parse an environment variable with type conversion.

    Args:
        var_name: Name of the environment variable
        var_type: Type name for conversion ('str', 'int', 'float', 'bool', 'list', 'dict', etc.)
        default: Default value if environment variable is not set
        required: Whether the environment variable is required

    Returns:
        Parsed value or default if not set

    Raises:
        ValueError: If required variable is not set or conversion fails
    """
    value = os.getenv(var_name)

    if value is None:
        if required:
            raise ValueError(f"Required environment variable {var_name} is not set")
        return default

    try:
        if var_type == "str":
            return value
        elif var_type == "int":
            return int(value)
        elif var_type == "float":
            return float(value)
        elif var_type == "bool":
            return value.lower() in ("true", "yes", "1", "t", "y")
        elif var_type == "list" or var_type == "dict":
            return json.loads(value)
        else:
            # For other types, try the complex parser
            return parse_complex_type(value, var_type)
    except Exception as e:
        raise ValueError(f"Failed to convert {var_name}={value} to type {var_type}: {e}")


def parse_complex_type(value: Any, type_name: str) -> Any:
    """
    Handle complex types like enums, models, and nested structures.

    Args:
        value: The value to parse
        type_name: Name of the type to convert to

    Returns:
        Converted value
    """
    if value is None:
        return None

    # Try to find the type in modules
    for module_name, module in sys.modules.items():
        if hasattr(module, type_name):
            type_class = getattr(module, type_name)

            # Handle Enum types
            if isinstance(type_class, type) and issubclass(type_class, Enum):
                return type_class(value)

            # Handle Pydantic models and other classes with __annotations__
            if hasattr(type_class, "__annotations__"):
                if isinstance(value, dict):
                    return type_class(**value)
                if isinstance(value, str):
                    # Try parsing as JSON if it's a string
                    try:
                        data = json.loads(value)
                        return type_class(**data)
                    except:
                        pass

    # As a fallback, just return the value
    return value
