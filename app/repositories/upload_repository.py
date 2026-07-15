from asyncpg import Pool
from app.sql import INSERT_DOCUMENT

class UploadRepository:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def create_document(self, pdf_name: str) -> dict:
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(INSERT_DOCUMENT, pdf_name)
            return dict(record) if record else {}