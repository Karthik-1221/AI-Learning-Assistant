🎓 AI Learning Assistant

A 3-Step Research-to-Quiz Agent built for the Google AI Agents Intensive Capstone (Kaggle).

This project is an autonomous agent designed to streamline the process of learning any new topic. Given a single prompt, the agent automatically researches the topic, synthesizes the findings into a study guide, and generates a quiz to test comprehension.

Video Demo

Watch a  demo of the app in action:

https://youtu.be/Q8xEudiGkKs

🚀 Features

The AI Learning Assistant uses a 3-step sequential workflow:

Research: Autonomously searches Google for the 3 most relevant and authoritative sources on the user's topic.

Summarize: Reads and synthesizes the research findings into a concise, easy-to-digest study guide, complete with an introduction, key bullet points, and a conclusion.

Quiz: Generates a 3-question multiple-choice quiz based on the study guide to immediately reinforce and test the user's knowledge.

🏗️ Architecture

This project is built using the Google Agent Development Kit (ADK) and follows a SequentialAgent architecture. This workflow ensures that each specialized agent completes its task before passing the output to the next, creating a reliable and logical flow.

The architecture consists of three specialized sub-agents:

ResearchAgent: An LlmAgent that uses the Google Search tool to find sources.

SummarizerAgent: An LlmAgent that takes the research and creates a study guide.

QuizAgent: An LlmAgent that takes the study guide and creates a quiz.

🛠️ Tech Stack

Core: Google Agent Development Kit (ADK), Python

Model: Google Gemini (via gemini-2.5-flash-lite)

App Framework: Streamlit

Tools: Google Search (via ADK)

Dependencies: python-dotenv for environment variable management

⚙️ Setup and Installation

Follow these steps to run the project locally.

Clone the repository:


Install dependencies:
It's recommended to use a virtual environment.

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt


(Ensure your requirements.txt file includes google-generative-ai, google-adk, streamlit, and python-dotenv)

Create your Environment File:
Create a file named .env in the root of the project directory and add your Google API key:

GOOGLE_API_KEY="your_api_key_here"


▶️ How to Run

Once your dependencies are installed and your .env file is set up, run the Streamlit app:

streamlit run learning_assistant.py


This will open the AI Learning Assistant in your default web browser.

Kaggle Competition

This project was built for the Agents Intensive - Capstone Project on Kaggle.

Track: Agents for Good

