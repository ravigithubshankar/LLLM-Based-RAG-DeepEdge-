from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from groq import Groq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_core.language_models import BaseLLM
from langchain.schema import LLMResult, Generation
from groq import Groq  # This is the correct import
from typing import Optional, List, Any, Dict
# Load environment variables
load_dotenv()

app = Flask(__name__)

# Set environment variables
#SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
#GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SEARCH_API_KEY=b3480786b4014dcc81fbfe8f4e8d7bf7316174b9ab6bf89ce4bfd01937261a11
GROQ_API_KEY=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
FLASK_SECRET_KEY=16428fedb8c656d945426a06536a67b9f9526612938e4f163d893a72c9217e1a




# Verify API keys
if not SEARCH_API_KEY:
    print("Error: SEARCH_API_KEY is not set.")
if not GROQ_API_KEY:
    print("Error: GROQ_API_KEY is not set.")
    
    

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    user_query = data.get("query")
    history = data.get("history", [])

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        articles = search_and_scrape(user_query)
        if not articles:
            return jsonify({"error": "No relevant articles found"}), 404

        concatenated_content = " ".join(articles)
        answer = generate_response(user_query, concatenated_content, history)
        
        return jsonify({"answer": str(answer).strip()})

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
        
        



# Custom Groq LLM class 
class GroqLLM(BaseLLM):
    model: str = "llama3-70b-8192"
    client: Any = None
    temperature: float = 0.7
    max_tokens: int = 1024

    def __init__(self, api_key: str):
        super().__init__()
        self.client = Groq(api_key=api_key)

    def _generate(self, prompts: List[str], **kwargs) -> LLMResult:
        try:
            responses = []
            for prompt in prompts:
                response = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model,
                    temperature=kwargs.get("temperature", self.temperature),
                    max_tokens=kwargs.get("max_tokens", self.max_tokens)
                )
                responses.append(response.choices[0].message.content)
            return LLMResult(generations=[[Generation(text=text)] for text in responses])
        except Exception as e:
            return LLMResult(generations=[[Generation(text=f"Error: {str(e)}")]])

    async def _agenerate(self, prompts: List[str], **kwargs) -> LLMResult:
        return self._generate(prompts, **kwargs)

    @property
    def _llm_type(self) -> str:
        return "groq"

# Initialize Groq LLM
llm = GroqLLM(api_key=GROQ_API_KEY)

# Set up LangChain memory
memory = ConversationBufferMemory(input_key="query", memory_key="history")

# Define PromptTemplate
prompt_template = PromptTemplate(
    input_variables=["query", "context", "history"],
    template="""You are a helpful AI assistant. Use the following information to answer the question.

Previous Conversation:
{history}

Relevant Context:
{context}

Question: {query}

Answer in a clear and concise manner:
"""
)

# Initialize the chain
chain = LLMChain(
    llm=llm,
    prompt=prompt_template,
    memory=memory,
    verbose=True
)


def search_and_scrape(query):
    """
    Search the web for articles related to the query and scrape their content.
    Returns a list of article texts (headings and paragraphs).
    """
    search_url = "https://serpapi.com/search"
    params = {"q": query, "api_key": SEARCH_API_KEY}

    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        urls = [result.get("link") for result in data.get("organic_results", [])[:3]]
        articles = []

        for url in urls:
            content = scrape_content(url)
            if content:
                articles.append(content)

        return articles

    except requests.RequestException as e:
        print(f"Error searching with SerpAPI: {e}")
        return []
    except ValueError as e:
        print(f"Error parsing SerpAPI response: {e}")
        return []
        
        

def scrape_content(url):
    """
    Scrape headings and paragraphs from a given URL.
    Returns cleaned text content.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        if 'dictionary.cambridge.org' in url:
            return ""
        
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        if 'text/html' not in response.headers.get('content-type', ''):
            return ""

        soup = BeautifulSoup(response.text, 'html.parser')
        content = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
            text = tag.get_text(strip=True)
            if text and len(text) > 10:
                content.append(text)

        return " ".join(content)[:4000] if content else ""

    except (requests.RequestException, ValueError) as e:
        print(f"Error scraping {url}: {e}")
        return ""
        
        
def generate_response(query, context, history):
    """
    Generate an answer using the LLM, incorporating context and conversational history.
    
    Args:
        query: The user's current question/input.
        context: Relevant context for answering the query.
        history: Previous conversation history (either as a string or a list of messages).
    
    Returns:
        str: The generated response.
    """
    try:
        # Prepare inputs for the chain
        inputs = {
            "query": query,
            "context": context[:2000] if context else "",
            "history": memory.load_memory_variables({}).get("history", "")  # Load from memory
        }

        # Generate response
        result = chain.run(**inputs)

        # Handle output
        if isinstance(result, dict):
            return result.get("text", "").strip() or str(result).strip()
        return str(result).strip()

    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "I encountered an error while generating a response. Please try again."





if __name__ == '__main__':
    try:
        app.run(host='localhost', port=7000)
    except Exception as e:
        print(f"Error starting the application: {e}")
