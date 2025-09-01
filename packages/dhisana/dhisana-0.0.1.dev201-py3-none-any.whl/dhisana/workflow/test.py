from http.client import HTTPException
import os
from typing import Any, Dict, List
import openai
import asyncio

from dhisana.workflow.task import task
from dhisana.workflow.flow import Flow, flow
from dhisana.workflow.agent import agent



# Initialize OpenAI API
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

async def call_openai_api_test(system_content: str, user_content: str, max_tokens: int) -> str:
    return "This is a test response."

async def call_openai_api(system_content: str, user_content: str, max_tokens: int) -> str:
    try:
        # Call the OpenAI API using the new client method
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ],
            max_tokens=max_tokens
        )
        
        # Access the response content properly
        reply = response.choices[0].message.content.strip()
        return reply
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")




@task(name="generate_poem", description="Generate a poem about a given topic", label="poem")
async def generate_poem(inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = []
    for input_data in inputs:
        topic = input_data.get('topic', 'life')
        system_content = "You are a poet."
        user_content = f"Write a poem about {topic}."
        poem = await call_openai_api(system_content, user_content, max_tokens=100)
        results.append({'topic': topic, 'poem': poem})
    return results

@task(name="summarize_poem", description="Summarize the given poem", label="summary", dependencies=["generate_poem"])
async def summarize_poem(inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = []
    for input_data in inputs:
        poem = input_data.get('poem', '')
        system_content = "You are a literary critic."
        user_content = f"Summarize the following poem:\n\n{poem}"
        summary = await call_openai_api(system_content, user_content, max_tokens=50)
        results.append({'poem': poem, 'summary': summary})
    return results

@task(name="analyze_sentiment", description="Analyze the sentiment of the given text", label="sentiment", dependencies=["summarize_poem"])
async def analyze_sentiment(inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = []
    for input_data in inputs:
        summary = input_data.get('summary', '')
        system_content = "You are a sentiment analyst."
        user_content = f"Analyze the sentiment of the following text:\n\n{summary}"
        sentiment = await call_openai_api(system_content, user_content, max_tokens=50)
        results.append({'summary': summary, 'sentiment': sentiment})
    return results

@agent
class AIAgent:
    pass

@flow(name="AI_Workflow")
async def ai_workflow(f: Flow, inputs_list: List[Dict[str, Any]]):
    f.add_task(generate_poem.task)
    f.add_task(summarize_poem.task)
    f.add_task(analyze_sentiment.task)
    f.add_agent(AIAgent.agent)

# Execute the workflow with a list of topics
topics = [{"topic": "artificial intelligence"}, {"topic": "quantum computing"}]

asyncio.run(ai_workflow(inputs_list=topics))
