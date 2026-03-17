import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd

from utils.data_loader import load_data
from utils.agent_handler import get_llm, get_agent, query_agent

# Load environment variables
load_dotenv()

# Page configuration - must be the first Streamlit command
st.set_page_config(
    page_title="Chat with Your Data",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f1f8e9;
    }
    .success-text {
        color: #2e7d32;
        font-weight: 500;
    }
    .error-text {
        color: #c62828;
        font-weight: 500;
    }
    .info-box {
        background-color: #e8eaf6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for settings and file upload
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("⚙️ Settings")
    st.markdown("---")

    # API Key input (optional, can also be set in .env)
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("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", ""),
        help="Enter your OpenAI API key. It will not be stored."
    )

    if not api_key:
        st.warning("Please enter your OpenAI API key to proceed.")
        st.info("Get your key from [OpenAI Platform](https://platform.openai.com/api-keys)")

    st.markdown("---")

    # File uploader
    uploaded_file = st.file_uploader(
        "📂 Upload your data file",
        type=["csv", "xlsx", "xls"],
        help="Upload a CSV or Excel file to start chatting with your data."
    )

    # Example datasets (optional)
    st.markdown("---")
    st.markdown("### 📋 Need an example?")
    if st.button("Load sample sales data"):
        # Create a small sample dataframe
        sample_df = pd.DataFrame({
            'Date': pd.date_range(start='2024-01-01', periods=100, freq='D'),
            'Product': ['A', 'B', 'C', 'D'] * 25,
            'Sales': np.random.randint(10, 100, 100),
            'Region': ['North', 'South', 'East', 'West'] * 25
        })
        st.session_state['df'] = sample_df
        st.session_state['data_loaded'] = True
        st.rerun()

    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state['messages'] = []
        st.rerun()

# Main content area
st.title("📄 Chat with Your Data")
st.markdown("Upload a CSV or Excel file and ask questions about your data in plain English. The AI will analyze it and give you answers instantly.")

# Initialize session state for chat history and data
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if 'df' not in st.session_state:
    st.session_state['df'] = None

if 'data_loaded' not in st.session_state:
    st.session_state['data_loaded'] = False

# Handle file upload or sample data
if uploaded_file is not None:
    # Load data from uploaded file
    df, message = load_data(uploaded_file)
    if df is not None:
        st.session_state['df'] = df
        st.session_state['data_loaded'] = True
        st.sidebar.success(message)
    else:
        st.sidebar.error(message)
        st.session_state['data_loaded'] = False

# Display data preview if loaded
if st.session_state['data_loaded'] and st.session_state['df'] is not None:
    df = st.session_state['df']

    with st.expander("🔍 Data Preview", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rows", df.shape[0])
            st.metric("Columns", df.shape[1])
        with col2:
            st.dataframe(df.head(10), use_container_width=True)

    # Check for API key
    if not api_key:
        st.warning("⚠️ Please provide your OpenAI API key in the sidebar to start chatting.")
    else:
        # Initialize LLM and agent
        llm = get_llm(api_key)
        agent = get_agent(llm, df)

        # Chat interface
        st.markdown("---")
        st.subheader("💬 Chat with your data")

        # Display chat history
        for message in st.session_state['messages']:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask a question about your data..."):
            # Add user message to chat history
            st.session_state['messages'].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get agent response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing your data..."):
                    answer, error = query_agent(agent, prompt)
                    if error:
                        st.error(error)
                        st.session_state['messages'].append({"role": "assistant", "content": f"Error: {error}"})
                    else:
                        st.markdown(answer)
                        st.session_state['messages'].append({"role": "assistant", "content": answer})

else:
    # No data loaded: show friendly welcome message
    st.info("👋 Welcome! Please upload a CSV or Excel file in the sidebar to get started.")
    st.markdown("""
    <div class="info-box">
        <h4>✨ What can I do?</h4>
        <ul>
            <li>Answer questions like "What was the total sales last month?"</li>
            <li>Find trends: "Which product sold the most in the North region?"</li>
            <li>Perform calculations: "What's the average order value?"</li>
            <li>And much more!</li>
        </ul>
        <p>Simply upload your file and start asking.</p>
    </div>
    """, unsafe_allow_html=True)

    # Example questions as suggestions
    st.markdown("### 🔍 Example Questions")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.code("Show me the top 5 rows")
    with col2:
        st.code("What is the sum of sales?")
    with col3:
        st.code("Group by region and calculate average")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Built with ❤️ using Streamlit and LangChain</p>",
    unsafe_allow_html=True
  )
