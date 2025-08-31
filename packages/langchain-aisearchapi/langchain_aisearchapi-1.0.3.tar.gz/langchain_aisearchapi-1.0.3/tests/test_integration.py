#!/usr/bin/env python3
"""
⚡ Quick Test Script for AI Search API + LangChain Integration
==============================================================

Run this script to verify your integration is working correctly!

Usage:
    python test_integration.py

Make sure to set your API key first:
    export AI_SEARCH_API_KEY='your-actual-api-key-here'
"""

import os
import sys
from typing import Optional
from langchain_aisearchapi import AISearchLLM

# Color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_test(test_name: str, success: bool, message: str = ""):
    """Print test result"""
    status = f"{Colors.GREEN}✅ PASSED{Colors.ENDC}" if success else f"{Colors.FAIL}❌ FAILED{Colors.ENDC}"
    print(f"{Colors.CYAN}Test:{Colors.ENDC} {test_name:<40} {status}")
    if message:
        print(f"     {Colors.WARNING}→ {message}{Colors.ENDC}")


def test_imports() -> bool:
    """Test if all required imports work"""
    try:
        # Test AI Search API client
        from aisearchapi_client import AISearchAPIClient, ChatMessage
        print_test("AI Search API import", True)
        
        # Test LangChain
        from langchain.llms.base import LLM
        from langchain.schema import HumanMessage
        print_test("LangChain import", True)
        
        # Test integration module
        from langchain_aisearchapi import AISearchLLM, AISearchChat, AISearchTool
        print_test("Integration module import", True)
        
        return True
    except ImportError as e:
        print_test("Import test", False, str(e))
        return False


def test_api_key() -> Optional[str]:
    """Test if API key is configured"""
    api_key = os.getenv('AI_SEARCH_API_KEY')
    
    if api_key:
        masked_key = api_key[:10] + '...' + api_key[-4:] if len(api_key) > 20 else 'key_set'
        print_test("API key environment variable", True, f"Found: {masked_key}")
        return api_key
    else:
        print_test("API key environment variable", False, 
                  "Set with: export AI_SEARCH_API_KEY='your-key'")
        return None


def test_connection(api_key: str) -> bool:
    """Test API connection"""
    try:
        from aisearchapi_client import AISearchAPIClient
        
        client = AISearchAPIClient(api_key=api_key)
        balance = client.balance()
        
        print_test("API connection", True, 
                  f"Credits available: {balance.available_credits:,}")
        
        if balance.available_credits < 10:
            print(f"     {Colors.WARNING}⚠️  Low balance warning!{Colors.ENDC}")
        
        return True
    except Exception as e:
        print_test("API connection", False, str(e))
        return False


def test_basic_llm(api_key: str) -> bool:
    """Test basic LLM functionality"""
    try:
        from langchain_aisearchapi import AISearchLLM
        
        llm = AISearchLLM(api_key=api_key, response_type="text")
        response = llm("What is 2+2? Give a very short answer.")
        
        if response and len(response) > 0:
            print_test("Basic LLM query", True, 
                      f"Response length: {len(response)} chars")
            print(f"     {Colors.BLUE}Sample: {response[:100]}...{Colors.ENDC}")
            return True
        else:
            print_test("Basic LLM query", False, "Empty response")
            return False
            
    except Exception as e:
        print_test("Basic LLM query", False, str(e))
        return False


def test_chat_model(api_key: str) -> bool:
    """Test chat model functionality"""
    try:
        from langchain_aisearchapi import AISearchChat
        from langchain.schema import HumanMessage
        
        chat = AISearchChat(api_key=api_key, response_type="text")
        
        messages = [
            HumanMessage(content="What is Python?"),
            HumanMessage(content="Name one advantage")
        ]
        
        response = chat(messages)
        
        if response and response.content:
            print_test("Chat model", True, 
                      f"Response length: {len(response.content)} chars")
            return True
        else:
            print_test("Chat model", False, "Empty response")
            return False
            
    except Exception as e:
        print_test("Chat model", False, str(e))
        return False


def test_search_tool(api_key: str) -> bool:
    """Test search tool functionality"""
    try:
        from langchain_aisearchapi import AISearchTool
        
        tool = AISearchTool(api_key=api_key)
        result = tool.run("What year was Python created?")
        
        if result and len(result) > 0:
            print_test("Search tool", True, 
                      f"Found {result.count('Source')} sources")
            return True
        else:
            print_test("Search tool", False, "No results")
            return False
            
    except Exception as e:
        print_test("Search tool", False, str(e))
        return False


