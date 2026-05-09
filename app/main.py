from fastapi import FastAPI

from app.models import (
    ChatRequest
)

from app.agent import generate_reply

app = FastAPI()


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


@app.post("/chat")
def chat(req: ChatRequest):

    messages = [
        {
            "role": m.role,
            "content": m.content
        }
        for m in req.messages
    ]

    return generate_reply(messages)