from ..db import get_connection


def add_message(chat_id, role, content):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute(
		"""
		INSERT INTO messages (chat_id, role, content)
		VALUES (%s, %s, %s);
		""",
		(chat_id, role, content)
	)

	conn.commit()
	cur.close()
	conn.close()


def get_last_messages(chat_id, limit=5):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute(
		"""
		SELECT role, content
		FROM messages
		WHERE chat_id = %s
		ORDER BY created_at DESC
		LIMIT %s;
		""",
		(chat_id, limit)
	)

	rows = cur.fetchall()
	cur.close()
	conn.close()

	return rows[::-1]
