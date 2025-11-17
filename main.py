import os
import asyncio
import uuid
import streamlit as st
from google.genai import types
from dotenv import load_dotenv  # Import the dotenv library

# --- ADK Imports ---
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search

# --- Load .env file ---
# This line loads the variables from your .env file into the environment
load_dotenv()

# --- 1. App Title and Setup ---
st.set_page_config(page_title="AI Learning Assistant", page_icon="🎓")
st.title("🎓 AI Learning Assistant")
st.write("This agent uses a 3-step workflow (Research, Summarize, Quiz) to help you learn any topic.")

# --- 2. Get API Key from .env file ---
# We now get the key directly from the environment variables
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    st.warning("Could not find GOOGLE_API_KEY in your .env file. Please make sure it's set.")
    st.stop()

# Set the API key for the ADK (this is now slightly redundant but doesn't hurt)
# The ADK itself will also pick it up from the environment
os.environ["GOOGLE_API_KEY"] = api_key
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"


# --- 3. Define All Agent Logic (in helper functions) ---

@st.cache_resource
def get_root_agent():
    """
    Creates and returns the complete, configured SequentialAgent.
    We use @st.cache_resource to build this complex object only ONCE.
    """

    # Model Retry Configuration
    retry_config = types.HttpRetryOptions(
        attempts=5, exp_base=7, initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )

    # Agent 1: The Researcher
    research_agent = LlmAgent(
        name="ResearchAgent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="Find the 3 most relevant and authoritative sources for the user's topic. Present findings as snippets and source URLs.",
        tools=[google_search],
        output_key="research_findings",
    )

    # Agent 2: The Summarizer
    summarizer_agent = LlmAgent(
        name="SummarizerAgent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""Read the provided {research_findings} and synthesize them into a concise, easy-to-understand study guide.
        Format with an introduction, 3-5 key bullet points, and a conclusion.""",
        tools=[],
        output_key="study_guide",
    )

    # Agent 3: The Quiz Master
    quiz_agent = LlmAgent(
        name="QuizAgent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""Based on the {study_guide}, create a 3-question multiple-choice quiz to test knowledge.
        Provide questions, options (A, B, C, D), and clearly mark the correct answer.""",
        tools=[],
        output_key="final_quiz",
    )

    # The Root Workflow Agent
    root_agent = SequentialAgent(
        name="LearningAssistantWorkflow",
        sub_agents=[research_agent, summarizer_agent, quiz_agent],
    )

    print("--- AGENT WORKFLOW CREATED (cached) ---")
    return root_agent


@st.cache_resource
def get_runner():
    """
    Creates and returns the ADK Runner and SessionService.
    We use @st.cache_resource to create these objects only ONCE.
    """
    session_service = InMemorySessionService()
    runner = Runner(
        agent=get_root_agent(),
        app_name="LearningAssistantApp",
        session_service=session_service
    )
    print("--- RUNNER AND SESSION SERVICE CREATED (cached) ---")
    return runner, session_service


def run_agent_workflow(runner, session_service, topic):
    """
    This is the bridge function to run the async ADK code
    from synchronous Streamlit code.
    """
    app_name = runner.app_name
    user_id = "streamlit_user"
    session_id = f"learn-{uuid.uuid4().hex[:8]}"

    async def _run_async():
        # 1. Create the session
        await session_service.create_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

        # 2. Create the user's message
        query_content = types.Content(role="user", parts=[types.Part(text=topic)])

        # 3. Run the agent workflow to completion
        # We'll use st.status to show progress
        status = st.status(f"**Step 1: Researching '{topic}'...**")

        async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=query_content
        ):
            # Update the status as the agent moves to the next step
            if event.author == "SummarizerAgent":
                status.update(label="**Step 2: Writing study guide...**")
            elif event.author == "QuizAgent":
                status.update(label="**Step 3: Creating quiz...**")

        status.update(label="**Workflow Complete!**", state="complete")

        # 4. Get the final session and extract the answer
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

        # 5. Return all the pieces to display
        return {
            "research": session.state.get("research_findings", "No research found."),
            "guide": session.state.get("study_guide", "No study guide created."),
            "quiz": session.state.get("final_quiz", "No quiz created.")
        }

    # Use asyncio.run() to execute the async function
    # This is the standard way to call async from sync
    return asyncio.run(_run_async())


# --- 4. The Main App Logic ---

# Initialize the Runner and SessionService using caching
try:
    runner, session_service = get_runner()
except Exception as e:
    st.error(f"Failed to initialize agent. Check your API key. Error: {e}")
    st.stop()

# Get user input
topic = st.text_input("What topic do you want to learn about today?")

if topic:
    if st.button(f"Generate Learning Module for '{topic}'"):
        try:
            # Run the entire workflow
            results = run_agent_workflow(runner, session_service, topic)

            # Display the results in expanding sections
            st.success("Your learning module is ready!")

            with st.expander("Step 1: Research Findings (from ResearchAgent)"):
                st.markdown(results["research"])

            with st.expander("Step 2: Study Guide (from SummarizerAgent)"):
                st.markdown(results["guide"])

            with st.expander("Step 3: Your Quiz (from QuizAgent)", expanded=True):
                st.markdown(results["quiz"])

        except Exception as e:
            st.error(f"An error occurred while running the agent: {e}")
            st.exception(e)