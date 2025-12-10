# backend/llm/generator.py
import os
from textwrap import dedent
from groq import Groq


class LLMGenerator:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set in environment/.env")

        self.client = Groq(api_key=api_key)
        self.model = os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile")

    def generate_answer(self, question: str, contexts, citations):
        """
        contexts: list[str]
        citations: list[str] (page + modality)
        Returns answer string.
        """
        context_block = "\n\n---\n\n".join(contexts)
        citation_block = "; ".join(citations)

        system_prompt = dedent(
            """
            You are a retrieval-augmented QA assistant for IMF-style country reports.
            Answer ONLY using the provided context from the document.
            Be concise, factual, and include references to pages in parentheses like (see page X).
            If the answer is not present in the context, say: "I cannot find this information in the document."
            """
        )

        user_prompt = dedent(
            f"""
            Question:
            {question}

            Document context:
            {context_block}

            Relevant source locations:
            {citation_block}

            Now answer the question based strictly on this context.
            """
        )

        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        return chat_completion.choices[0].message.content.strip()
