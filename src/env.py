import os
from dotenv import load_dotenv

ENV = os.getenv("ENV", "LOCAL")

if ENV == "LOCAL":
    load_dotenv(".env.local")
else:
    load_dotenv()
