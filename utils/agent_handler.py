import streamlit as st
from langchain.agents import create_pandas_dataframe_agent
from langchain.llms import OpenAI
import os

# Cache the LLM and agent to avoid re-initialization on each interaction
@st.cache_resource
def get_llm(api_key):
    """Initialize the OpenAI LLM with a low temperature for deterministic answers."""
    return OpenAI(temperature=0, openai_api_key=api_key, model_name="gpt-3.5-turbo-instruct")

@st.cache_resource
def get_agent(_llm, df):
    """Create a pandas dataframe agent."""
    # The agent uses the LLM and the dataframe to answer questions
    return create_pandas_dataframe_agent(_llm, df, verbose=True, allow_dangerous_code=True)

def query_agent(agent, question):
    """
    Send a question to the agent and return the answer.
    Handles errors gracefully.
    """
    try:
        answer = agent.run(question)
        return answer, None
    except Exception as e:
        return None, f"Error processing question: {str(e)}"
