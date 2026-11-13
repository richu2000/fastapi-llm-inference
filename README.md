
# FastAPI LLM Inference API

A reliable REST API built using Python, FastAPI, HTTPX and Ollama to run local LLM inference.

## Architecture

Client (cURL / Python)
        |
        v
FastAPI REST API (Port 8000)
        |
        v
Ollama API (Port 11434)
        |
        v
LLM Model (Llama 3.2)
        |
        v
Generated Response (JSON)

## Features

- REST API using FastAPI
- Local LLM inference using Ollama
- Async HTTP communication using HTTPX
- Pydantic request validation
- Exception handling
- Application logging
- Unique request ID tracking
- Inference latency measurement
- API processing time measurement

## Tech Stack

- Python
- FastAPI
- Uvicorn
- HTTPX
- Pydantic
- Ollama
- Llama 3.2 (1B)

## Project Structure

fastapi-llm/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── tests/
    └── test_api.py

## Prerequisites

- Python 3.10+
- Ollama installed
- Git

## Setup

### 1. Clone the repository

git clone <YOUR_GITHUB_REPOSITORY_URL>

cd fastapi-llm

### 2. Create virtual environment

python3 -m venv venv

source venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Download the LLM model

ollama pull llama3.2:1b

### 5. Start FastAPI

uvicorn main:app --reload --port 8000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /generate | Generate LLM response |

## Example Request

curl -X POST http://localhost:8000/generate \
-H "Content-Type: application/json" \
-d '{
  "prompt": "Explain Kubernetes pods",
  "model": "llama3.2:1b"
}'

## Example Response

{
  "request_id": "example-request-id",
  "model": "llama3.2:1b",
  "response": "A Kubernetes Pod is the smallest deployable unit...",
  "latency_ms": 2500.50
}

## API Documentation

Open Swagger UI:

http://localhost:8000/docs

## Reliability Features

- Request and response logging
- Request ID correlation
- Connection error handling
- Inference timeout handling
- HTTP error handling
- Latency measurement

## Learning Outcomes

- Understanding LLM inference
- Integrating local LLMs with Python
- Building REST APIs with FastAPI
- Asynchronous programming
- Backend reliability and observability
- Git and GitHub version control

