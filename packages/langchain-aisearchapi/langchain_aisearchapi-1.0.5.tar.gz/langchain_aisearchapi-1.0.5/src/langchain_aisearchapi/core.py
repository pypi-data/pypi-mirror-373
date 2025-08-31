"""
🚀 LangChain Integration for AI Search API
==========================================

A powerful integration that brings AI Search API's intelligent search capabilities
into the LangChain ecosystem. Search, analyze, and build AI applications with
context-aware responses and source attribution.

Author: AI Search API Team
Version: 1.0.0
License: MIT
"""

import os
import json
from typing import Any, List, Optional, Dict, Iterator, AsyncIterator

# LangChain imports
from langchain.callbacks.manager import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.chat_models.base import BaseChatModel
from langchain.schema import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    ChatGeneration,
    LLMResult,
    ChatResult,
)
from langchain.schema.messages import BaseMessageChunk, AIMessageChunk
from langchain.schema.output import ChatGenerationChunk
from langchain.tools import BaseTool
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate

# Pydantic v2
from pydantic import BaseModel, model_validator, ConfigDict, PrivateAttr

# Your AI Search API client
from aisearchapi_client import AISearchAPIClient, ChatMessage, AISearchAPIError


# ============================================================================
# 🎯 Core LangChain LLM Implementation
# ============================================================================

class AISearchLLM(LLM):
    """
    🤖 LangChain LLM wrapper for AI Search API

    Features:
    - Semantic search with context awareness
    - Source attribution
    - Markdown/text response formatting
    - Error handling
    """

    # Pydantic v2 config
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    # Public fields
    api_key: Optional[str] = None
    base_url: str = "https://api.aisearchapi.io"
    timeout: int = 30
    response_type: str = "markdown"   # 'text' or 'markdown'
    include_sources: bool = True

    # Private (not part of the model)
    _client: AISearchAPIClient = PrivateAttr(default=None)

    @model_validator(mode="before")
    def _ensure_api_key(cls, values: Dict) -> Dict:
        api_key = values.get("api_key") or os.getenv("AI_SEARCH_API_KEY")
        if not api_key:
            raise ValueError(
                "AI Search API key not found. Set 'api_key' or env var 'AI_SEARCH_API_KEY'."
            )
        values["api_key"] = api_key
        return values

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._client = AISearchAPIClient(
            api_key=self.api_key, base_url=self.base_url, timeout=self.timeout
        )

    @property
    def _llm_type(self) -> str:
        return "ai_search_api"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "base_url": self.base_url,
            "response_type": self.response_type,
            "include_sources": self.include_sources,
            "timeout": self.timeout,
        }

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        try:
            # optional chat context
            context = kwargs.get("context", [])
            chat_context: Optional[List[ChatMessage]] = None
            if context:
                chat_context = []
                for msg in context:
                    if isinstance(msg, str):
                        chat_context.append(ChatMessage(role="user", content=msg))
                    elif isinstance(msg, dict):
                        chat_context.append(
                            ChatMessage(role="user", content=msg.get("content", ""))
                        )

            # call API
            response = self._client.search(
                prompt=prompt,
                context=chat_context,
                response_type=self.response_type,
            )

            result = response.answer
            if self.include_sources and response.sources:
                result += "\n\n📚 **Sources:**\n"
                for i, source in enumerate(response.sources, 1):
                    result += f"{i}. {source}\n"

            result += f"\n<!-- Processing time: {response.total_time}ms -->"
            return result

        except AISearchAPIError as e:
            return f"❌ AI Search API Error: {e.description}"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"

    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        return self._call(prompt, stop, run_manager, **kwargs)

    def get_num_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    def save(self, file_path: str) -> None:
        config = {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "response_type": self.response_type,
            "include_sources": self.include_sources,
        }
        with open(file_path, "w") as f:
            json.dump(config, f, indent=2)

    @classmethod
    def load(cls, file_path: str) -> "AISearchLLM":
        with open(file_path, "r") as f:
            config = json.load(f)
        return cls(**config)


# ============================================================================
# 💬 Chat Model Implementation
# ============================================================================

