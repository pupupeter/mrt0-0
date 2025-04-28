# mcp.py
import os
import asyncio
from config import DEFAULT_MODEL, MODEL_PROVIDER, GEMINI_API_KEY, HF_API_KEY

# ✅ 載入不同 Provider 的 LLM client
from google import genai
import requests

class ModelClient:
    def __init__(self, model=DEFAULT_MODEL, provider=MODEL_PROVIDER):
        self.model = model
        self.provider = provider
        if provider == 'gemini':
            self.client = genai.Client(api_key=GEMINI_API_KEY)
        elif provider == 'hf':
            self.client = HF_API_KEY  # just save token
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def generate(self, messages: list):
        content = "\n".join(messages)
        if self.provider == 'gemini':
            response = self.client.models.generate_content(
                model=self.model,
                contents=content
            )
            return response.text.strip()
        elif self.provider == 'hf':
            url = f"https://api-inference.huggingface.co/models/{self.model}"
            headers = {"Authorization": f"Bearer {self.client}"}
            payload = {"inputs": content}
            r = requests.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()[0]['generated_text'].strip()
        else:
            raise ValueError("Invalid model provider")

class ContextManager:
    def __init__(self):
        self.history = []

    def add_message(self, role, content):
        self.history.append(f"[{role}] {content}")

    def get_context(self):
        return [msg for msg in self.history]

class ProtocolAgent:
    def __init__(self, name, role, model_client: ModelClient):
        self.name = name
        self.role = role
        self.model_client = model_client
        self.context_manager = ContextManager()  # ✅ 每個 Agent 自己有上下文

    async def act(self, input_text):
        self.context_manager.add_message(self.role, input_text)
        context = self.context_manager.get_context()
        response = await self.model_client.generate(context)
        self.context_manager.add_message(self.name, response)
        return response
    
class MultiTaskAgent(ProtocolAgent):
    def __init__(self, name, role, model_client: ModelClient):
        super().__init__(name=name, role=role, model_client=model_client)

    async def perform_task(self, task_type, input_text):
        if task_type == "explanation":
            return await self.explain(input_text)
        elif task_type == "problem_solving":
            return await self.solve_problem(input_text)
        else:
            return "Unknown task type"

    async def explain(self, input_text):
        explanation = f"Explaining: {input_text} ..."
        return explanation

    async def solve_problem(self, input_text):
        solution = f"Solving: {input_text} ..."
        return solution
