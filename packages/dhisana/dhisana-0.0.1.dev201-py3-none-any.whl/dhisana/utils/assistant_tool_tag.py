# Read API keys from environment variables
def assistant_tool(func):
    func.is_assistant_tool = True
    return func
