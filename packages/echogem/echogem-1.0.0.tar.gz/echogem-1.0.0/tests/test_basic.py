#!/usr/bin/env python3
"""
Basic tests for EchoGem
"""

import pytest
import os
from unittest.mock import Mock, patch

# Test imports
def test_imports():
    """Test that all modules can be imported"""
    try:
        from echogem import (
            Chunker,
            ChunkVectorDB,
            UsageCache,
            PromptAnswerVectorDB,
            PAPair,
            Processor,
            Chunk,
            ChunkResponse
        )
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_models():
    """Test data models"""
    from echogem.models import Chunk, ChunkResponse
    
    # Test Chunk model
    chunk = Chunk(
        title="Test Chunk",
        content="This is test content",
        keywords=["test", "content"],
        named_entities=["Test"],
        timestamp_range="00:00-01:00"
    )
    
    assert chunk.title == "Test Chunk"
    assert chunk.content == "This is test content"
    assert chunk.keywords == ["test", "content"]
    assert chunk.named_entities == ["Test"]
    assert chunk.timestamp_range == "00:00-01:00"
    
    # Test ChunkResponse model
    response = ChunkResponse(chunks=[chunk])
    assert len(response.chunks) == 1
    assert response.chunks[0].title == "Test Chunk"

def test_usage_cache():
    """Test usage cache functionality"""
    from echogem.usage_cache import UsageCache
    
    # Test with temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_path = f.name
    
    try:
        cache = UsageCache(temp_path)
        
        # Test blank row creation
        blank = cache._blank_row("test_id")
        assert blank["chunk_id"] == "test_id"
        assert blank["usage_count"] == 0
        
        # Test usage update
        cache.update_usage("test_id")
        chunk_data = cache.get_chunk("test_id")
        assert chunk_data is not None
        assert chunk_data["usage_count"] == 1
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key', 'PINECONE_API_KEY': 'test_key'})
def test_processor_initialization():
    """Test processor initialization with mocked dependencies"""
    from echogem.processor import Processor
    
    # Mock the external dependencies
    with patch('echogem.processor.GoogleGenerativeAIEmbeddings') as mock_embeddings, \
         patch('echogem.processor.ChatGoogleGenerativeAI') as mock_llm, \
         patch('echogem.processor.ChunkVectorDB') as mock_vdb, \
         patch('echogem.processor.UsageCache') as mock_cache, \
         patch('echogem.processor.PromptAnswerVectorDB') as mock_pa:
        
        # Mock the embedding model
        mock_emb_model = Mock()
        mock_embeddings.return_value = mock_emb_model
        
        # Mock the LLM
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance
        
        # Mock the vector database
        mock_vdb_instance = Mock()
        mock_vdb.return_value = mock_vdb_instance
        
        # Mock the usage cache
        mock_cache_instance = Mock()
        mock_cache.return_value = mock_cache_instance
        
        # Mock the prompt-answer store
        mock_pa_instance = Mock()
        mock_pa.return_value = mock_pa_instance
        
        # Initialize processor
        processor = Processor()
        
        # Verify components were created
        assert processor.embedding_model == mock_emb_model
        assert processor.llm == mock_llm_instance
        assert processor.vector_db == mock_vdb_instance
        assert processor.usage_cache == mock_cache_instance
        assert processor.pa_db == mock_pa_instance

def test_chunker():
    """Test chunker functionality"""
    from echogem.chunker import Chunker
    
    chunker = Chunker()
    
    # Test prompt creation
    prompt = chunker._create_prompt()
    assert "SYSTEM PROMPT" in prompt.template
    assert "TRANSCRIPT" in prompt.template
    assert "OUTPUT FORMAT" in prompt.template

if __name__ == "__main__":
    pytest.main([__file__])
