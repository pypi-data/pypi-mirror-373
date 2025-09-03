from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .config import load_config
from . import providers
from .providers import ProviderError


class Message(BaseModel):
    role: str
    content: str


class ChatBody(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    provider: Optional[str] = None
    temperature: float = 0.2
    stream: bool = False


app = FastAPI(title="TermAI Server", version="1.1.4")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/v1/chat")
def chat(body: ChatBody):
    cfg = load_config()
    if body.model:
        cfg["model"] = body.model
    if body.provider:
        cfg["default_provider"] = body.provider
    try:
        provider = providers.make_provider(cfg)
        msgs = [providers.ChatMessage(role=m.role, content=m.content) for m in body.messages]
        text = "".join(provider.chat(msgs, cfg["model"], temperature=body.temperature, stream=False))
        return {"content": text}
    except ProviderError as e:
        raise HTTPException(400, detail=str(e))
