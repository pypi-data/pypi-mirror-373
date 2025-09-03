

llm-toolchain: Giving LLMs Real Influence
============================================

llm-toolchain is a lightweight, easy-to-use Python library that makes it simple to connect Large Language Models (LLMs) to external functions and tools. It prioritizes simplicity and control, allowing you to enhance LLMs for personal automation, increase their reliability, and integrate them into your projects without complex, layered frameworks.

Philosophy
----------

The goal of llm-toolchain is to provide the power of tool use in a simple, intuitive package. It's for developers who:

* **Want to stay in control**: Interact directly with LLM providers without a middleman.
* **Want to keep it simple**: Use a minimal, clean API with no boilerplate code.
* **Want flexibility**: Easily extend the library with custom adapters for any LLM and custom selectors for any logic.
* **Want to automate personal tasks**: Create reliable agents for tasks like sending emails, managing files, or interacting with your personal APIs.

---

Key Features ✨
-----------------

* **Universal Adapters**: A powerful adapter system enables llm-toolchain to work with virtually any LLM, whether it has native function-calling capabilities or not. Pre-built adapters for OpenAI, Google Gemini, Vertex AI, and a generic `PromptAdapter` are included.
* **Semantic Tool Selector**: Intelligently and automatically selects the most relevant tools for a given prompt from a larger collection using vector embeddings, saving tokens and improving accuracy.
* **Simple & Lightweight**: With a minimal API and a focus on core functionality, the library is easy to learn and integrate into any project.
* **Easily Extensible**: Write your own adapters, selectors, and tools through simple class inheritance. If you can write a Python function, you can provide it to an LLM as a tool.

---

Installation 🚀
----------------

The base library is lightweight. You install the specific dependencies for the LLM providers you want to use as "extras."

Core Installation
^^^^^^^^^^^^^^^^^

.. code-block:: bash

    pip install llm-toolchain

Extras for LLM Providers
^^^^^^^^^^^^^^^^^^^^^^^^

Install the extras needed for the specific models you want to use.

For Google Gemini:
.. code-block:: bash

    pip install 'llm-toolchain[gemini]'

For OpenAI:
.. code-block:: bash

    pip install openai

For Google Vertex AI:
.. code-block:: bash

    pip install google-cloud-aiplatform

Environment Variables
^^^^^^^^^^^^^^^^^^^^^

You also need to set up your API keys in a `.env` file in the root of your project:

.. code-block:: ini

    # .env file
    OPENAI_API_KEY="sk-..."
    GEMINI_API_KEY="..."
    GEMINI_PROJECT_ID="..." # Required for Vertex AI

---

Quickstart ⚡
--------------

Here's the simplest way to get started. In just a few lines of code, you can give a Gemini model a custom tool and have it execute a function call.

.. code-block:: python


    # File: main.py
    import os
    from google import generativeai as genai
    import dotenv
    from llm_toolchain import Toolchain, GenAIAdapter, tool

    # --- 1. Define a tool ---
    # The @tool decorator automatically prepares your function for the LLM.
    # The docstring is crucial - it's used as the description for the LLM and the selector.
    @tool
    def get_weather(city: str) -> str:
        """
        Fetches the current weather for a specific city.
        Returns a string describing the weather.
        """
        # Dummy implementation for this example
        if "new york" in city.lower():
            return "It is currently 24°C and sunny in New York City."
        else:
            return f"Weather data for {city} is not available."

    # --- 2. Set up the LLM and Toolchain ---
    dotenv.load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    # The client and adapter handle the communication with the LLM
    llm_client = genai.GenerativeModel('gemini-1.5-flash')
    adapter = GenAIAdapter()

    # The Toolchain orchestrates everything
    chain = Toolchain(
        llm_client=llm_client,
        adapter=adapter,
        tools=[get_weather] # Pass the list of available tools
    )

    # --- 3. Run the Toolchain ---
    prompt = "What's the weather like in New York City today?"
    response = chain.run(prompt=prompt)

    print(response)
    # Expected Output: It is currently 24°C and sunny in New York City.

---

Advanced Usage
--------------

Using Different LLMs
^^^^^^^^^^^^^^^^^^^^

Switching between LLM providers is as simple as changing the client and the adapter.

OpenAI
""""""

