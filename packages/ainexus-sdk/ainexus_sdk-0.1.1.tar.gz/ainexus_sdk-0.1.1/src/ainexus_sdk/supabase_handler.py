import os
import asyncio
from supabase import create_client, Client, acreate_client, AsyncClient


class SupabaseHandler:
    def __init__(self, url: str = None, key: str = None):
        self.url = url or os.environ.get("SUPABASE_URL")
        self.key = key or os.environ.get("SUPABASE_KEY")
        self._sync_client: Client | None = None
        self._async_client: AsyncClient | None = None

    def get_sync_client(self) -> Client:
        """Get a synchronous Supabase client"""
        if not self._sync_client:
            self._sync_client = create_client(self.url, self.key)
        return self._sync_client

    async def get_async_client(self) -> AsyncClient:
        """Get an asynchronous Supabase client"""
        if not self._async_client:
            self._async_client = await acreate_client(self.url, self.key)
        return self._async_client

