# SkillSense: AI-Powered Talent Intelligence Platform

## Overview

SkillSense is an advanced, AI-powered talent intelligence platform. It leverages a sophisticated **agentic architecture** to understand user queries and dynamically interact with multiple data sources. The agent can seamlessly query a structured database (NL-to-SQL) and perform semantic searches across unstructured documents (RAG) like resumes and performance reviews to provide comprehensive, evidence-based answers to complex questions about your workforce.

The entire backend is built with a fully **asynchronous** design, allowing the agent to execute tasks concurrently for enhanced performance.

## Core Features

-   **Agentic Query Processing**: An intelligent agent plans and executes tasks, deciding whether to use SQL, RAG, or both to answer a user's question.
-   **Hybrid Data Retrieval**: Combines structured data from a SQL database with unstructured data from documents in a single query.
-   **Multi-Format Document Support**: Ingest and analyze documents in various formats, including **.txt**, **.pdf**, and **.docx**.
-   **Conversational Interface**: The agent can recognize and respond to simple greetings and small talk, providing a more user-friendly experience.
-   **Robust and Resilient**:
    -   **SQL Self-Correction**: The agent can automatically detect errors in its generated SQL and attempt to correct them.
    -   **Resilient to Service Delays**: The system is designed to be resilient against slow or hanging external API calls, preventing application freezes.
-   **Comprehensive Testing Suite**: Includes a built-in benchmark to test the agent's performance across various query types.

## Setup and Installation

1.  **Clone the repository** (if you haven't already).

2.  **Set up your environment variables**:
    Copy the `.env.example` file to a new file named `.env` and add your `OPENROUTER_API_KEY`.

    ```
    OPENROUTER_API_KEY="your_key_here"
    ```

3.  **Install dependencies**:
    It's recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database**:
    This will create the `talent_database.db` file and populate it with initial data.
    ```bash
    python setup_database.py
    ```

## How to Run

1.  **Start the API Server**:
    ```bash
    uvicorn api_server:app --reload
    ```
    The server will be available at `http://localhost:8001`.

2.  **Use the Interactive Chat Client**:
    In a separate terminal, run the chat client to interact with the agent.
    ```bash
    python chat_client.py
    ```

## How to Use

Once the chat client is running, you can interact with the agent.

-   **Ask a Question**: Type any question about your talent pool and press Enter.
    -   *SQL-like query*: `What are the top 5 technical skills in the company?`
    -   *RAG-like query*: `What does Alice's resume say about machine learning?`
    -   *Hybrid query*: `Find Python developers and show me their project examples`
-   **Upload a Document**: Use the `upload` command to add new documents to the RAG system's knowledge base.
    ```
    You: upload path/to/your/resume.docx
    ```
-   **Say Hello**: The agent will respond to simple greetings.
    ```
    You: hello
    ```

## Testing

The project includes a comprehensive benchmark suite to evaluate the agent's performance. To run the benchmark, use the `--test` flag:

```bash
python chat_client.py --test
```

## A Note on LLM Configuration

The application's performance and stability are highly dependent on the LLM provider and the specific models being used. This project is configured to use **OpenRouter**.

-   **Rate Limiting**: Be aware that free or low-tier models on services like OpenRouter are often subject to strict rate limiting. This can cause significant delays or timeouts. The intermittent "freezing" issues encountered during development were ultimately traced back to being rate-limited on a free model.
-   **Model Choice**: The quality of the agent's plans and generated SQL depends on the model's instruction-following capabilities. The current configuration uses different models for planning and general tasks, which can be adjusted in `managers/llm_manager.py`.
