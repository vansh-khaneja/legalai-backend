from ..db import get_connection


def create_chat(user_id):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute(
		"""
		INSERT INTO chats (user_id)
		VALUES (%s)
		RETURNING id;
		""",
		(user_id,)
	)

	result = cur.fetchone()
	conn.commit()
	cur.close()
	conn.close()

	return str(result[0]) if result else None


def get_user_chats(user_id):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute(
		"""
		SELECT id, created_at
		FROM chats
		WHERE user_id = %s
		ORDER BY created_at DESC;
		""",
		(user_id,)
	)

	chats = cur.fetchall()
	cur.close()
	conn.close()

	return [{"id": str(chat[0]), "created_at": str(chat[1])} for chat in chats]
