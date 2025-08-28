import os
from dotenv import load_dotenv
from s2s import SofIAClient

load_dotenv()

client = None

def get_sofia_client():
    global client
    if client is None:
        client = SofIAClient(
            api_key=os.getenv("OPENAI_API_KEY"),
            initial_prompt=os.getenv("INITIAL_PROMPT", ""),
            include_date=os.getenv("INCLUDE_DATE", "True").lower() in ("true", "1", "yes"),
            include_time=os.getenv("INCLUDE_TIME", "True").lower() in ("true", "1", "yes"),
            mode="realtime",
            function_calling=os.getenv("FUNCTION_CALLING", "False").lower() in ("true", "1", "yes"),
            voice=os.getenv("VOICE", "echo")
        )
    return client
