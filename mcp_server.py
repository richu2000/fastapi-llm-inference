import os
import json
import time
import httpx

from mcp.server.fastmcp import FastMCP


# Create MCP server
mcp = FastMCP("AI Infrastructure Assistant")


# Ollama configuration
OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
).rstrip("/")

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:1b"
)


@mcp.tool()
async def check_ollama_health() -> str:
    """
    Check Ollama availability and verify that
    the configured LLM model is installed.
    """

    start_time = time.perf_counter()

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:

            # Check Ollama API availability
            health_response = await client.get(
                f"{OLLAMA_BASE_URL}/"
            )

            health_response.raise_for_status()

            # Retrieve installed models
            models_response = await client.get(
                f"{OLLAMA_BASE_URL}/api/tags"
            )

            models_response.raise_for_status()

            models_data = models_response.json()

            available_models = [
                model["name"]
                for model in models_data.get("models", [])
            ]

            model_available = any(
                model.split(":")[0] == OLLAMA_MODEL.split(":")[0]
                and (
                    ":" not in OLLAMA_MODEL
                    or model.split(":")[-1] == OLLAMA_MODEL.split(":")[-1]
                )
                for model in available_models
            )

            latency_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2
            )

            result = {
                "service": "Ollama",
                "status": "healthy" if model_available else "degraded",
                "api_available": True,
                "configured_model": OLLAMA_MODEL,
                "model_available": model_available,
                "available_models": available_models,
                "response_time_ms": latency_ms
            }

            return json.dumps(result, indent=2)

    except httpx.TimeoutException:
        result = {
            "service": "Ollama",
            "status": "unhealthy",
            "error": "Ollama request timed out"
        }

    except httpx.ConnectError:
        result = {
            "service": "Ollama",
            "status": "unhealthy",
            "error": "Cannot connect to Ollama",
            "url": OLLAMA_BASE_URL
        }

    except httpx.HTTPStatusError as exc:
        result = {
            "service": "Ollama",
            "status": "unhealthy",
            "error": "Ollama returned an HTTP error",
            "http_status": exc.response.status_code
        }

    except (ValueError, KeyError):
        result = {
            "service": "Ollama",
            "status": "unhealthy",
            "error": "Invalid response from Ollama"
        }

    except httpx.RequestError as exc:
        result = {
            "service": "Ollama",
            "status": "unhealthy",
            "error": f"Request failed: {type(exc).__name__}"
        }

    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")

