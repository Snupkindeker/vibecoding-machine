import os

import openai
from github import *
from httpx import Client

from dotenv import load_dotenv
from os import getenv


load_dotenv()
github_key = getenv("GITHUB_PAT")
ai_key = getenv("AI_API_KEY")
ai_endpoint = getenv("AI_API_ENDPOINT")

proxy_url = "http://202.28.194.139:31280"
http_client = Client(proxy=proxy_url, timeout=30.0)

ai_client = openai.OpenAI(
    base_url=ai_endpoint,
    api_key=ai_key,
    http_client=http_client
)

def run_cycle():
    pass