"""
Tests for AI Search API CrewAI Tool
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from crewai_aisearchapi import AISearchTool, AISearchToolConfig
from aisearchapi_client import SearchResponse, BalanceResponse, AISearchAPIError


class TestAISearchTool:
    """Test suite for AI Search Tool"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock AI Search API client"""
        with patch('crewai_aisearchapi.tool.AISearchAPIClient') as mock:
            yield mock
    
    @pytest.fixture
    def tool(self, mock_client):
        """Create a tool instance with mocked client"""
        return AISearchTool(api_key='test-key')
    
    def test_initialization_with_api_key(self):
        """Test tool initialization with API key"""
        tool = AISearchTool(api_key='test-key')
        assert tool.api_key == 'test-key'
        assert tool.name == "AI Search"
    
    def test_initialization_with_env_var(self, monkeypatch):
        """Test tool initialization with environment variable"""
        monkeypatch.setenv('AISEARCHAPI_API_KEY', 'env-test-key')
        tool = AISearchTool()
        assert tool.api_key == 'env-test-key'
    
    def test_initialization_without_api_key(self):
        """Test that initialization fails without API key"""
        with pytest.raises(ValueError, match="API key is required"):
            AISearchTool()
    
    def test_successful_search(self, tool, mock_client):
        """Test successful search execution"""
        # Setup mock response
        mock_response = SearchResponse(
            answer="Machine learning is a subset of AI.",
            sources=["https://example.com/ml"],
            response_type="markdown",
            total_time=150
        )
        
        tool.client.search = Mock(return_value=mock_response)
        
        # Execute search
        result = tool._run(query="What is machine learning?")
        
        # Verify result
        assert "Machine learning is a subset of AI" in result
        assert "Sources:" in result
        assert "https://example.com/ml" in result
    
    def test_search_with_context(self, tool, mock_client):
        """Test search with context"""
        mock_response = SearchResponse(
            answer="Solar panels convert sunlight to electricity.",
            sources=["https://example.com/solar"],
            response_type="markdown",
            total_time=100
        )
        
        tool.client.search = Mock(return_value=mock_response)
        
        result = tool._run(
            query="How do they work?",
            context="I'm researching solar energy"
        )
        
        # Verify context was passed
        tool.client.search.assert_called_once()
        call_args = tool.client.search.call_args
        assert call_args[1]['context'] is not None
    
    def test_api_error_handling(self, tool, mock_client):
        """Test handling of API errors"""
        tool.client.search = Mock(
            side_effect=AISearchAPIError("Quota exceeded", 433)
        )
        
        result = tool._run(query="Test query")
        
        assert "Search failed" in result
        assert "quota exceeded" in result.lower()
    
    def test_check_balance(self, tool, mock_client):
        """Test balance checking"""
        mock_balance = BalanceResponse(available_credits=100)
        tool.client.balance = Mock(return_value=mock_balance)
        
        balance = tool.check_balance()
        
        assert balance['available_credits'] == 100
        assert balance['status'] == 'active'
    
    def test_context_history_management(self, tool, mock_client):
        """Test context history is maintained"""
        mock_response = SearchResponse(
            answer="Answer",
            sources=[],
            response_type="text",
            total_time=50
        )
        
        tool.client.search = Mock(return_value=mock_response)
        
        # Run multiple searches
        tool._run(query="First query")
        tool._run(query="Second query")
        
        # Check context history
        assert len(tool.context_history) == 2
        assert "First query" in tool.context_history[0].content
    
    def test_clear_context(self, tool):
        """Test clearing context history"""
        tool.context_history = [Mock(), Mock()]
        tool.clear_context()
        assert len(tool.context_history) == 0