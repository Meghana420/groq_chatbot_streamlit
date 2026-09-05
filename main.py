import os
import warnings

from groq import NotFoundError, RateLimitError
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

# Suppress deprecation warnings for a clean user interface
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

load_dotenv()
#load environment variables from .env file


def get_setting(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value:
        return value

    try:
        return st.secrets.get(name, default)
    except FileNotFoundError:
        return default


@tool
def calculator(a: float, b: float) -> str:
    """Useful for performing basic arithmetic calculations with numbers."""
    return f"The sum of {a} and {b} is {a + b}"

@tool
def say_hello(name: str) -> str:
    """Useful for greeting a user."""
    return f"Hello {name}, I hope you are well today"


@st.cache_resource
def create_agent():
    groq_key = get_setting("GROQ_API_KEY")
    model_name = get_setting("GROQ_MODEL", "llama-3.1-8b-instant")

    if not groq_key:
        return None

    model = ChatGroq(api_key=groq_key, model=model_name, temperature=0)
    return create_react_agent(model, [calculator, say_hello])


def main():
    st.set_page_config(page_title="Groq Chatbot", page_icon="💬")
    st.title("Groq Chatbot")
    st.caption("Ask a question, request a calculation, or say hello.")

    if "show_tools" not in st.session_state:
        st.session_state.show_tools = False

    if st.button("+ Tools"):
        st.session_state.show_tools = not st.session_state.show_tools

    if st.session_state.show_tools:
        st.info("Available tools")

        with st.form("calculator_form"):
            st.write("Calculator")
            first_number = st.number_input("First number", key="first_number")
            second_number = st.number_input("Second number", key="second_number")
            calculate = st.form_submit_button("Calculate")

            if calculate:
                st.success(calculator.invoke({"a": first_number, "b": second_number}))

        with st.form("greeting_form"):
            st.write("Greeting")
            name = st.text_input("Name", key="greeting_name")
            greet = st.form_submit_button("Greet")

            if greet:
                if name.strip():
                    st.success(say_hello.invoke({"name": name}))
                else:
                    st.warning("Please enter a name.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask me anything...")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    agent = create_agent()
    if agent is None:
        st.error("GROQ_API_KEY is missing. Add it to .env locally or Streamlit secrets when hosted.")
        return

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = agent.invoke({"messages": [HumanMessage(content=prompt)]})
                answer = response["messages"][-1].content
            except RateLimitError:
                fallback_model = "openai/gpt-oss-20b"
                configured_model = get_setting("GROQ_MODEL", fallback_model)
                if configured_model == fallback_model:
                    st.error(
                        "Groq rate limit reached. Please wait for the quota to "
                        "reset or use an API key with available quota."
                    )
                else:
                    try:
                        fallback = ChatGroq(
                            api_key=get_setting("GROQ_API_KEY"),
                            model=fallback_model,
                            temperature=0,
                        )
                        fallback_agent = create_react_agent(
                            fallback, [calculator, say_hello]
                        )
                        response = fallback_agent.invoke(
                            {"messages": [HumanMessage(content=prompt)]}
                        )
                        answer = response["messages"][-1].content
                    except (NotFoundError, RateLimitError):
                        st.error(
                            "The configured Groq model is unavailable or rate-limited. "
                            "Set GROQ_MODEL to an active model and use an API key "
                            "with available quota."
                        )
            except NotFoundError:
                st.error(
                    "The GROQ_MODEL is unavailable. Set it to an active Groq model "
                    "such as openai/gpt-oss-20b."
                )
            except Exception:
                st.error(
                    "The chatbot could not contact Groq. Check GROQ_API_KEY and "
                    "GROQ_MODEL, then try again."
                )
            else:
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )


if __name__ == "__main__":
    main()