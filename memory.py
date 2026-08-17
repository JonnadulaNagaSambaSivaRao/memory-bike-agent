# memory.py

import sqlite3
from datetime import datetime
from typing import List, Dict, Any


# ============================================================
# CONFIGURATION
# ============================================================

DATABASE_FILE = "memory.db"

# Number of recent messages sent to the LLM
MAX_RECENT_MESSAGES = 10

# When conversation reaches this number,
# summarization should happen
MAX_HISTORY_MESSAGES = 20

# Number of messages to keep after summarization
KEEP_MESSAGES_AFTER_SUMMARY = 6


# ============================================================
# MEMORY MANAGER
# ============================================================

class MemoryManager:

    def __init__(
        self,
        database_file: str = DATABASE_FILE
    ):

        self.database_file = database_file

        self._create_tables()

    # ========================================================
    # DATABASE CONNECTION
    # ========================================================

    def _connect(self):

        connection = sqlite3.connect(
            self.database_file
        )

        return connection

    # ========================================================
    # CREATE TABLES
    # ========================================================

    def _create_tables(self):

        connection = self._connect()

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Conversations
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        # ----------------------------------------------------
        # Long-term memories
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'general',
                created_at TEXT NOT NULL
            )
            """
        )

        # ----------------------------------------------------
        # Agent state / conversation summary
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_state (
                id INTEGER PRIMARY KEY,
                summary TEXT DEFAULT ''
            )
            """
        )

        # Create default summary row
        cursor.execute(
            """
            INSERT OR IGNORE INTO agent_state
            (id, summary)
            VALUES (1, '')
            """
        )

        connection.commit()
        connection.close()

    # ========================================================
    # ADD MESSAGE
    # ========================================================

    def add_message(
        self,
        role: str,
        content: str
    ):

        if not content:
            return

        connection = self._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO conversations
            (role, content, created_at)
            VALUES (?, ?, ?)
            """,
            (
                role,
                content,
                datetime.now().isoformat()
            )
        )

        connection.commit()
        connection.close()

    # ========================================================
    # GET RECENT MESSAGES
    # ========================================================

    def get_recent_messages(
        self,
        limit: int = MAX_RECENT_MESSAGES
    ) -> List[Dict[str, Any]]:

        connection = self._connect()

        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT role, content, created_at
            FROM conversations
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )

        rows = cursor.fetchall()

        connection.close()

        # Reverse so oldest → newest
        rows = list(reversed(rows))

        return [
            {
                "role": row["role"],
                "content": row["content"],
                "timestamp": row["created_at"]
            }
            for row in rows
        ]

    # ========================================================
    # GET ALL MESSAGES
    # ========================================================

    def get_all_messages(self):

        connection = self._connect()

        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, role, content, created_at
            FROM conversations
            ORDER BY id ASC
            """
        )

        rows = cursor.fetchall()

        connection.close()

        return [
            dict(row)
            for row in rows
        ]

    # ========================================================
    # GET OLD MESSAGES FOR SUMMARY
    # ========================================================

    def get_messages_for_summary(
        self,
        keep_recent: int = KEEP_MESSAGES_AFTER_SUMMARY
    ):

        connection = self._connect()

        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, role, content, created_at
            FROM conversations
            ORDER BY id ASC
            """
        )

        rows = cursor.fetchall()

        connection.close()

        rows = list(rows)

        if len(rows) <= keep_recent:
            return [
                dict(row)
                for row in rows
            ]

        old_rows = rows[:-keep_recent]

        return [
            dict(row)
            for row in old_rows
        ]

    # ========================================================
    # ADD LONG-TERM MEMORY
    # ========================================================

    def add_long_term_memory(
        self,
        memory: str,
        category: str = "general"
    ):

        if not memory:
            return

        memory = memory.strip()

        if not memory:
            return

        connection = self._connect()

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Exact duplicate check
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM memories
            WHERE LOWER(TRIM(memory)) = LOWER(TRIM(?))
            LIMIT 1
            """,
            (memory,)
        )

        existing = cursor.fetchone()

        if existing:

            connection.close()

            return

        # ----------------------------------------------------
        # Insert memory
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO memories
            (memory, category, created_at)
            VALUES (?, ?, ?)
            """,
            (
                memory,
                category,
                datetime.now().isoformat()
            )
        )

        connection.commit()
        connection.close()

    # ========================================================
    # GET ALL LONG-TERM MEMORIES
    # ========================================================

    def get_all_long_term_memories(self):

        connection = self._connect()

        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, memory, category, created_at
            FROM memories
            ORDER BY id ASC
            """
        )

        rows = cursor.fetchall()

        connection.close()

        return [
            dict(row)
            for row in rows
        ]

    # ========================================================
    # NORMALIZE WORDS
    # ========================================================

    @staticmethod
    def _normalize_text(text: str):

        if not text:
            return []

        text = text.lower()

        # Replace punctuation with spaces
        punctuation = """
        ,.!?;:"'()[]{}<>/
        \\|-_+=*&^%$#@~`
        """

        for character in punctuation:
            text = text.replace(
                character,
                " "
            )

        words = text.split()

        # ----------------------------------------------------
        # Common words that don't help memory matching
        # ----------------------------------------------------

        stop_words = {
            "i",
            "me",
            "my",
            "mine",
            "the",
            "a",
            "an",
            "is",
            "am",
            "are",
            "was",
            "were",
            "be",
            "to",
            "of",
            "for",
            "and",
            "or",
            "in",
            "on",
            "with",
            "this",
            "that",
            "it",
            "want",
            "need",
            "like",
            "looking",
            "lookingfor",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "can",
            "could",
            "would",
            "should",
            "please",
            "very",
            "just",
            "another"
        }

        return [
            word
            for word in words
            if word not in stop_words
        ]

    # ========================================================
    # WORD SIMILARITY
    # ========================================================

    @staticmethod
    def _words_match(
        word1: str,
        word2: str
    ) -> bool:

        if word1 == word2:
            return True

        # Handle simple plural forms
        if word1.endswith("s") and word1[:-1] == word2:
            return True

        if word2.endswith("s") and word2[:-1] == word1:
            return True

        # Handle simple "ing"
        if word1.endswith("ing") and word1[:-3] == word2:
            return True

        if word2.endswith("ing") and word2[:-3] == word1:
            return True

        return False

    # ========================================================
    # SEARCH MEMORIES
    # ========================================================

    def search_memories(
        self,
        query: str
    ):

        if not query:
            return []

        memories = (
            self.get_all_long_term_memories()
        )

        query_words = self._normalize_text(
            query
        )

        if not query_words:
            return []

        results = []

        for item in memories:

            memory_words = self._normalize_text(
                item["memory"]
            )

            score = 0

            # ------------------------------------------------
            # Compare every query word with memory words
            # ------------------------------------------------

            for query_word in query_words:

                for memory_word in memory_words:

                    if self._words_match(
                        query_word,
                        memory_word
                    ):

                        score += 1

                        break

            # ------------------------------------------------
            # Category relevance
            # ------------------------------------------------

            category = (
                item["category"]
                .lower()
            )

            category_words = self._normalize_text(
                category
            )

            for query_word in query_words:

                if query_word in category_words:

                    score += 1

            # ------------------------------------------------
            # Add relevant memory
            # ------------------------------------------------

            if score > 0:

                results.append(
                    {
                        **item,
                        "score": score
                    }
                )

        # Highest relevance first
        results.sort(
            key=lambda x: (
                x["score"],
                x["id"]
            ),
            reverse=True
        )

        return results

    # ========================================================
    # GET RELEVANT MEMORIES
    # ========================================================

    def get_relevant_memories(
        self,
        query: str,
        limit: int = 5
    ):

        results = self.search_memories(
            query
        )

        return [
            item["memory"]
            for item in results[:limit]
        ]

    # ========================================================
    # GET ALL MEMORIES FOR CONTEXT
    # ========================================================

    def get_memory_context(
        self,
        query: str,
        limit: int = 5
    ):

        results = self.search_memories(
            query
        )

        return results[:limit]

    # ========================================================
    # SET SUMMARY
    # ========================================================

    def set_summary(
        self,
        summary: str
    ):

        connection = self._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE agent_state
            SET summary = ?
            WHERE id = 1
            """,
            (summary,)
        )

        connection.commit()
        connection.close()

    # ========================================================
    # GET SUMMARY
    # ========================================================

    def get_summary(self):

        connection = self._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT summary
            FROM agent_state
            WHERE id = 1
            """
        )

        row = cursor.fetchone()

        connection.close()

        if row:
            return row[0] or ""

        return ""

    # ========================================================
    # CHECK SUMMARIZATION
    # ========================================================

    def needs_summarization(self):

        connection = self._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM conversations
            """
        )

        count = cursor.fetchone()[0]

        connection.close()

        return count >= MAX_HISTORY_MESSAGES

    # ========================================================
    # GET CONVERSATION COUNT
    # ========================================================

    def get_conversation_count(self):

        connection = self._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM conversations
            """
        )

        count = cursor.fetchone()[0]

        connection.close()

        return count

    # ========================================================
    # KEEP RECENT MESSAGES
    # ========================================================

    def keep_recent_messages(
        self,
        limit: int = KEEP_MESSAGES_AFTER_SUMMARY
    ):

        connection = self._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM conversations
            WHERE id NOT IN (
                SELECT id
                FROM conversations
                ORDER BY id DESC
                LIMIT ?
            )
            """,
            (limit,)
        )

        connection.commit()
        connection.close()

    # ========================================================
    # CLEAR LONG-TERM MEMORY
    # ========================================================

    def clear_long_term_memory(self):

        connection = self._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM memories
            """
        )

        connection.commit()
        connection.close()

    # ========================================================
    # CLEAR CONVERSATIONS
    # ========================================================

    def clear_conversations(self):

        connection = self._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM conversations
            """
        )

        cursor.execute(
            """
            UPDATE agent_state
            SET summary = ''
            WHERE id = 1
            """
        )

        connection.commit()
        connection.close()

    # ========================================================
    # SHOW MEMORY
    # ========================================================

    def show_memory(self):

        print("\n" + "=" * 60)
        print("LONG-TERM MEMORY")
        print("=" * 60)

        memories = (
            self.get_all_long_term_memories()
        )

        if not memories:

            print("No long-term memories stored.")

        else:

            for item in memories:

                print(
                    f"\n{item['id']}. "
                    f"{item['memory']}"
                )

                print(
                    f"   Category: "
                    f"{item['category']}"
                )

                print(
                    f"   Created: "
                    f"{item['created_at']}"
                )

        print("\n" + "=" * 60)
        print("CONVERSATION SUMMARY")
        print("=" * 60)

        summary = self.get_summary()

        print(
            summary
            if summary
            else "No summary available."
        )

        print("\n" + "=" * 60)
        print("RECENT CONVERSATION")
        print("=" * 60)

        messages = self.get_recent_messages()

        if not messages:

            print("No conversation messages.")

        else:

            for message in messages:

                print(
                    f"{message['role'].upper()}: "
                    f"{message['content']}"
                )

        print("=" * 60)

    # ========================================================
    # GET COMPLETE CONTEXT
    # ========================================================

    def get_context(
        self,
        current_request: str
    ):

        return {
            "summary":
                self.get_summary(),

            "recent_messages":
                self.get_recent_messages(
                    MAX_RECENT_MESSAGES
                ),

            "relevant_memories":
                self.get_relevant_memories(
                    current_request,
                    limit=5
                )
        }