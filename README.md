# Smart Codebase Assistant

This project helps developers understand their code.

You can upload a project ZIP file, select the project, and ask questions about its code. The system finds relevant code from the selected project and gives an answer with file references.

## Features

- Upload a project ZIP file
- Split code into smaller parts
- Create embeddings for searching
- Store embeddings in Qdrant Cloud
- Store file details in SQLite
- Search code by asking a question
- Select a project before asking questions
- Get AI answers about the selected project with file references
- View and delete indexed files

## Tools Used

- Python and FastAPI — backend
- Groq API — AI answers
- `openai/gpt-oss-20b` — language model
- Sentence Transformers — embeddings
- Qdrant Cloud — vector storage
- SQLite — file details
- Docker and Docker Compose — running the project

## How It Works

1. Upload your project as a ZIP file.
2. The system reads supported files and splits them into small parts.
3. It creates embeddings and saves them in Qdrant Cloud.
4. Select the project you want to ask about.
5. Enter your question about that project.
6. The system finds useful code from the selected project and sends it to Groq.
7. You get an answer with file references.

## Run the Project

1. Install Docker and start it.
2. Add your Groq API key, Qdrant Cloud URL, and Qdrant API key to the environment settings used by Docker Compose.
3. Open a terminal in the project folder and run:

```bash
docker compose up --build
```

4. Open this link to test the APIs:

[http://localhost:8000/docs](http://localhost:8000/docs)

Use the upload endpoint first. For chat, select your project and then enter your question.

Keep your API keys private. Internet is needed to connect to Groq and Qdrant Cloud.

## Main APIs

| Method | API | Purpose |
|---|---|---|
| POST | `/codebase/index` | Upload a ZIP |
| GET | `/codebase/files` | View indexed files |
| GET | `/codebase/files/{file_id}` | View file details |
| DELETE | `/codebase/files/{file_id}` | Delete a file from the index |
| POST | `/search` | Search code |
| POST | `/chat` | Ask about the selected project |
| GET | `/health` | Check service status |

## Chat Example

1. Select your project, for example `mini_shop`.
2. Ask: “How does this project connect to the database?”
3. The assistant answers using code from `mini_shop`.

The chat request includes the selected project along with the question. Use the project field shown in your updated API; its exact field name is not confirmed in the shared ZIP.

## Current Setup

FastAPI runs in Docker on port **8000**. Groq generates answers, Qdrant Cloud stores embeddings, and SQLite stores file details.

A local Qdrant container is also defined in Docker Compose. It is separate from Qdrant Cloud.

This README describes the updated setup. The shared ZIP contains the older Ollama code, so use the updated Groq and Qdrant Cloud files to run this version.
