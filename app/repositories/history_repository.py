import json

from asyncpg import Pool

from app.sql import (
    INSERT_HISTORY_LOG,
    INSERT_HISTORY_CITATION,
    GET_HISTORY_WITH_CITATIONS,
)


class HistoryRepository:
    """
    Repository responsible for storing and retrieving
    conversation history.
    """

    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def save_conversation(
        self,
        session_id: str,
        question: str,
        answer: str,
        citations: list[dict],
    ) -> str:
        """
        Save conversation along with citations.
        """

        print("\n" + "=" * 80)
        print("SAVE CONVERSATION")
        print("=" * 80)
        print(f"Session ID : {session_id}")
        print(f"Question   : {question}")
        print(f"Answer     : {answer}")
        print(f"Total Citations : {len(citations)}")

        async with self.pool.acquire() as conn:

            async with conn.transaction():

                history_id = await conn.fetchval(
                    INSERT_HISTORY_LOG,
                    session_id,
                    question,
                    answer,
                    len(citations),
                )

                print(f"\nHistory ID : {history_id}")

                for index, chunk in enumerate(citations, start=1):

                    print("\n" + "-" * 80)
                    print(f"CITATION {index}")
                    print("-" * 80)

                    print(
                        json.dumps(
                            chunk,
                            indent=4,
                            default=str,
                        )
                    )

                    await conn.execute(
                        INSERT_HISTORY_CITATION,
                        history_id,
                        chunk["document_id"],
                        chunk["pdf_name"],
                        chunk["chunk_number"],
                        chunk["page_number"],
                        chunk["line_start"],
                        chunk["line_end"],
                        float(chunk.get("similarity", 0.0)),
                        chunk["chunk_text"],
                    )

                print("\nConversation saved successfully.")
                print("=" * 80 + "\n")

                return str(history_id)

    async def get_session_history(
        self,
        session_id: str,
    ) -> list[dict]:
        """
        Fetch complete conversation history.
        """

        async with self.pool.acquire() as conn:

            records = await conn.fetch(
                GET_HISTORY_WITH_CITATIONS,
                session_id,
            )

        history = []

        print("\n" + "=" * 80)
        print("FETCH HISTORY")
        print("=" * 80)

        for record in records:

            row = dict(record)

            if isinstance(row["citations"], str):
                row["citations"] = json.loads(
                    row["citations"]
                )

            print(
                json.dumps(
                    row,
                    indent=4,
                    default=str,
                )
            )

            history.append(row)

        print("=" * 80 + "\n")

        return history