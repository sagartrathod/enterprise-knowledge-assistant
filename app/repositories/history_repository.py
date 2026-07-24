# app/repositories/history_repository.py

from __future__ import annotations

import json

from asyncpg import Pool

from app.sql import (
    GET_HISTORY_WITH_CITATIONS,
    INSERT_HISTORY_CITATION,
    INSERT_HISTORY_LOG,
)


class HistoryRepository:
    """
    Repository responsible for storing and retrieving
    conversation history.
    """

    def __init__(
        self,
        db_pool: Pool,
    ) -> None:
        self.pool = db_pool

    async def save_conversation(
        self,
        session_id: str,
        question: str,
        answer: str,
        citations: list[dict],
    ) -> str:
        """
        Save a conversation along with all retrieved citations.
        """

        print("\n" + "=" * 80)
        print("SAVE CONVERSATION")
        print("=" * 80)
        print(f"Session ID       : {session_id}")
        print(f"Question         : {question}")
        print(f"Answer           : {answer}")
        print(f"Total Citations  : {len(citations)}")

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
                        chunk["page_start"],
                        chunk["page_end"],
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
        document_id: str,
    ) -> list[dict]:
        """
        Retrieve conversation history only for the selected document.

        Args:
            session_id:
                Current chat session.

            document_id:
                Currently selected PDF/document.

        Returns:
            List of conversation history records with citations.
        """

        print("\n" + "=" * 80)
        print("FETCH HISTORY")
        print("=" * 80)
        print(f"Session ID  : {session_id}")
        print(f"Document ID : {document_id}")
        print("=" * 80)

        async with self.pool.acquire() as conn:

            records = await conn.fetch(
                GET_HISTORY_WITH_CITATIONS,
                session_id,
                document_id,
            )

        history: list[dict] = []

        for index, record in enumerate(records, start=1):

            row = dict(record)

            if isinstance(row.get("citations"), str):
                row["citations"] = json.loads(
                    row["citations"]
                )

            print(f"\nConversation {index}")
            print("-" * 80)
            print(
                json.dumps(
                    row,
                    indent=4,
                    default=str,
                )
            )

            history.append(row)

        print("\nTotal Conversations :", len(history))
        print("=" * 80 + "\n")

        return history