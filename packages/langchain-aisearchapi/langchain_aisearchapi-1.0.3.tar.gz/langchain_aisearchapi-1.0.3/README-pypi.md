# 🚀 LangChain + AI Search API Integration

[![PyPI version](https://img.shields.io/pypi/v/langchain-aisearchapi.svg)](https://pypi.org/project/langchain-aisearchapi/)  
[![Python Support](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Official **LangChain integration** for the [AI Search API](https://aisearchapi.io?utm_source=pypi).  
Bring **semantic search**, **contextual answers**, **summarization**, and **intelligent agents** to your LangChain apps in minutes.

---

## ✨ Features

- 🔑 **One-Line Install** – `pip install langchain-aisearchapi`  
- 🤖 **LLM Interface** – Use AI Search API directly as a LangChain LLM  
- 💬 **Chat Model** – Build conversations with memory & context  
- 🛠️ **Agent Tools** – Add AI Search, Web Search, Summarization APIs as tools  
- 📚 **Prebuilt Chains** – Research, Q&A, fact-checking, and summaries out of the box  

---

## 🔑 Get Started

1. [🆕 Sign Up](https://aisearchapi.io/join?utm_source=pypi)  
2. [🔑 Log In](https://aisearchapi.io/login?utm_source=pypi)  
3. [📊 Dashboard](https://aisearchapi.io/dashboard?utm_source=pypi) → Copy your API key  

---

## ⚡ Installation

```bash
pip install langchain-aisearchapi
```

---

## 🚀 Quick Examples

### LLM Usage
```python
from langchain_aisearchapi import AISearchLLM

llm = AISearchLLM(api_key="your-key")
print(llm("Explain semantic search in simple terms"))
```

### Conversational Chat
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

### Tool + Agent
```python
from langchain_aisearchapi import AISearchTool, AISearchLLM
from langchain.agents import initialize_agent, AgentType

tool = AISearchTool(api_key="your-key")
llm = AISearchLLM(api_key="your-key")

agent = initialize_agent(
    tools=[tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
print(agent.run("Find the latest SpaceX launch details"))
```

### Research Chain
```python
from langchain_aisearchapi import create_research_chain

research = create_research_chain(api_key="your-key")
print(research.run("Breakthroughs in AI search 2024"))
```

### Summarization
```python
from langchain_aisearchapi import AISearchLLM

llm = AISearchLLM(api_key="your-key")
summary = llm("Summarize this text: AI search connects context and meaning in queries.")
print(summary)
```

---

## 🛠️ Components

| Component | Description | Use Case |
|-----------|-------------|----------|
| **AISearchLLM** | AI Search API as an LLM | Completions, text generation |
| **AISearchChat** | Chat model with context | Assistants, multi-turn chats |
| **AISearchTool** | Search / Web Search API tool | Agents, workflows |
| **create_research_chain()** | Prebuilt chain | Research & reporting |
| **Summarization API** | Text summarization | Notes, abstracts |

📘 Docs: [AI Search API Documentation](https://docs.aisearchapi.io?utm_source=pypi)

---

## ❗ Troubleshooting

- **No API key?** → [Sign up](https://aisearchapi.io/join?utm_source=pypi)  
- **Issues with key?** → Check [Dashboard](https://aisearchapi.io/dashboard?utm_source=pypi)  
- **Rate limited?** → Add retries (e.g. with [tenacity](https://pypi.org/project/tenacity/))  

---

## 📚 Resources

- [🌐 Homepage](https://aisearchapi.io?utm_source=pypi)  
- [📘 Documentation](https://docs.aisearchapi.io?utm_source=pypi)  
- [📦 PyPI](https://pypi.org/project/langchain-aisearchapi/)  
- [📝 Blog](https://aisearchapi.io/blog/)  

---

## 🎉 Get Started Now

```bash
pip install langchain-aisearchapi
```

👉 [Join now](https://aisearchapi.io/join?utm_source=pypi) for a free API key and start building!

---

Made with ❤️ for LangChain developers using the AI Search API.

---

## 🔍 SEO Keywords

LangChain AI Search API integration, AI Search API Python package, semantic search LangChain, contextual AI LangChain, AI chatbot LangChain, summarization API LangChain, web search API LangChain, AI Search API key setup, summary API integration
