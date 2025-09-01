from functools import wraps
from typing import Callable, Any, Dict, List
from functools import wraps
from dhisana.workflow.task import Task
from dhisana.workflow.agent import Agent

class Flow:
    def __init__(self, name: str):
        self.name = name
        self.tasks: Dict[str, Task] = {}
        self.agents: List[Agent] = []

    def add_task(self, task: Task) -> None:
        self.tasks[task.name] = task

    def add_agent(self, agent: Agent) -> None:
        self.agents.append(agent)

    def resolve_dependencies(self):
        for task in self.tasks.values():
            task.dependencies = [self.tasks[dep_name] for dep_name in task.dependency_names]

    async def run(self, inputs_list: List[Dict[str, Any]] = [{}]) -> None:
        self.resolve_dependencies()
        for task in self.tasks.values():
            if all(dep.results and dep.error is None for dep in task.dependencies):
                for agent in self.agents:
                    results = await agent.perform_task(task, inputs_list)
                    if results:
                        print(f"Results of task '{task.name}': {results}")
                    else:
                        print(f"Task '{task.name}' failed.")
            else:
                print(f"Skipping task '{task.name}' due to unmet dependencies.")

def flow(name: str):
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            f = Flow(name=name)
            await func(f, *args, **kwargs)
            await f.run(kwargs.get('inputs_list', [{}]))
        return wrapper
    return decorator