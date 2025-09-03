# this code is not very well debugged yet, but it seems to work
import argparse
import os
import json
from typing import List, Dict, Optional, Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn
from starlette.responses import PlainTextResponse

from grok3api.client import GrokClient
from grok3api.logger import logger
from grok3api.types.GrokResponse import GrokResponse


class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "grok-3"
    messages: List[Message]
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Dict[str, Any]

app = FastAPI(title="Grok3API OpenAI-Compatible Server")

env_cookies = os.getenv("GROK_COOKIES", None)
TIMEOUT = os.getenv("GROK_TIMEOUT", 120)

try:
    grok_client = GrokClient(
        cookies=None,
        proxy=os.getenv("GROK_PROXY", None),
        timeout=TIMEOUT,
        history_msg_count=0,
        always_new_conversation=True,
    )
except Exception as e:
    logger.error(f"Failed to initialize GrokClient: {e}")
    raise

async def handle_grok_str_request(q: str):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    response: GrokResponse = await grok_client.async_ask(
        message=q,
        modelName="grok-3",
        timeout=TIMEOUT,
        customInstructions="",
        disableSearch=False,
        enableImageGeneration=False,
        enableImageStreaming=False,
        enableSideBySide=False
    )

    if response.error or not response.modelResponse.message:
        raise HTTPException(
            status_code=500,
            detail=response.error or "No response from Grok API."
        )

    return response.modelResponse.message


@app.get("/v1/string", response_class=PlainTextResponse)
async def simple_string_query_get(q: str):
    """
    Простой эндпоинт, принимающий строку как query-параметр и возвращающий ответ от Grok.
    Пример: GET /v1/string?q=Привет
    """
    return await handle_grok_str_request(q)


@app.post("/v1/string", response_class=PlainTextResponse)
async def simple_string_query_post(request: Request):
    """
    Простой эндпоинт для POST запроса, принимающий строку как тело и возвращающий ответ от Grok.
    Пример: POST /v1/string с телом запроса "Привет"
    """
    data = await request.body()
    q = data.decode("utf-8").strip()

    return await handle_grok_str_request(q)

@app.post("/v1/chat/completions")
async def chat_completions(
        request: ChatCompletionRequest,
):
    """Эндпоинт для обработки запросов в формате OpenAI."""
    try:
        if request.stream:
            raise HTTPException(status_code=400, detail="Streaming is not supported.")

        grok_client.cookies = env_cookies

        history_messages = []
        last_user_message = ""

        for msg in request.messages:
            if msg.role == "user" and not last_user_message:
                last_user_message = msg.content
            else:
                sender = "USER" if msg.role == "user" else "ASSISTANT" if msg.role == "assistant" else "SYSTEM"
                history_messages.append({"sender": sender, "message": msg.content})

        if history_messages:
            history_json = json.dumps(history_messages)
            message_payload = f"{history_json}\n{last_user_message}" if last_user_message else history_json
        else:
            message_payload = last_user_message

        if not message_payload.strip():
            raise HTTPException(status_code=400, detail="No user message provided.")

        response: GrokResponse = await grok_client.async_ask(
            message=message_payload,
            modelName=request.model,
            timeout=TIMEOUT,
            customInstructions="",
            disableSearch=False,
            enableImageGeneration=False,
            enableImageStreaming=False,
            enableSideBySide=False
        )

        if response.error or not response.modelResponse.message:
            raise HTTPException(
                status_code=500,
                detail=response.error or "No response from Grok API."
            )

        import time
        current_time = int(time.time())
        response_id = response.responseId or f"chatcmpl-{current_time}"

        chat_response = ChatCompletionResponse(
            id=response_id,
            created=current_time,
            model=request.model,
            choices=[
                Choice(
                    index=0,
                    message=Message(
                        role="assistant",
                        content=response.modelResponse.message
                    ),
                    finish_reason="stop"
                )
            ],
            usage={
                "prompt_tokens": len(message_payload.split()),
                "completion_tokens": len(response.modelResponse.message.split()),
                "total_tokens": len(message_payload.split()) + len(response.modelResponse.message.split())
            }
        )

        return chat_response

    except Exception as ex:
        logger.error(f"Error in chat_completions: {ex}")
        raise HTTPException(status_code=500, detail=str(ex))

def run_server(default_host: str = "0.0.0.0", default_port: int = 8000):
    parser = argparse.ArgumentParser(description="Run Grok3API-compatible server.")
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("GROK_SERVER_HOST", default_host),
        help="Host to bind the server to (default: env GROK_SERVER_HOST or 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("GROK_SERVER_PORT", default_port)),
        help="Port to bind the server to (default: env GROK_SERVER_PORT or 8000)"
    )

    args = parser.parse_args()

    print(f"🚀 Starting server on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    run_server()