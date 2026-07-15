from asyncpg import Pool
from app.sql import GET_ALL_DOCUMENTS, DELETE_DOCUMENT_BY_ID

class DocumentRepository:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def get_all(self) -> list[dict]:
        async with self.pool.acquire() as conn:
            records = await conn.fetch(GET_ALL_DOCUMENTS)
            return [dict(r) for r in records]

    async def delete_by_id(self, document_id: str) -> bool:
        async with self.pool.acquire() as conn:
            # ON DELETE CASCADE handles chunk and citation cleanup automatically
            result = await conn.execute(DELETE_DOCUMENT_BY_ID, document_id)
            return result == "DELETE 1"