from typing import Any, Dict, List

from dhisana.workflow.task import Task

class Agent:
    def __init__(self, name: str):
        self.name = name

    async def perform_task(self, task: Task, inputs_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if task.error:
            print(f"Skipping task '{task.name}' due to previous error.")
            return []
        print(f"\nAgent {self.name} is performing task: {task.name}")       
        return await task.run(inputs_list)

def agent(cls):
    cls.agent = Agent(name=cls.__name__)
    return cls