import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def init_db():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not set")

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email TEXT UNIQUE,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    # CHATS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE
    );
    """)

    # MESSAGES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        chat_id UUID NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
        content TEXT NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        FOREIGN KEY (chat_id)
            REFERENCES chats(id)
            ON DELETE CASCADE
    );
    """)

    # INDEXES
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_chats_user_id
        ON chats(user_id);
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_messages_chat_id
        ON messages(chat_id);
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Database initialized successfully")


if __name__ == "__main__":
    init_db()
