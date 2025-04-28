import os
from dotenv import load_dotenv
from smolagents import CodeAgent, LiteLLMModel

load_dotenv()
gemini_api_key = os.environ.get("GEMINI_API_KEY")

model_id = "gemini/gemini-2.0-flash"
model = LiteLLMModel(model_id=model_id, GEMINI_API_KEY=gemini_api_key)

fastest_agent = CodeAgent(tools=[], model=model, add_base_tools=True)
fewest_transfers_agent = CodeAgent(tools=[], model=model, add_base_tools=True)

# 記憶儲存結構
user_contexts = {}

def run_with_user_context(agent, question, user_id, context_key):
    user_ctx = user_contexts.setdefault(user_id, {'fastest': [], 'fewest': []})
    history = user_ctx.get(context_key, [])

    full_prompt = "\n".join(history + [question])
    response = agent.run(full_prompt)
    response_text = str(response).strip()

    history.append(question)
    history.append(response_text)
    if len(history) > 10:
        history[:] = history[-10:]

    return response_text

def reset_user_context(user_id):
    user_contexts[user_id] = {'fastest': [], 'fewest': []}
