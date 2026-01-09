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


def get_chat_messages(chat_id, limit=None, offset=None):
	conn = get_connection()
	cur = conn.cursor()

	query = """
		SELECT role, content, created_at
		FROM messages
		WHERE chat_id = %s
		ORDER BY created_at DESC
	"""
	params = [chat_id]

	if limit is not None:
		query += " LIMIT %s"
		params.append(limit)

	if offset is not None:
		query += " OFFSET %s"
		params.append(offset)

	query += ";"

	cur.execute(query, params)

	messages = cur.fetchall()
	cur.close()
	conn.close()

	# Reverse to show oldest first in the response (chronological order)
	return [
		{
			"role": msg[0],
			"content": msg[1],
			"created_at": str(msg[2])
		}
		for msg in messages
	][::-1]