.. code-block:: python

    from openai import OpenAI
    from llm_toolchain import OpenAIAdapter # Use the OpenAIAdapter

    llm_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    adapter = OpenAIAdapter()

    chain = Toolchain(llm_client=llm_client, adapter=adapter, tools=[...])

Google Vertex AI
""""""""""""""""

.. code-block:: python

    import vertexai
    from vertexai.generative_models import GenerativeModel
    from llm_toolchain import VertexAIAdapter # Use the VertexAIAdapter

    project_id = os.getenv("GEMINI_PROJECT_ID")
    vertexai.init(project=project_id, location="us-central1")
    llm_client = GenerativeModel('gemini-1.5-flash')
    adapter = VertexAIAdapter()

    chain = Toolchain(llm_client=llm_client, adapter=adapter, tools=[...])

The PromptAdapter (for any LLM)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For models that don't support native tool calls, the `PromptAdapter` injects tool definitions and JSON formatting instructions directly into the system prompt.

.. code-block:: python

    from llm_toolchain import PromptAdapter # Use the PromptAdapter

    # Use any LLM client, for example Gemini
    llm_client = genai.GenerativeModel('gemini-1.5-flash')
    adapter = PromptAdapter()

    chain = Toolchain(llm_client=llm_client, adapter=adapter, tools=[...])

Using the SemanticToolSelector
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Instead of passing a small list of tools to the `Toolchain`, you can provide a `SemanticToolSelector` with a large library of tools. It automatically selects the most relevant ones for the given prompt and provides them to the LLM.

.. code-block:: python

    from llm_toolchain import SemanticToolSelector
    from llm_toolchain import tools # Assuming you have a tools package

    all_my_tools = [
        tools.get_weather,
        tools.send_email,
        tools.read_file,
        # ... and dozens more
    ]

    selector = SemanticToolSelector(all_tools=all_my_tools)

    chain = Toolchain(
        llm_client=llm_client,
        adapter=adapter,
        selector=selector # Pass the selector instead of the 'tools' list
    )

    # The chain will now use the selector to pick the best tools for this prompt
    chain.run("What's the weather in Berlin and then email the result to my boss?")

---

Extending the Toolchain 🧑‍💻
------------------------------

llm-toolchain is designed to be easily extensible.

Creating a Custom Tool
^^^^^^^^^^^^^^^^^^^^^^

Simply decorate any Python function with `@tool`. A descriptive docstring is required as it's used to tell the LLM and the selector what the tool does.

.. code-block:: python

    from llm_toolchain import tool

    @tool
    def calculate_compound_interest(principal: float, rate: float, time: int) -> float:
        """
        Calculates the compound interest for a given principal amount, interest rate, and time period.
        """
        return principal * (1 + rate) ** time

Creating a Custom Adapter
^^^^^^^^^^^^^^^^^^^^^^^^^

You can support any LLM API by inheriting from `BaseAdapter`.

.. code-block:: python

    from llm_toolchain.adapters import BaseAdapter

    class MyCustomAdapter(BaseAdapter):
        def _get_run_strategies(self):
            # Return possible paths to the LLM's run method
            return [['run_llm']]

        def _get_parse_strategies(self):
            # Return possible paths to the response content
            return [['response', 'text']]

        def _build_request(self, messages, tools, **kwargs):
            # Format the request payload for your custom LLM
            return {"prompt": messages[-1]['content'], **kwargs}

        def generate_schema(self, tool):
            # Format the tool's schema for your custom LLM
            return f"{tool.name}: {tool.description}"

Creating a Custom Selector
^^^^^^^^^^^^^^^^^^^^^^^^^^

Implement any tool selection logic by inheriting from `BaseSelector`.

.. code-block:: python

    from llm_toolchain.selectors import BaseSelector

    class MyKeywordSelector(BaseSelector):
        def select_tools(self, prompt: str):
            selected = set()
            for tool in self.all_tools:
                if tool.name in prompt:
                    selected.add(tool)
            return selected

---

Roadmap 🗺️
----------

This library is under active development. The next major planned feature is:

* **Interactive UI**: A user interface for real-time control, observation, and correction of LLM tool calls, giving you full oversight of the agent's actions.

---

Contributing
------------

Contributions are welcome! If you'd like to help, feel free to submit a pull request, open an issue, or propose a new feature.

---

License
-------

This project is licensed under the MIT License. See the `LICENSE` file for more details.