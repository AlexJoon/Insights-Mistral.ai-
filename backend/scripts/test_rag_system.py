#!/usr/bin/env python3
"""
Quick test script for RAG system.
Tests Pinecone connection and basic functionality.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_db.factory import VectorDatabaseFactory
from backend.services.embedding_service import EmbeddingService
from backend.config.settings import load_config


async def test_pinecone_connection():
    """Test Pinecone connection."""
    print("=" * 60)
    print("Testing Pinecone Connection")
    print("=" * 60)

    try:
        # Create Pinecone adapter from env
        db = VectorDatabaseFactory.create_from_env('pinecone')
        print("✓ Pinecone adapter created")

        # Initialize
        await db.initialize()
        print("✓ Pinecone initialized")

        # Health check
        health = await db.health_check()
        if health:
            print("✓ Pinecone health check passed")
        else:
            print("✗ Pinecone health check failed")
            return False

        # Get stats
        stats = await db.get_stats()
        print(f"\n📊 Pinecone Stats:")
        print(f"  - Total vectors: {stats.get('total_vectors', 0)}")
        print(f"  - Dimension: {stats.get('dimension', 'N/A')}")
        print(f"  - Index fullness: {stats.get('index_fullness', 'N/A')}")

        return True

    except Exception as e:
        print(f"✗ Pinecone test failed: {e}")
        return False


async def test_embeddings():
    """Test Mistral embeddings."""
    print("\n" + "=" * 60)
    print("Testing Mistral Embeddings")
    print("=" * 60)

    try:
        config = load_config()
        service = EmbeddingService(config.mistral.api_key)

        # Generate test embedding
        result = await service.generate_embedding("This is a test sentence.")
        print(f"✓ Generated embedding")
        print(f"  - Dimension: {result.dimension}")
        print(f"  - Tokens used: {result.tokens_used}")

        return True

    except Exception as e:
        print(f"✗ Embedding test failed: {e}")
        return False


async def test_end_to_end():
    """Test uploading a chunk and searching for it."""
    print("\n" + "=" * 60)
    print("Testing End-to-End RAG Pipeline")
    print("=" * 60)

    try:
        config = load_config()

        # Initialize services
        db = VectorDatabaseFactory.create_from_env('pinecone')
        await db.initialize()

        embedding_service = EmbeddingService(config.mistral.api_key)

        # Test content
        test_content = """
        CS101 - Introduction to Programming
        Grading Policy: Exams 40%, Projects 40%, Participation 20%
        Instructor: Dr. Jane Smith
        Office Hours: Monday 2-4pm
        """

        print("\n1. Generating embedding for test content...")
        embedding_result = await embedding_service.generate_embedding(test_content)

        print("2. Uploading to Pinecone...")
        await db.upsert_vectors(
            ids=["test_chunk_1"],
            vectors=[embedding_result.embedding],
            metadata=[{
                "content": test_content,
                "course_code": "CS101",
                "document_id": "test_syllabus",
                "instructor": "Dr. Jane Smith"
            }]
        )
        print("✓ Test chunk uploaded")

        print("\n3. Searching for similar content...")
        query = "What is the grading policy?"
        query_embedding = await embedding_service.embed_query(query)

        results = await db.search(
            query_vector=query_embedding,
            top_k=3,
            filter={"course_code": "CS101"}
        )

        if results:
            print(f"✓ Found {len(results)} results")
            for i, result in enumerate(results, 1):
                print(f"\n  Result {i}:")
                print(f"    - ID: {result.id}")
                print(f"    - Score: {result.similarity_score:.3f}")
                print(f"    - Content preview: {result.content[:100]}...")
        else:
            print("✗ No results found")

        print("\n4. Cleaning up test data...")
        await db.delete_by_id(["test_chunk_1"])
        print("✓ Test chunk deleted")

        return True

    except Exception as e:
        print(f"✗ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n🧪 RAG System Test Suite\n")

    results = []

    # Test 1: Pinecone connection
    result1 = await test_pinecone_connection()
    results.append(("Pinecone Connection", result1))

    # Test 2: Embeddings
    result2 = await test_embeddings()
    results.append(("Mistral Embeddings", result2))

    # Test 3: End-to-end
    result3 = await test_end_to_end()
    results.append(("End-to-End Pipeline", result3))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<40} {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All tests passed! Your RAG system is ready.")
        print("\nNext steps:")
        print("  1. Upload your syllabi:")
        print("     python scripts/upload_syllabi.py ~/Desktop/syllabi/")
        print("\n  2. Start querying:")
        print("     See RAG_SETUP_GUIDE.md for examples")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")
        print("   - Verify PINECONE_API_KEY in .env")
        print("   - Verify MISTRAL_API_KEY in .env")
        print("   - Check network connection")

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
