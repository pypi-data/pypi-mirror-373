from functools import wraps
from typing import Callable, Any, Dict, List
from functools import wraps

class Task:
    def __init__(self, name: str, description: str, label: str, function: Callable[..., Any]):
        self.name = name
        self.description = description
        self.label = label
        self.function = function
        self.dependencies: List['Task'] = []
        self.results: List[Dict[str, Any]] = []
        self.error = None

    async def run(self, inputs_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            self.results = []
            for inputs in inputs_list:
                # Gather inputs from dependencies
                dep_results = {dep.label: dep.results for dep in self.dependencies}
                inputs.update(dep_results)
                result = await self.function([inputs])
                self.results.extend(result)
        except Exception as e:
            self.error = e
            print(f"Error in task '{self.name}': {e}")
        return self.results

    def set_dependencies(self, dependencies: List['Task']):
        self.dependencies = dependencies

def task(name: str, description: str = "", label: str = "", dependencies: List[str] = None):
    # Enforce naming convention: alphanumeric characters and underscores only
    if not name.replace('_', '').isalnum():
        raise ValueError("Task name must contain only alphanumeric characters and underscores.")
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await func(*args, **kwargs)
        wrapper.task = Task(name=name, description=description, label=label or name, function=wrapper)
        wrapper.task.dependency_names = dependencies or []
        return wrapper
    return decorator