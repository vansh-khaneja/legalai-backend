import psycopg2
from ..db import get_connection


def create_user(email: str, user_id: str):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute(
		"""
		INSERT INTO users (id, email)
		VALUES (%s, %s)
		ON CONFLICT (email) DO NOTHING
		RETURNING id;
		""",
		(user_id, email)
	)

	result = cur.fetchone()
	conn.commit()
	cur.close()
	conn.close()

	if result:
		return str(result[0])  # Convert UUID to string
	else:
		# User already exists, get their ID
		return get_user_by_email(email)["id"] if get_user_by_email(email) else None


def get_user_by_email(email: str):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute(
		"""
		SELECT id, email FROM users WHERE email = %s;
		""",
		(email,)
	)

	user = cur.fetchone()
	cur.close()
	conn.close()

	return {"id": str(user[0]), "email": user[1]} if user else None


def is_user_premium(user_id: str):
	conn = get_connection()
	cur = conn.cursor()

	cur.execute(
		"""
		SELECT premium FROM users WHERE id = %s;
		""",
		(user_id,)
	)

	result = cur.fetchone()
	cur.close()
	conn.close()

	return result[0] if result else False
