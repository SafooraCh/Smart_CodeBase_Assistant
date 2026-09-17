# Smart_CodeBase_Assistant

# Smart Codebase & Tech Stack Knowledge Assistant

A local AI assistant for understanding a codebase. Upload a project as a zip, and it reads the code, breaks it into chunks, and lets you search or chat with it — all running locally.

## What it does

- Upload a project zip
- Cleans out junk like `node_modules`, `.git`, `venv`, build folders
- Splits the code into chunks and embeds them
- Saves everything to SQLite + Qdrant
- You can search the code or just ask it questions
- Answers come with the file/lines they're based on — if it can't find anything, it tells you instead of guessing
- You can also list indexed files, view a file's chunks, read a file back, or delete it

## How it works

1. Upload a zip, it gets unzipped.
2. Only real code/docs files are kept (`.py`, `.js`, `.ts`, `.md`, `.json`, `.yaml`, `.yml`, `.txt`).
3. Files get split into chunks with file path + line numbers attached.
4. Chunks get embedded and stored.
5. When you ask something, it finds the closest matching chunks and gives them to a local LLM (Ollama) to answer from — nothing outside that context.

## Tech stack

Python, FastAPI, SQLite, Qdrant, sentence-transformers, LangChain, Ollama, Docker.

## API

| Method   | Endpoint                         | What it does                       |
| -------- | -------------------------------- | ---------------------------------- |
| `GET`    | `/`                              | Status check                       |
| `GET`    | `/health`                        | Checks API, Qdrant, Ollama are up  |
| `POST`   | `/codebase/index`                | Upload + index a zip               |
| `GET`    | `/codebase/files`                | List indexed files                 |
| `GET`    | `/codebase/files/{file_id}`      | Get a file's metadata + chunks     |
| `GET`    | `/codebase/files/{file_id}/text` | Get a file's full text             |
| `DELETE` | `/codebase/files/{file_id}`      | Remove a file                      |
| `POST`   | `/search`                        | Search the code                    |
| `POST`   | `/chat`                          | Ask a question, get a cited answer |

Full docs at `/docs` once it's running.

## Running it

Install Docker Desktop and Ollama first.

```bash
ollama pull llama3:8b
docker compose up --build
```

Then open `http://localhost:8000/docs` and try it out.

## Config

Set via environment variables in `app/config.py` — things like `OLLAMA_MODEL`, `QDRANT_HOST`, `SEARCH_TOP_K`, etc. Defaults work out of the box for local dev.

## Status

**Done:** upload, chunking, embeddings, storage, search, and chat with citations.

**Next:** a frontend, multi-project support, streaming responses.

## Why

A fully local assistant that answers questions about your code using your actual code — nothing made up, nothing leaves your machine.
