"""InMemorySessionStore is a simple in-memory session store for the authentication provider."""

import logging
import time
from datetime import datetime, timedelta
from threading import Lock, Thread
from typing import Any

from pydantic import BaseModel

from zmp_authentication_provider.utils.time_utils import DEFAULT_TIME_ZONE

logger = logging.getLogger(__name__)

class SessionData(BaseModel):
    """SessionData is a model for the session data."""

    user_info: dict[str, Any]
    access_token: str
    refresh_token: str
    id_token: str
    expires_at: datetime | None = None


class InMemorySessionStore:
    """InMemorySessionStore is a simple in-memory session store for the authentication provider."""

    def __init__(self, session_ttl: int = 3600, session_cleanup_interval: int = 300):
        """Initialize the InMemorySessionStore."""
        self.session_store: dict[str, SessionData] = {}
        self.session_ttl = session_ttl
        self.session_cleanup_interval = session_cleanup_interval
        self.session_store_lock = Lock()
        self._running = True
        self.session_cleanup_thread = Thread(target=self.session_cleanup, daemon=True)
        self.session_cleanup_thread.start()

    def get(self, unique_id: str) -> SessionData:
        """Get the session data from the in-memory session store."""
        return self.session_store.get(unique_id)

    def set(self, unique_id: str, session_data: SessionData):
        """Set the session data in the in-memory session store."""
        # delete the session data if it exists
        if self.get(unique_id):
            self.delete(unique_id)

        # set the expires_at
        session_data.expires_at = datetime.now(DEFAULT_TIME_ZONE) + timedelta(seconds=self.session_ttl)

        # set the session data in the in-memory session store
        self.session_store[unique_id] = session_data

    def reset_ttl(self, unique_id: str):
        """Reset the ttl of the session data in the in-memory session store."""
        session_data = self.get(unique_id)
        if session_data:
            session_data.expires_at = datetime.now(DEFAULT_TIME_ZONE) + timedelta(seconds=self.session_ttl)
            self.session_store[unique_id] = session_data
            logger.info(f"Session data for {unique_id} has been reset ttl until {session_data.expires_at}")

    def delete(self, unique_id: str):
        """Delete the session data from the in-memory session store."""
        if self.get(unique_id):
            del self.session_store[unique_id]
        else:
            # skip if the session data is not found in the in-memory session store
            pass

    def session_cleanup(self):
        """Cleanup the session data from the in-memory session store."""
        while self._running:
            with self.session_store_lock:
                for unique_id, session_data in self.session_store.items():
                    if session_data.expires_at and session_data.expires_at < datetime.now(DEFAULT_TIME_ZONE):
                        self.delete(unique_id)
                        logger.info(f"Session data for {unique_id} has expired and has been deleted.")

                logger.info(f"Session cleanup completed. {len(self.session_store)} sessions remaining.")

            time.sleep(self.session_cleanup_interval)

    def close(self):
        """Explicitly clean up resources."""
        self._running = False
        if self.session_cleanup_thread.is_alive():
            self.session_cleanup_thread.join(timeout=5)