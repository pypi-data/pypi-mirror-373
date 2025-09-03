# src/broadie/persistence.py
import asyncio
import datetime
import logging
import pathlib
import uuid
from contextlib import AsyncExitStack

from langchain.embeddings import init_embeddings
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres import AsyncPostgresStore

from broadie.config import settings


class PersistenceMixin:
    def __init__(self):
        self.url = settings.DATABASE_URL
        self.embedding_model = settings.EMBEDDING_MODEL
        self.decay_minutes = settings.MEMORY_DECAY_MINUTES
        self._exit_stack = AsyncExitStack()
        self.checkpointer = None
        self.store = None

    # ----------------------------
    # Setup
    # ----------------------------
    async def init_checkpointer(self):
        """Initialize async checkpointer depending on DATABASE_URL."""
        if not self.url:
            self.checkpointer = InMemorySaver()
            return self.checkpointer

        if self.url.startswith("sqlite://"):
            db_path = pathlib.Path(self.url.split("///", 1)[-1]).name
            cm = AsyncSqliteSaver.from_conn_string(db_path)
            self.checkpointer = await self._exit_stack.enter_async_context(cm)
            return self.checkpointer

        if self.url.startswith(("postgres://", "postgresql://")):
            cm = AsyncPostgresSaver.from_conn_string(self.url)
            self.checkpointer = await self._exit_stack.enter_async_context(cm)
            return self.checkpointer

        raise ValueError(f"Unsupported DATABASE_URL schema: {self.url}")

    async def init_store(self):
        """Initialize async store depending on DATABASE_URL."""
        if self.url and self.url.startswith(("postgres://", "postgresql://")):
            cm = await AsyncPostgresStore.from_conn_string(
                self.url,
                index={
                    "dims": 768,
                    "embed": init_embeddings(self.embedding_model),
                },
            )
            await cm.setup()
            self.store = await self._exit_stack.enter_async_context(cm)
            return self.store

        # Default: in-memory store
        self.store = InMemoryStore(
            index={
                "dims": 768,
                "embed": init_embeddings(self.embedding_model),
            },
        )
        return self.store

    async def aclose(self):
        """Gracefully close all registered resources."""
        await self._exit_stack.aclose()

    # ------------------------
    # User Long-Term Profile
    # ------------------------
    async def remember_user_fact(self, user_id: str, fact: dict):
        ns = ("users", user_id, "profile")
        fid = str(uuid.uuid4())
        await self.store.aput(ns, fid, fact)
        return fid

    async def recall_user_facts(self, user_id: str, query: str, limit=3):
        ns = ("users", user_id, "profile")
        return await self.store.asearch(ns, query=query, limit=limit)

    async def clear_user_facts(self, user_id: str):
        ns = ("users", user_id, "profile")
        return await self.store.alist(ns, delete_all=True)

    # ------------------------
    # Thread History (decay)
    # ------------------------
    async def save_thread_message(self, thread_id: str, message: dict):
        ns = ("threads", thread_id, "history")
        mid = str(uuid.uuid4())
        value = {
            **message,
            "_created_at": datetime.datetime.utcnow().isoformat(),
        }
        await self.store.aput(ns, mid, value)
        return mid

    async def get_thread_history(self, thread_id: str, limit=50):
        ns = ("threads", thread_id, "history")
        all_items = await self.store.alist(ns, limit=limit)
        return [i for i in all_items if not self._is_expired(i.value)]

    async def clear_thread_history(self, thread_id: str):
        ns = ("threads", thread_id, "history")
        return await self.store.alist(ns, delete_all=True)

    def _is_expired(self, value: dict):
        ts = value.get("_created_at")
        if not ts:
            return False
        created = datetime.datetime.fromisoformat(ts)
        age = (datetime.datetime.utcnow() - created).total_seconds() / 60
        return age > self.decay_minutes

    async def _start_decay_cleaner(self):
        while True:
            try:
                logging.debug("[DECAY] Running cleaner...")
                # TODO: prune expired thread items here
            except Exception as e:
                logging.warning(f"[DECAY] Cleaner failed: {e}")
            await asyncio.sleep(self.decay_minutes * 30)
