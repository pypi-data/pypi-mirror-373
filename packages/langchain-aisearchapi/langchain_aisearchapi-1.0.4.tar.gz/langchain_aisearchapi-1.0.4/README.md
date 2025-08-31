# 🚀 LangChain AI Search API Integration

[![PyPI version](https://img.shields.io/pypi/v/langchain-aisearchapi.svg)](https://pypi.org/project/langchain-aisearchapi/)  
[![Python Support](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Official **LangChain integration** for the [AI Search API](https://aisearchapi.io?utm_source=github).  
Use **semantic search**, **contextual answers**, **summarization**, and **intelligent agents** in your LangChain projects with just one package.

---

## ✨ Features

- 🔑 **One Package Setup** – `pip install langchain-aisearchapi` and you’re ready  
- 🤖 **LLM Interface** – Use AI Search API as a LangChain LLM  
- 💬 **Chat Model** – Build conversational agents with context memory  
- 🛠️ **Tools for Agents** – Add AI Search, Web Search API, or Summarization API into LangChain workflows  
- 📚 **Prebuilt Chains** – Research, Q&A, fact-checking, summarization out of the box  

---

## 🔑 Get Started

Create an account and get your API key:  
- [🆕 Sign Up](https://aisearchapi.io/join?utm_source=github)  
- [🔑 Log In](https://aisearchapi.io/login?utm_source=github)  
- [📊 Dashboard](https://aisearchapi.io/dashboard?utm_source=github)  

---

## ⚡ Installation

Install from PyPI:

```bash
pip install langchain-aisearchapi
```

That’s it — no extra setup required.

---

## 🚀 Quick Start

### 1. Basic LLM Usage
```python
from langchain_aisearchapi import AISearchLLM

llm = AISearchLLM(api_key="your-key")
response = llm("Explain semantic search in simple terms")
print(response)
```

### 2. Conversational Chat
```python
from langchain_aisearchapi import AISearchChat
from langchain.schema import HumanMessage

chat = AISearchChat(api_key="your-key")

messages = [
    HumanMessage(content="What is LangChain?"),
    HumanMessage(content="Why do developers use it?")
]

response = chat(messages)
print(response.content)
```

### 3. AI Search + Agents
```python
from langchain_aisearchapi import AISearchTool, AISearchLLM
from langchain.agents import initialize_agent, AgentType

search_tool = AISearchTool(api_key="your-key")
llm = AISearchLLM(api_key="your-key")

agent = initialize_agent(
    tools=[search_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

result = agent.run("Find the latest SpaceX launch details")
print(result)
```

### 4. Research Assistant
```python
from langchain_aisearchapi import create_research_chain

research = create_research_chain(api_key="your-key")
result = research.run("Breakthroughs in AI search technology 2024")
print(result)
```

### 5. Summarization API Example
```python
from langchain_aisearchapi import AISearchLLM

llm = AISearchLLM(api_key="your-key")
text = "Your long text here..."
summary = llm(f"Summarize this text: {text}")
print(summary)
```

---

## 🛠️ Components

| Component | Description | Use Case |
|-----------|-------------|----------|
| **AISearchLLM** | AI Search API as an LLM | Completions, text generation |
| **AISearchChat** | Chat model with context | Conversational AI, assistants |
| **AISearchTool** | Search / Web Search API as LangChain tool | Agents, workflows |
| **create_research_chain()** | Ready-made chain | Research and reporting |
| **Summarization API** | Summarize text into concise outputs | Notes, abstracts, executive summaries |

📘 Full API reference: [AI Search API Docs](https://docs.aisearchapi.io)

---

## ❗ Troubleshooting

- **No API key?** → [Sign up](https://aisearchapi.io/join?utm_source=github) or [Log in](https://aisearchapi.io/login?utm_source=github)  
- **Key issues?** → Check your [dashboard](https://aisearchapi.io/dashboard?utm_source=github)  
- **Rate limited?** → Use retry logic with [tenacity](https://pypi.org/project/tenacity/)  

---

## 📚 Resources

- [🌐 AI Search API Homepage](https://aisearchapi.io?utm_source=github)  
- [📘 Documentation](https://docs.aisearchapi.io?utm_source=github)  
- [📦 PyPI Package](https://pypi.org/project/langchain-aisearchapi/)  
- [Blog](https://aisearchapi.io/blog/)

---

## 🎉 Start Now

Install the package, get your API key, and build powerful LangChain apps with the **AI Search API, Web Search API, Summary API, and Summarization API**:

```bash
pip install langchain-aisearchapi
```

👉 [Join now](https://aisearchapi.io/join?utm_source=github) to claim your free API key and start building!

---

Made with ❤️ for the AI Search API + LangChain developer community  

---

## 🔍 SEO Keywords

LangChain AI Search API integration, AI Search API Python package, semantic search LangChain, contextual AI LangChain, AI chatbot LangChain, summarization API LangChain, web search API LangChain, AI Search API key setup, summary API integration