class AISearchChat(BaseChatModel):
    """
    🗨️ Chat-optimized wrapper for AI Search API
    """

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    api_key: Optional[str] = None
    base_url: str = "https://api.aisearchapi.io"
    timeout: int = 30
    response_type: str = "markdown"
    include_sources: bool = True
    streaming: bool = False

    _client: AISearchAPIClient = PrivateAttr(default=None)

    @model_validator(mode="before")
    def _ensure_api_key(cls, values: Dict) -> Dict:
        api_key = values.get("api_key") or os.getenv("AI_SEARCH_API_KEY")
        if not api_key:
            raise ValueError("AI Search API key required")
        values["api_key"] = api_key
        return values

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._client = AISearchAPIClient(
            api_key=self.api_key, base_url=self.base_url, timeout=self.timeout
        )

    @property
    def _llm_type(self) -> str:
        return "ai_search_chat"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if not messages:
            raise ValueError("No messages provided")

        last_message = messages[-1]
        prompt = last_message.content

        # build context from earlier messages
        context: List[ChatMessage] = []
        for msg in messages[:-1]:
            if isinstance(msg, (HumanMessage, SystemMessage)):
                context.append(ChatMessage(role="user", content=msg.content))

        try:
            response = self._client.search(
                prompt=prompt,
                context=context if context else None,
                response_type=self.response_type,
            )

            content = response.answer
            if self.include_sources and response.sources:
                content += "\n\n📚 **Sources:**\n"
                for i, source in enumerate(response.sources, 1):
                    content += f"{i}. {source}\n"

            message = AIMessage(
                content=content,
                additional_kwargs={
                    "sources": response.sources,
                    "processing_time_ms": response.total_time,
                },
            )
            generation = ChatGeneration(message=message)
            return ChatResult(generations=[generation])

        except AISearchAPIError as e:
            error_message = AIMessage(content=f"❌ Error: {e.description}")
            generation = ChatGeneration(message=error_message)
            return ChatResult(generations=[generation])

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        return self._generate(messages, stop, run_manager, **kwargs)

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        result = self._generate(messages, stop, run_manager, **kwargs)
        full_content = result.generations[0].message.content

        chunk_size = 20
        for i in range(0, len(full_content), chunk_size):
            chunk_text = full_content[i : i + chunk_size]
            chunk = ChatGenerationChunk(message=AIMessageChunk(content=chunk_text))
            yield chunk

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        for chunk in self._stream(messages, stop, run_manager, **kwargs):
            yield chunk


# ============================================================================
# 🛠️ Custom Tools for AI Search
# ============================================================================

class AISearchTool(BaseTool):
    """
    🔍 AI Search as a LangChain Tool
    """

    name: str = "ai_search"
    description: str = (
        "Intelligent search tool that provides accurate, sourced answers. "
        "Use this when you need to find information with reliable sources."
    )

    # Keep API key via env by default
    def __init__(self, api_key: Optional[str] = None, **kwargs: Any):
        super().__init__(**kwargs)
        api_key = api_key or os.getenv("AI_SEARCH_API_KEY")
        if not api_key:
            raise ValueError("API key required")
        self._client = AISearchAPIClient(api_key=api_key)

    def _run(self, query: str, run_manager: Optional[Any] = None) -> str:
        try:
            response = self._client.search(prompt=query, response_type="markdown")
            result = f"🔍 **Search Results:**\n\n{response.answer}\n\n"
            if response.sources:
                result += "📚 **Sources:**\n"
                for i, source in enumerate(response.sources, 1):
                    result += f"{i}. {source}\n"
            return result
        except Exception as e:
            return f"❌ Search failed: {str(e)}"

    async def _arun(self, query: str, run_manager: Optional[Any] = None) -> str:
        return self._run(query, run_manager)


def create_balance_tool(api_key: Optional[str] = None) -> Tool:
    api_key = api_key or os.getenv("AI_SEARCH_API_KEY")
    client = AISearchAPIClient(api_key=api_key)

    def check_balance(_: str = "") -> str:
        try:
            balance = client.balance()
            return (
                f"💳 **Account Balance:**\n"
                f"Available Credits: {balance.available_credits:,}\n"
                f"{'⚠️ Low balance warning!' if balance.available_credits < 10 else '✅ Balance healthy'}"
            )
        except Exception as e:
            return f"❌ Failed to check balance: {str(e)}"

    return Tool(
        name="check_ai_search_balance",
        func=check_balance,
        description="Check AI Search API account balance and available credits",
    )


# ============================================================================
# 🎭 Pre-built Chains and Agents (new style)
# ============================================================================

def create_research_chain(api_key: Optional[str] = None):
    """
    Returns a Runnable: (PromptTemplate | AISearchLLM)
    Use: chain.invoke({'topic': '...'})
    """
    llm = AISearchLLM(api_key=api_key, response_type="markdown", include_sources=True)

    prompt = PromptTemplate(
        input_variables=["topic"],
        template=(
            "Please provide a comprehensive research summary on the following topic:\n\n"
            "Topic: {topic}\n\n"
            "Include:\n"
            "1. Key concepts and definitions\n"
            "2. Current state of knowledge\n"
            "3. Recent developments\n"
            "4. Future implications\n"
            "5. Reliable sources\n"
        ),
    )

    # New runnable style
    chain = prompt | llm
    return chain


