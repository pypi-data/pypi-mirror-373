# Global List of tools that can be used in the assistant
# Only functions marked with @assistant_tool will be available in the allowed list
# This is in addition to the tools from OpenAPI Spec add to allowed tools
# These tools are loaded in the agent like below

# async def load_global_tool_function():
#     # Iterate over all modules in the package
#     for loader, module_name, is_pkg in pkgutil.walk_packages(global_tools.__path__):
#         module = importlib.import_module(f"{global_tools.__name__}.{module_name}")
#         for name in dir(module):
#             func = getattr(module, name)
#             if callable(func) and getattr(func, 'is_assistant_tool', False):
#                 GLOBAL_TOOLS_FUNCTIONS[name] = func

# Global Data Models Used for Data Extraction. These can be referenced in workflows.
GLOBAL_DATA_MODELS = []

# Global Functions used in workflows. Like CRM, Email, etc. They can be invoked as Python functions.
GLOBAL_TOOLS_FUNCTIONS = {}

# GLOBAL_TOOLS_FUNCTIONS in OPENAI function spec format
# src/dhisana/utils/agent_tools.py

# Global List of tools that can be used in the assistant
# Only functions marked with @assistant_tool will be available in the allowed list
# This is in addition to the tools from OpenAPI Spec add to allowed tools
# These tools are loaded in the agent like below

# async def load_global_tool_function():
#     # Iterate over all modules in the package
#     for loader, module_name, is_pkg in pkgutil.walk_packages(global_tools.__path__):
#         module = importlib.import_module(f"{global_tools.__name__}.{module_name}")
#         for name in dir(module):
#             func = getattr(module, name)
#             if callable(func) and getattr(func, 'is_assistant_tool', False):
#                 GLOBAL_TOOLS_FUNCTIONS[name] = func

# Ensure GLOBAL_DATA_MODELS is only initialized once
if 'GLOBAL_DATA_MODELS' not in globals():
    GLOBAL_DATA_MODELS = []

# Ensure GLOBAL_TOOLS_FUNCTIONS is only initialized once
if 'GLOBAL_TOOLS_FUNCTIONS' not in globals():
    GLOBAL_TOOLS_FUNCTIONS = {}

# Ensure GLOBAL_OPENAI_ASSISTANT_TOOLS is only initialized once
if 'GLOBAL_OPENAI_ASSISTANT_TOOLS' not in globals():
    GLOBAL_OPENAI_ASSISTANT_TOOLS = []
    
if 'GLOBAL_TOOLS_CACHE_PATH' not in globals():
    GLOBAL_TOOLS_CACHE_PATH = '/tmp/dhisana_ai'