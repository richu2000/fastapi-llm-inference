
import logging
import time
import uuid

import httpx

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field



# -----------------------------------
# 1. LOGGING CONFIGURATION
# -----------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger("llm_api")


# -----------------------------------
# 2. FASTAPI APPLICATION
# -----------------------------------

app = FastAPI(title="Reliable LLM Inference API")

OLLAMA_URL = "http://localhost:11434/api/generate"


# -----------------------------------
# 3. REQUEST MODEL
# -----------------------------------

class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=10000)
    model: str = "llama3.2:1b"


# -----------------------------------
# 4. RESPONSE MODEL
# -----------------------------------

class GenerateResponse(BaseModel):
    request_id: str
    model: str
    response: str
    latency_ms: float


# -----------------------------------
# 5. REQUEST LOGGING MIDDLEWARE
# -----------------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):

    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.perf_counter()

    logger.info(
        f"[{request_id}] Request started: "
        f"{request.method} {request.url.path}"
    )

    try:
        response = await call_next(request)

        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-ms"] = (
            f"{latency_ms:.2f}"
        )

        logger.info(
            f"[{request_id}] Request completed | "
            f"status={response.status_code} | "
            f"latency={latency_ms:.2f}ms"
        )

        return response

    except Exception:
        logger.exception(
            f"[{request_id}] Unhandled request error"
        )
        raise


# -----------------------------------
# 6. HEALTH CHECK
# -----------------------------------

@app.get("/health")
async def health():

    return {
        "status": "API is running"
    }


# -----------------------------------
# 7. LLM INFERENCE ENDPOINT
# -----------------------------------

@app.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    http_request: Request
):

    request_id = http_request.state.request_id

    payload = {
        "model": request.model,
        "prompt": request.prompt,
        "stream": False
    }

    logger.info(
        f"[{request_id}] Starting inference | "
        f"model={request.model}"
    )

    start_time = time.perf_counter()

    try:

        async with httpx.AsyncClient(
            timeout=120.0
        ) as client:

            # Call Ollama
            ollama_response = await client.post(
                OLLAMA_URL,
                json=payload
            )

        # Check HTTP status
        ollama_response.raise_for_status()

        # Parse JSON response
        result = ollama_response.json()

        # Validate expected response fields
        if not isinstance(result, dict):
            raise ValueError("Invalid Ollama response")

        if not isinstance(result.get("response"), str):
            raise ValueError("Missing generated response")

        # Measure Ollama round-trip latency
        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.info(
            f"[{request_id}] Inference completed | "
            f"latency={latency_ms:.2f}ms"
        )

        return GenerateResponse(
            request_id=request_id,
            model=result.get("model", request.model),
            response=result["response"],
            latency_ms=round(latency_ms, 2)
        )

    # -----------------------------------
    # 8. EXCEPTION HANDLING
    # -----------------------------------

    except httpx.TimeoutException:

        logger.error(
            f"[{request_id}] Ollama request timed out"
        )

        raise HTTPException(
            status_code=504,
            detail="LLM inference timed out"
        )

    except httpx.ConnectError:

        logger.error(
            f"[{request_id}] Cannot connect to Ollama"
        )

        raise HTTPException(
            status_code=503,
            detail="Ollama service unavailable"
        )

    except httpx.HTTPStatusError as exc:

        logger.error(
            f"[{request_id}] Ollama HTTP error: "
            f"{exc.response.status_code}"
        )

        raise HTTPException(
            status_code=502,
            detail="Ollama returned an error"
        )

    except httpx.RequestError:

        logger.exception(
            f"[{request_id}] Ollama network request failed"
        )

        raise HTTPException(
            status_code=502,
            detail="Error communicating with Ollama"
        )

    except ValueError:

        logger.exception(
            f"[{request_id}] Invalid Ollama response"
        )

        raise HTTPException(
            status_code=502,
            detail="Invalid response from Ollama"
        )

    except Exception:

        logger.exception(
            f"[{request_id}] Unexpected inference error"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

