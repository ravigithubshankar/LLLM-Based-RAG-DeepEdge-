LLM-Based RAG System
Overview
This project builds a Retrieval-Augmented Generation (RAG) system using a Large Language Model (LLM). It integrates web scraping via an API, serves LLM-generated answers through an API, and provides a Streamlit frontend for user interaction. Use only packages from requirements.txt (or similar alternatives for the same functionality).
Process Overview

User Input: Enter a query via the Streamlit frontend.
Query to Backend: The query is sent to a Flask backend via an API call.
Search and Scrape: The backend searches the web using an API, retrieves top articles, and scrapes headings and paragraphs.
Content Processing: Scraped content is processed into coherent input for the LLM.
LLM Response: The LLM generates a contextual answer using the query and processed content, returned via the backend.
Display Response: The answer is sent to the Streamlit frontend and displayed.

Expectations
Demonstrate your ability to work with the provided tools and deliver a solution meeting the requirements.Bonus: Use LangChain (or similar) to add conversational memory to the chatbot.
Prerequisites

Python 3.8+

Setup Instructions

Clone the Repository:git clone https://github.com/your-repo-url.git
cd rag-system-chatbot


Set Up Virtual Environment:
Using venv:python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate


Using conda:conda create --name rag_env python=3.8
conda activate rag_env




Install Requirements:pip install -r requirements.txt


Set Up Environment Variables:Create a .env file in the root directory with your API keys:SEARCH_API_KEY=your_serpapi_key
GROQ_API_KEY=your_groq_api_key


Run Flask Backend:cd flask_app
python app.py

Runs on http://localhost:7000.
Run Streamlit Frontend:cd streamlit_app
streamlit run app.py

Runs on http://localhost:8501.
Open the Application:Visit http://localhost:8501 to interact with the system.

Project Structure

flask_app/: Backend Flask API and utilities.
streamlit_app/: Streamlit frontend code.
.env: API keys (exclude from version control).
requirements.txt: Project dependencies.

Task Instructions

Implement functionality to fetch, process, and generate LLM responses using the provided APIs.
Integrate APIs with the Flask backend.
Display results in the Streamlit frontend.


