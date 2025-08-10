import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not OPENAI_API_KEY or not ANTHROPIC_API_KEY or not GOOGLE_API_KEY:
    raise EnvironmentError("Please set OPENAI_API_KEY, ANTHROPIC_API_KEY, and GOOGLE_API_KEY in your .env file.")

anthropic_llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0)
openai_llm = ChatOpenAI(model="gpt-4", temperature=0)
gemini_llm = GoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY)
serper = GoogleSerperAPIWrapper()

