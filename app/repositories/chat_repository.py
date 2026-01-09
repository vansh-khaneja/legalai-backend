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

	chat_id = cur.fetchone()[0]
	conn.commit()
	cur.close()
	conn.close()

	return chat_id
