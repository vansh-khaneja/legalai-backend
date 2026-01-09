import os
import sys

# Ensure project root is on sys.path so we can import `app.*` while running from app/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.db import get_connection
from app.repositories.user_repository import create_user
from app.repositories.chat_repository import create_chat
from app.repositories.message_repository import add_message, get_last_messages


def main():
	email = "testuser@example.com"
	print(f"➡️  Adding user: {email}")

	user_id = create_user(email)
	if user_id:
		print(f"✅ Created new user id: {user_id}")
	else:
		# If user already exists, fetch the existing id
		conn = get_connection()
		cur = conn.cursor()
		cur.execute("SELECT id FROM users WHERE email = %s;", (email,))
		row = cur.fetchone()
		cur.close()
		conn.close()
		if row:
			user_id = row[0]
			print(f"ℹ️  User already exists. id: {user_id}")
		else:
			print("❌ Failed to create or find user.")
			return

	# Create a chat for this user
	print("➡️  Creating chat for user")
	chat_id = create_chat(user_id)
	print(f"✅ chat_id: {chat_id}")

	# Insert a pair of messages: human + AI
	print("➡️  Inserting messages (human + AI)")
	add_message(chat_id, "user", "Hello, I need help with a case.")
	add_message(chat_id, "assistant", "Sure — can you share more details?")

	# Fetch and print last messages
	print("➡️  Fetching last messages")
	msgs = get_last_messages(chat_id, limit=5)
	print("✅ Chat history (oldest → newest):")
	for i, (role, content) in enumerate(msgs, start=1):
		print(f"{i}. {role}: {content}")


if __name__ == "__main__":
	main()