def create_qa_chain(api_key: Optional[str] = None) -> ConversationChain:
    """
    Q&A chain with memory (ConversationChain is still fine).
    Use: qa.invoke({'input': '...'})
    """
    llm = AISearchLLM(api_key=api_key, response_type="text")
    memory = ConversationBufferMemory()
    return ConversationChain(llm=llm, memory=memory, verbose=True)


def create_fact_checker_chain(api_key: Optional[str] = None):
    """
    Returns a Runnable: (PromptTemplate | AISearchLLM)
    Use: checker.invoke({'claim': '...'})
    """
    llm = AISearchLLM(api_key=api_key, response_type="markdown", include_sources=True)

    prompt = PromptTemplate(
        input_variables=["claim"],
        template=(
            "Please fact-check the following claim:\n\n"
            "Claim: {claim}\n\n"
            "Provide:\n"
            "1. Verdict: TRUE / FALSE / PARTIALLY TRUE / UNVERIFIABLE\n"
            "2. Explanation with evidence\n"
            "3. Reliable sources supporting the verdict\n"
        ),
    )

    chain = prompt | llm
    return chain


# ============================================================================
# 🎯 Utility Functions
# ============================================================================

def test_connection(api_key: Optional[str] = None) -> bool:
    try:
        api_key = api_key or os.getenv("AI_SEARCH_API_KEY")
        client = AISearchAPIClient(api_key=api_key)
        balance = client.balance()
        print(f"✅ Connection successful! Credits: {balance.available_credits:,}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False


def estimate_cost(text: str, cost_per_credit: float = 0.001) -> float:
    credits = max(1, len(text) // 100)
    return credits * cost_per_credit


# ============================================================================
# 🚀 Quick Start Examples (new invoke style)
# ============================================================================

def example_basic_usage():
    print("🎯 Basic AI Search LangChain Usage\n" + "=" * 40)

    llm = AISearchLLM(api_key=os.getenv("AI_SEARCH_API_KEY"))

    # Simple query
    response = llm.invoke("What are the benefits of renewable energy?")
    print(f"Response:\n{response}\n")

    # With context
    response = llm.invoke(
        "What are the main challenges?",
        context=["We're discussing solar panel installation for homes"],
    )
    print(f"Contextual Response:\n{response}")


def example_chat_usage():
    print("💬 Chat Model Usage\n" + "=" * 40)

    chat = AISearchChat(api_key=os.getenv("AI_SEARCH_API_KEY"))

    messages = [
        HumanMessage(content="Tell me about electric vehicles"),
        HumanMessage(content="What about their environmental impact?"),
        HumanMessage(content="How do they compare to hydrogen cars?"),
    ]

    result = chat.invoke(messages)
    # result is ChatResult; get first generation content:
    content = result.generations[0].message.content
    print(f"Chat Response:\n{content}")


def example_agent_usage():
    print("🤖 Agent with AI Search Tools\n" + "=" * 40)

    from langchain.agents import initialize_agent, AgentType

    search_tool = AISearchTool(api_key=os.getenv("AI_SEARCH_API_KEY"))
    balance_tool = create_balance_tool(api_key=os.getenv("AI_SEARCH_API_KEY"))

    llm = AISearchLLM(api_key=os.getenv("AI_SEARCH_API_KEY"))
    agent = initialize_agent(
        tools=[search_tool, balance_tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    result = agent.invoke({"input": "Search info about Mars colonization and check my balance"})
    print(f"Agent Result:\n{result['output']}")


def example_chain_usage():
    print("🔗 Custom Chain Usage\n" + "=" * 40)

    research_chain = create_research_chain(api_key=os.getenv("AI_SEARCH_API_KEY"))
    result = research_chain.invoke({"topic": "Quantum computing applications in medicine"})
    print(f"Research Result:\n{result}\n")

    fact_checker = create_fact_checker_chain(api_key=os.getenv("AI_SEARCH_API_KEY"))
    result = fact_checker.invoke({"claim": "Coffee is the world's second-most traded commodity"})
    print(f"Fact Check Result:\n{result}")


if __name__ == "__main__":
    print(
        """
    🚀 AI Search API + LangChain Integration
    ========================================

    Quick Start:
    1. Set your API key:
       - PowerShell: $env:AI_SEARCH_API_KEY="your-key"
       - bash/zsh:   export AI_SEARCH_API_KEY="your-key"
    2. Import components
    3. Build your app!
    """
    )

    # Uncomment to run examples:
    # example_basic_usage()
    # example_chat_usage()
    # example_agent_usage()
    # example_chain_usage()
