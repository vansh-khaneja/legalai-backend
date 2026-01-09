import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

def get_connection():
	url = os.getenv("DATABASE_URL")
	if not url:
		raise ValueError("DATABASE_URL not set")
	return psycopg2.connect(url)
