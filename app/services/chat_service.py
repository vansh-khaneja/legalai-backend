from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

class ChatService:
    def __init__(self):
        self.client = OpenAI()

    def generate_response(self, query: str, context: str) -> str:
        # Generate a response based on the query and context using OpenAI's model.
        prompt = f"Context: {context}\n\nQuery: {query}\n\nResponse:"
        response = self.client.responses.create(
            model="gpt-5-nano",
            input=prompt
        )
        return response.output_text
