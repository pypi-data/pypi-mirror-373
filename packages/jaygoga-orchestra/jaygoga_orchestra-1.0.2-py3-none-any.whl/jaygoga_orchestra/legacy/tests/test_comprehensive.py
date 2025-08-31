"""
Comprehensive test suite for AIFlow missing features implementation.
Tests each component 50 times to ensure reliability and correctness.
"""

import asyncio
import pytest
import tempfile
import json
import os
from pathlib import Path
from typing import Dict, Any, List
import sys

# Add aiflow to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from jaygoga_orchestra.knowledge.base import Knowledge
from jaygoga_orchestra.knowledge.readers import TextReader, JSONReader
from jaygoga_orchestra.knowledge.sources import TextKnowledgeBase, JSONKnowledgeBase
from jaygoga_orchestra.knowledge.rag_tool import RagTool
from jaygoga_orchestra.vectordb.base import VectorDBConfig, InMemoryVectorDB
from jaygoga_orchestra.vectordb.embedders import SimpleEmbedder
from jaygoga_orchestra.memory.base import MemoryConfig, MemoryEntry, MemoryType, MemoryImportance
from jaygoga_orchestra.memory.types import ShortTermMemory, LongTermMemory, EntityMemory
from jaygoga_orchestra.memory.manager import AdvancedMemoryManager
from jaygoga_orchestra.cli.base import CLIContext, CLIUtils

