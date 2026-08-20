import json
from datetime import datetime

from sqlalchemy import select

from src.API.database import Base, SessionLocal, engine
from src.Database.chat_models import ChatMessage, ChatSession


def init_chat_tables() -> None:
    """Create chat tables in the existing data/pmi.db."""
    Base.metadata.create_all(bind=engine)


def list_chats(user_id: int) -> dict:
    """Return chats belonging only to the authenticated user."""
    with SessionLocal() as db:
        chat_rows = db.scalars(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(
                ChatSession.updated_at.desc(),
                ChatSession.id.desc(),
            )
        ).all()

        result = {}

        for chat in chat_rows:
            message_rows = db.scalars(
                select(ChatMessage)
                .where(
                    ChatMessage.chat_id == chat.id,
                    ChatMessage.user_id == user_id,
                )
                .order_by(ChatMessage.id.asc())
            ).all()

            active_reference = None

            if chat.active_reference:
                try:
                    active_reference = json.loads(
                        chat.active_reference
                    )
                except (TypeError, json.JSONDecodeError):
                    active_reference = chat.active_reference

            result[str(chat.id)] = {
                "title": chat.title,
                "messages": [
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                    for message in message_rows
                ],
                "active_reference": active_reference,
            }

        return result


def create_chat(user_id: int, title: str = "New Chat") -> int:
    with SessionLocal() as db:
        chat = ChatSession(
            user_id=user_id,
            title=title,
        )

        db.add(chat)
        db.commit()
        db.refresh(chat)

        return chat.id


def ensure_first_chat(user_id: int) -> int:
    with SessionLocal() as db:
        existing = db.scalar(
            select(ChatSession.id)
            .where(ChatSession.user_id == user_id)
            .limit(1)
        )

        if existing is not None:
            return existing

        chat = ChatSession(
            user_id=user_id,
            title="New Chat",
        )

        db.add(chat)
        db.commit()
        db.refresh(chat)

        return chat.id


def _get_owned_chat(
    db,
    chat_id: int,
    user_id: int,
) -> ChatSession:

    chat = db.scalar(
        select(ChatSession).where(
            ChatSession.id == chat_id,
            ChatSession.user_id == user_id,
        )
    )

    if chat is None:
        raise ValueError("Chat not found for this user.")

    return chat


def add_message(
    *,
    chat_id: int,
    user_id: int,
    role: str,
    content: str,
) -> None:

    with SessionLocal() as db:
        chat = _get_owned_chat(
            db,
            chat_id,
            user_id,
        )

        db.add(
            ChatMessage(
                chat_id=chat.id,
                user_id=user_id,
                role=role,
                content=content,
            )
        )

        chat.updated_at = datetime.utcnow()

        db.commit()


def update_chat(
    *,
    chat_id: int,
    user_id: int,
    title: str | None = None,
    active_reference=None,
) -> None:

    with SessionLocal() as db:
        chat = _get_owned_chat(
            db,
            chat_id,
            user_id,
        )

        if title is not None:
            chat.title = title

        if active_reference is not None:
            chat.active_reference = json.dumps(
                active_reference,
                ensure_ascii=False,
            )

        chat.updated_at = datetime.utcnow()

        db.commit()