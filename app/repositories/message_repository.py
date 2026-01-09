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


