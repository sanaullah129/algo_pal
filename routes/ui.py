"""
UI routes — server-rendered pages via Jinja2 templates.
"""
import re
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["UI"])
templates = Jinja2Templates(directory="templates")

_SESSION_ID_RE = re.compile(r'^[a-zA-Z0-9_-]{1,80}$')


@router.get("/", response_class=HTMLResponse)
async def sessions_page(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.get("/chat/{session_id}", response_class=HTMLResponse)
async def chat_page(request: Request, session_id: str):
    # Validate session_id to prevent path traversal / injection
    if not _SESSION_ID_RE.match(session_id):
        return RedirectResponse(url="/")
    return templates.TemplateResponse(request, "chat.html", {"session_id": session_id})


@router.get("/new-chat")
async def new_chat():
    session_id = f"session_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    return RedirectResponse(url=f"/chat/{session_id}")
