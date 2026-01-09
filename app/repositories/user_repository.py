import psycopg2
from ..db import get_connection


def create_user(email: str):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute(
		"""
		INSERT INTO users (email)
		VALUES (%s)
		ON CONFLICT (email) DO NOTHING
		RETURNING id;
		""",
		(email,)
	)

	user_id = cur.fetchone()
	conn.commit()
	cur.close()
	conn.close()

	return user_id[0] if user_id else None