def test_chains(api_key: str) -> bool:
    """Test pre-built chains"""
    try:
        from langchain_aisearchapi import create_research_chain, create_qa_chain
        
        # Test research chain
        research_chain = create_research_chain(api_key=api_key)
        print_test("Research chain creation", True)
        
        # Test QA chain
        qa_chain = create_qa_chain(api_key=api_key)
        print_test("Q&A chain creation", True)
        
        return True
    except Exception as e:
        print_test("Chain creation", False, str(e))
        return False


def run_integration_demo(api_key: str):
    """Run a complete integration demo"""
    print_header("🎭 INTEGRATION DEMO")
    
    try:
        from langchain_aisearchapi import AISearchLLM, AISearchTool
        from langchain.agents import initialize_agent, AgentType
        from langchain.chains import LLMChain
        from langchain.prompts import PromptTemplate
        
        print(f"{Colors.CYAN}Creating an AI agent with search capabilities...{Colors.ENDC}\n")
        
        # Create LLM and tool
        llm = AISearchLLM(api_key=api_key, response_type="markdown")
        search_tool = AISearchTool(api_key=api_key)
        
        # Create a simple chain
        prompt = PromptTemplate(
            input_variables=["topic"],
            template="Explain {topic} in one paragraph for a beginner."
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Run the chain
        print(f"{Colors.BLUE}Running chain with topic 'artificial intelligence'...{Colors.ENDC}")
        result = chain.run("artificial intelligence")
        
        print(f"\n{Colors.GREEN}Result:{Colors.ENDC}")
        print(f"{result[:300]}...")
        
        print(f"\n{Colors.GREEN}✨ Integration demo successful!{Colors.ENDC}")
        return True
        
    except Exception as e:
        print(f"{Colors.FAIL}Demo failed: {e}{Colors.ENDC}")
        return False


def main():
    """Main test runner"""
    print_header("🚀 AI SEARCH API + LANGCHAIN INTEGRATION TEST")
    
    # Track test results
    all_passed = True
    
    # Test 1: Imports
    print(f"{Colors.BOLD}Step 1: Testing imports...{Colors.ENDC}")
    if not test_imports():
        print(f"\n{Colors.FAIL}Please install required packages:{Colors.ENDC}")
        print("pip install aisearchapi-client langchain langchain-community")
        sys.exit(1)
    
    # Test 2: API Key
    print(f"\n{Colors.BOLD}Step 2: Checking API key...{Colors.ENDC}")
    api_key = test_api_key()
    if not api_key:
        print(f"\n{Colors.WARNING}Using test key for demo...{Colors.ENDC}")
        # You can add a test key here if available
        api_key = "test-key-replace-with-real"
    
    # Test 3: Connection
    print(f"\n{Colors.BOLD}Step 3: Testing API connection...{Colors.ENDC}")
    if not test_connection(api_key):
        all_passed = False
        print(f"{Colors.WARNING}Connection failed. Check your API key.{Colors.ENDC}")
    
    # Test 4: Core functionality
    print(f"\n{Colors.BOLD}Step 4: Testing core functionality...{Colors.ENDC}")
    
    if test_basic_llm(api_key):
        pass
    else:
        all_passed = False
    
    if test_chat_model(api_key):
        pass
    else:
        all_passed = False
    
    if test_search_tool(api_key):
        pass
    else:
        all_passed = False
    
    if test_chains(api_key):
        pass
    else:
        all_passed = False
    
    # Test 5: Integration demo
    if all_passed:
        print(f"\n{Colors.BOLD}Step 5: Running integration demo...{Colors.ENDC}")
        run_integration_demo(api_key)
    
    # Final summary
    print_header("📊 TEST SUMMARY")
    
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED!{Colors.ENDC}")
        print(f"\n{Colors.CYAN}Your integration is ready to use! 🎉{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Next steps:{Colors.ENDC}")
        print("1. Check out the examples in the documentation")
        print("2. Start building your own applications")
        print("3. Explore advanced features like agents and chains")
    else:
        print(f"{Colors.WARNING}⚠️  Some tests failed.{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Troubleshooting:{Colors.ENDC}")
        print("1. Verify your API key is correct")
        print("2. Check your internet connection")
        print("3. Ensure all packages are installed correctly")
        print("4. Review the error messages above")
    
    print(f"\n{Colors.CYAN}Happy coding! 🚀{Colors.ENDC}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Test interrupted by user.{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)