class TestKnowledgeManagement:
    """Test knowledge management components."""
    
    @pytest.mark.asyncio
    async def test_text_reader_reliability(self):
        """Test TextReader 50 times."""

        for i in range(50):
            # Create temporary text file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                test_content = f"Test content iteration {i}\nThis is line 2\nThis is line 3"
                f.write(test_content)
                temp_path = f.name

            try:
                # Create reader with the file path
                reader = TextReader(temp_path)

                # Test reading
                knowledge_list = await reader.read()
                assert len(knowledge_list) > 0, f"No knowledge returned on iteration {i}"
                content = knowledge_list[0].content
                assert content == test_content, f"Content mismatch on iteration {i}"

                # Test chunking
                chunks = await reader.chunk_content(content, chunk_size=20)
                assert len(chunks) > 0, f"No chunks created on iteration {i}"
                assert all(len(chunk) <= 25 for chunk in chunks), f"Chunk size exceeded on iteration {i}"

            finally:
                os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_json_reader_reliability(self):
        """Test JSONReader 50 times."""

        for i in range(50):
            # Create temporary JSON file
            test_data = {
                "iteration": i,
                "data": [f"item_{j}" for j in range(5)],
                "nested": {"key": f"value_{i}"}
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(test_data, f)
                temp_path = f.name

            try:
                # Create reader with the file path
                reader = JSONReader(temp_path)

                # Test reading
                knowledge_list = await reader.read()
                assert len(knowledge_list) > 0, f"No knowledge returned on iteration {i}"
                content = knowledge_list[0].content
                assert f"iteration: {i}" in content, f"Content missing on iteration {i}"

                # Test extraction
                extracted = await reader.extract_content(temp_path)
                assert extracted["iteration"] == i, f"Extraction failed on iteration {i}"

            finally:
                os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_knowledge_base_reliability(self):
        """Test knowledge base operations 50 times."""
        
        for i in range(50):
            # Create temporary text file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                content = f"Knowledge base test {i}\nThis contains important information about topic {i}."
                f.write(content)
                temp_path = f.name
            
            try:
                # Test knowledge base
                kb = TextKnowledgeBase(temp_path)
                knowledge_list = await kb.load()
                
                assert len(knowledge_list) > 0, f"No knowledge loaded on iteration {i}"
                assert all(isinstance(k, Knowledge) for k in knowledge_list), f"Invalid knowledge type on iteration {i}"
                assert any(f"topic {i}" in k.content for k in knowledge_list), f"Content not found on iteration {i}"
                
            finally:
                os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_rag_tool_reliability(self):
        """Test RAG tool 50 times."""
        
        for i in range(50):
            # Create knowledge sources
            knowledge_sources = []
            temp_files = []
            
            for j in range(3):  # 3 sources per test
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    content = f"Source {j} for test {i}\nThis contains information about subject {j}."
                    f.write(content)
                    temp_files.append(f.name)
                    knowledge_sources.append(TextKnowledgeBase(f.name))
            
            try:
                # Test RAG tool
                rag = RagTool(knowledge_sources)
                
                # Test retrieval
                results = await rag.retrieve(f"subject {i % 3}")
                assert len(results) > 0, f"No results on iteration {i}"
                
                # Test context generation
                context = await rag.get_context(f"subject {i % 3}")
                assert len(context) > 0, f"No context generated on iteration {i}"
                assert f"subject {i % 3}" in context.lower(), f"Context doesn't match query on iteration {i}"
                
            finally:
                for temp_file in temp_files:
                    os.unlink(temp_file)

class TestVectorDatabase:
    """Test vector database components."""
    
    @pytest.mark.asyncio
    async def test_in_memory_vector_db_reliability(self):
        """Test InMemoryVectorDB 50 times."""
        
        for i in range(50):
            config = VectorDBConfig(dimension=384)
            db = InMemoryVectorDB(config)
            
            await db.connect()
            
            try:
                # Create collection
                collection_name = f"test_collection_{i}"
                success = await db.create_collection(collection_name)
                assert success, f"Failed to create collection on iteration {i}"
                
                # Insert vectors
                vectors = [[0.1 * j for _ in range(384)] for j in range(5)]
                metadata = [{"id": j, "content": f"Document {j} for test {i}"} for j in range(5)]
                
                success = await db.insert(collection_name, vectors, metadata)
                assert success, f"Failed to insert vectors on iteration {i}"
                
                # Search vectors
                query_vector = [0.1 for _ in range(384)]
                results = await db.search(collection_name, query_vector, limit=3)
                
                assert len(results) > 0, f"No search results on iteration {i}"
                assert all(hasattr(r, 'score') for r in results), f"Missing scores on iteration {i}"
                
                # Test deletion
                await db.delete_collection(collection_name)
                
            finally:
                await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_embedder_reliability(self):
        """Test SimpleEmbedder 50 times."""

        embedder = SimpleEmbedder()

        for i in range(50):
            # Test single text embedding
            text = f"This is test text number {i} for embedding."
            embedding = await embedder.embed_text(text)

            assert isinstance(embedding, list), f"Invalid embedding type on iteration {i}"
            assert len(embedding) == embedder.get_dimension(), f"Wrong embedding dimension on iteration {i}"
            assert all(isinstance(x, float) for x in embedding), f"Invalid embedding values on iteration {i}"

            # Test batch embedding
            texts = [f"Batch text {j} for iteration {i}" for j in range(3)]
            embeddings = await embedder.embed_batch(texts)

            assert len(embeddings) == 3, f"Wrong batch size on iteration {i}"
            assert all(len(emb) == embedder.get_dimension() for emb in embeddings), f"Wrong batch dimensions on iteration {i}"

class TestMemorySystem:
    """Test memory system components."""
    
    @pytest.mark.asyncio
    async def test_memory_types_reliability(self):
        """Test different memory types 50 times."""
        
        for i in range(50):
            config = MemoryConfig()
            
            # Test ShortTermMemory
            short_term = ShortTermMemory(config)
            
            entry = MemoryEntry(
                id=f"test_{i}",
                content=f"Short term memory test {i}",
                memory_type=MemoryType.SHORT_TERM,
                importance=MemoryImportance.MEDIUM,
                metadata={"test_iteration": i},
                created_at=None,
                accessed_at=None,
                agent_id=f"agent_{i}",
                session_id=f"session_{i}"
            )
            
            success = await short_term.store(entry)
            assert success, f"Failed to store short term memory on iteration {i}"
            
            retrieved = await short_term.get_by_id(f"test_{i}")
            assert retrieved is not None, f"Failed to retrieve memory on iteration {i}"
            assert retrieved.content == f"Short term memory test {i}", f"Content mismatch on iteration {i}"
            
            # Test LongTermMemory
            long_term = LongTermMemory(config)
            
            entry.memory_type = MemoryType.LONG_TERM
            entry.content = f"Long term memory test {i}"
            
            success = await long_term.store(entry)
            assert success, f"Failed to store long term memory on iteration {i}"
            
            # Test EntityMemory
            entity_memory = EntityMemory(config)
            
            success = await entity_memory.add_entity_fact(
                entity_name=f"Entity_{i}",
                entity_type="test_entity",
                fact=f"This entity was created in test iteration {i}",
                agent_id=f"agent_{i}"
            )
            assert success, f"Failed to add entity fact on iteration {i}"
            
            entity_memories = await entity_memory.get_entity_memories(f"Entity_{i}")
            assert len(entity_memories) > 0, f"No entity memories found on iteration {i}"
    
    @pytest.mark.asyncio
    async def test_advanced_memory_manager_reliability(self):
        """Test AdvancedMemoryManager 50 times."""
        
        for i in range(50):
            config = MemoryConfig(enable_persistence=False)  # Use in-memory for testing
            manager = AdvancedMemoryManager(config)
            
            await manager.connect()
            
            try:
                # Test storing different types of memories
                success = await manager.add_interaction(
                    content=f"User interaction {i}",
                    agent_id=f"agent_{i}",
                    session_id=f"session_{i}"
                )
                assert success, f"Failed to add interaction on iteration {i}"
                
                success = await manager.add_fact(
                    content=f"Important fact {i}",
                    agent_id=f"agent_{i}"
                )
                assert success, f"Failed to add fact on iteration {i}"
                
                success = await manager.add_entity_fact(
                    entity_name=f"TestEntity_{i}",
                    entity_type="test",
                    fact=f"Entity fact {i}",
                    agent_id=f"agent_{i}"
                )
                assert success, f"Failed to add entity fact on iteration {i}"
                
                # Test retrieval
                memories = await manager.retrieve_memories(
                    query=f"interaction {i}",
                    agent_id=f"agent_{i}"
                )
                assert len(memories) > 0, f"No memories retrieved on iteration {i}"
                
                # Test context retrieval
                context = await manager.get_recent_context(
                    agent_id=f"agent_{i}",
                    session_id=f"session_{i}"
                )
                assert len(context) > 0, f"No context retrieved on iteration {i}"
                
                # Test entity memories
                entity_memories = await manager.get_entity_memories(f"TestEntity_{i}")
                assert len(entity_memories) > 0, f"No entity memories retrieved on iteration {i}"
                
            finally:
                await manager.disconnect()

class TestCLITools:
    """Test CLI tools components."""
    
    def test_cli_utils_reliability(self):
        """Test CLI utilities 50 times."""
        
        for i in range(50):
            # Test project name validation
            valid_names = [f"test_project_{i}", f"TestProject{i}", f"project{i}"]
            invalid_names = [f"test-project-{i}", f"123project{i}", "aiflow", ""]
            
            for name in valid_names:
                assert CLIUtils.validate_project_name(name), f"Valid name rejected on iteration {i}: {name}"
            
            for name in invalid_names:
                assert not CLIUtils.validate_project_name(name), f"Invalid name accepted on iteration {i}: {name}"
            
            # Test template content
            templates = CLIUtils.get_template_content("test")
            assert isinstance(templates, dict), f"Templates not dict on iteration {i}"
            assert "basic_agent" in templates, f"Missing basic_agent template on iteration {i}"
            
            # Test template formatting
            formatted = CLIUtils.format_template(
                "Hello {name}, iteration {number}",
                name=f"Test{i}",
                number=i
            )
            expected = f"Hello Test{i}, iteration {i}"
            assert formatted == expected, f"Template formatting failed on iteration {i}"
    
    def test_cli_context_reliability(self):
        """Test CLI context 50 times."""
        
        for i in range(50):
            with tempfile.TemporaryDirectory() as temp_dir:
                project_root = Path(temp_dir)
                
                context = CLIContext(
                    project_root=project_root,
                    verbose=i % 2 == 0,
                    debug=i % 3 == 0,
                    environment=f"test_env_{i}"
                )
                
                # Test config operations
                test_config = {
                    "name": f"test_project_{i}",
                    "version": f"1.0.{i}",
                    "iteration": i
                }
                
                success = context.save_config(test_config)
                assert success, f"Failed to save config on iteration {i}"
                
                loaded_config = context.load_config()
                assert loaded_config["iteration"] == i, f"Config mismatch on iteration {i}"
                assert loaded_config["name"] == f"test_project_{i}", f"Name mismatch on iteration {i}"

@pytest.mark.asyncio
async def test_integration_reliability():
    """Test integration between components 50 times."""
    
    for i in range(50):
        # Create a complete workflow test
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # 1. Create knowledge base
            knowledge_file = project_root / f"knowledge_{i}.txt"
            knowledge_file.write_text(f"Knowledge content for integration test {i}")
            
            kb = TextKnowledgeBase(str(knowledge_file))
            knowledge_list = await kb.load()
            assert len(knowledge_list) > 0, f"Knowledge loading failed on iteration {i}"
            
            # 2. Create RAG tool
            rag = RagTool([kb])
            context = await rag.get_context(f"test {i}")
            assert len(context) > 0, f"RAG context generation failed on iteration {i}"
            
            # 3. Create memory system
            config = MemoryConfig(enable_persistence=False)
            memory = AdvancedMemoryManager(config)
            await memory.connect()
            
            try:
                # Store RAG context in memory
                success = await memory.add_fact(
                    content=context[:100],  # Store first 100 chars
                    agent_id=f"integration_agent_{i}"
                )
                assert success, f"Memory storage failed on iteration {i}"
                
                # Retrieve from memory
                memories = await memory.retrieve_memories(
                    query=f"test {i}",
                    agent_id=f"integration_agent_{i}"
                )
                assert len(memories) > 0, f"Memory retrieval failed on iteration {i}"
                
            finally:
                await memory.disconnect()

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])