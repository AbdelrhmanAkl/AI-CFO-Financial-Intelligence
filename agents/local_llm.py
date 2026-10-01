import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()


LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "ollama",
).lower().strip()


if LLM_PROVIDER == "ollama":

    llm = ChatOllama(
        model="qwen3:8b",
        temperature=0,
    )


elif LLM_PROVIDER == "gemini":

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is required when LLM_PROVIDER=gemini."
        )

    class GeminiTextWrapper:
        def __init__(self, model):
            self.model = model

        def invoke(self, prompt):
            response = self.model.invoke(prompt)

            content = response.content

            if isinstance(content, list):
                text_parts = []

                for block in content:
                    if isinstance(block, dict):
                        text = block.get("text")

                        if text:
                            text_parts.append(text)

                content = "".join(text_parts)

            response.content = content

            return response

    gemini = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0,
        google_api_key=api_key,
    )

    llm = GeminiTextWrapper(gemini)


else:

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}. "
        "Use 'ollama' or 'gemini'."
    )