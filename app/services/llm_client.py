# import httpx

# from app.config import OLLAMA_HOST, OLLAMA_MODEL


# SYSTEM_PROMPT = """
# You are a codebase assistant.

# You answer developer questions using ONLY the code and documentation
# provided in the CONTEXT section.

# Rules you MUST follow:

# 1. Answer ONLY using information from the CONTEXT section.
#    Do not use outside knowledge.

# 2. Do NOT invent:
#    - function names
#    - class names
#    - variable names
#    - parameters
#    - API endpoints
#    - file paths
#    - database tables
#    - code behavior

# 3. Comments, docstrings, examples, and string literals may contain
#    sample or placeholder code. Do NOT treat them as real implementations.

# 4. Before saying that a function or class exists, make sure it is actually
#    defined in the provided code using a real def or class statement.

# 5. If the provided context does not contain enough information to answer
#    the question, clearly say:
#    "The provided code context does not contain enough information to answer this."

# 6. Whenever you reference code, mention the file path where that code appears.

# 7. Keep the answer concise, clear, and technical.

# 8. Never guess.
# """


# def _build_prompt(query: str, context_chunks: list[dict]) -> str:
#     context_blocks = []

#     for chunk in context_chunks:
#         file_path = chunk.get("file_path", "Unknown file")
#         start_line = chunk.get("start_line", "?")
#         end_line = chunk.get("end_line", "?")
#         text = chunk.get("text", "")

#         context_blocks.append(
#             f"### {file_path} (Lines {start_line}-{end_line})\n"
#             f"{text}"
#         )

#     if context_blocks:
#         context_text = "\n\n".join(context_blocks)
#     else:
#         context_text = "No code context was provided."

#     return (
#         f"{SYSTEM_PROMPT.strip()}\n\n"
#         f"CONTEXT:\n"
#         f"{context_text}\n\n"
#         f"QUESTION:\n"
#         f"{query}\n\n"
#         f"ANSWER:"
#     )

# def generate_answer(
#     query: str,
#     context_chunks: list[dict],
#     timeout: float = 60.0,
# ) -> str:
#     if not GROQ_API_KEY:
#         raise ValueError("GROQ_API_KEY is not configured")

#     prompt = _build_prompt(query, context_chunks)
#     url = "https://api.groq.com/openai/v1/chat/completions"

#     response = httpx.post(
#         url,
#         headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
#         json={
#             "model": GROQ_MODEL,
#             "messages": [{"role": "user", "content": prompt}],
#         },
#         timeout=timeout,
#     )
#     response.raise_for_status()

#     data = response.json()
#     choices = data.get("choices") or []
#     answer = choices[0].get("message", {}).get("content") if choices else None

#     if not isinstance(answer, str):
#         raise ValueError("Groq response does not contain a valid message content.")

#     return answer.strip()

# # def generate_answer(
# #     query: str,
# #     context_chunks: list[dict],
# #     timeout: float = 60.0,
# # ) -> str:
# #     prompt = _build_prompt(query, context_chunks)

# #     url = f"{OLLAMA_HOST.rstrip('/')}/api/generate"

# #     response = httpx.post(
# #         url,
# #         json={
# #             "model": OLLAMA_MODEL,
# #             "prompt": prompt,
# #             "stream": False,
# #         },
# #         timeout=timeout,
# #     )

# #     response.raise_for_status()

# #     data = response.json()

# #     answer = data.get("response")

# #     if not isinstance(answer, str):
# #         raise ValueError(
# #             "Ollama response does not contain a valid 'response' field."
# #         )

# #     return answer.strip()
import httpx

from app.config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL

SYSTEM_PROMPT = """
You are a codebase assistant.

You answer developer questions using ONLY the code and documentation
provided in the CONTEXT section.

Rules you MUST follow:

1. Answer ONLY using information from the CONTEXT section.
   Do not use outside knowledge.

2. Do NOT invent:
   - function names
   - class names
   - variable names
   - parameters
   - API endpoints
   - file paths
   - database tables
   - code behavior

3. Comments, docstrings, examples, and string literals may contain
   sample or placeholder code. Do NOT treat them as real implementations.

4. Before saying that a function or class exists, make sure it is actually
   defined in the provided code using a real def or class statement.

5. If the provided context does not contain enough information to answer
   the question, clearly say:
   "The provided code context does not contain enough information to answer this."

6. Whenever you reference code, mention the file path where that code appears.

7. Keep the answer concise, clear, and technical.

8. Never guess.
"""


def _build_prompt(query: str, context_chunks: list[dict]) -> str:
    context_blocks = []

    for chunk in context_chunks:
        file_path = chunk.get("file_path", "Unknown file")
        start_line = chunk.get("start_line", "?")
        end_line = chunk.get("end_line", "?")
        text = chunk.get("text", "")

        context_blocks.append(
            f"### {file_path} (Lines {start_line}-{end_line})\n"
            f"{text}"
        )

    context_text = (
        "\n\n".join(context_blocks)
        if context_blocks
        else "No code context was provided."
    )

    return (
        f"{SYSTEM_PROMPT.strip()}\n\n"
        f"CONTEXT:\n{context_text}\n\n"
        f"QUESTION:\n{query}\n\n"
        f"ANSWER:"
    )


def generate_answer(
    query: str,
    context_chunks: list[dict],
    timeout: float = 60.0,
) -> str:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not configured")

    prompt = _build_prompt(query, context_chunks)
    url = f"{GROQ_BASE_URL.rstrip('/')}/chat/completions"

    response = httpx.post(
        url,
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={
            "model": GROQ_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
        },
        timeout=timeout,
    )
    response.raise_for_status()

    data = response.json()
    choices = data.get("choices") or []

    answer = (
        choices[0].get("message", {}).get("content")
        if choices
        else None
    )

    if not isinstance(answer, str):
        raise ValueError(
            "Groq response does not contain valid message content."
        )

    return answer.strip()