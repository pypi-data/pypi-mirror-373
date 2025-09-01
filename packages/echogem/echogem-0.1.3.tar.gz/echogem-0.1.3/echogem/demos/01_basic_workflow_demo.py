#!/usr/bin/env python3
"""
EchoGem Basic Workflow Demo
===========================

This demo shows the basic workflow of processing a transcript
and asking questions using the EchoGem library.

Prerequisites:
- Set GOOGLE_API_KEY environment variable
- Set PINECONE_API_KEY environment variable
"""

import os
import sys
import time
from pathlib import Path

# Add the parent directory to Python path to import echogem
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["GOOGLE_API_KEY", "PINECONE_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables:")
        print("   export GOOGLE_API_KEY='your-google-api-key'")
        print("   export PINECONE_API_KEY='your-pinecone-api-key'")
        return False
    
    print("✅ Environment variables configured")
    return True

def demo_basic_workflow():
    """Demonstrate the basic EchoGem workflow"""
    print("\n" + "="*60)
    print("BASIC WORKFLOW DEMO")
    print("="*60)
    
    try:
        from echogem.processor import Processor
        from echogem.models import ChunkingOptions, QueryOptions
        
        print("\n1. Initializing EchoGem processor...")
        processor = Processor()
        print("   ✓ Processor initialized successfully")
        
        # Check if we have a transcript file
        transcript_path = Path("../examples/sample_transcript.txt")
        if not transcript_path.exists():
            print(f"\n❌ Transcript file not found: {transcript_path}")
            print("   Please ensure the sample transcript exists")
            return False
        
        print(f"\n2. Processing transcript: {transcript_path.name}")
        start_time = time.time()
        
        # Process with custom options
        chunking_opts = ChunkingOptions(
            chunk_size=800,
            overlap=150,
            semantic_chunking=True,
            show_chunks=True
        )
        
        response = processor.chunk_and_process(str(transcript_path), chunking_opts)
        processing_time = time.time() - start_time
        
        if response.success:
            print(f"   ✓ Successfully processed {response.num_chunks} chunks")
            print(f"   ✓ Processing time: {processing_time:.2f} seconds")
            
            # Show chunk details if requested
            if hasattr(response, 'chunks') and response.chunks:
                print(f"\n   Chunk details:")
                for i, chunk in enumerate(response.chunks[:3], 1):  # Show first 3 chunks
                    print(f"   {i}. {chunk.title}")
                    print(f"      Content: {chunk.content[:100]}...")
                    print(f"      Keywords: {', '.join(chunk.keywords[:5])}")
        else:
            print(f"   ❌ Processing failed: {response.error_message}")
            return False
        
        print(f"\n3. Asking questions about the transcript...")
        
        # Define some questions to ask
        questions = [
            "What is the main topic of this meeting?",
            "Who are the participants and what are their roles?",
            "What are the key concerns about AI implementation?",
            "What is the timeline for FDA approval?",
            "What security measures are being implemented?"
        ]
        
        # Configure query options
        query_opts = QueryOptions(
            top_k=5,
            similarity_threshold=0.6,
            show_chunks=True,
            show_metadata=True
        )
        
        total_query_time = 0
        successful_queries = 0
        
        for i, question in enumerate(questions, 1):
            print(f"\n   Q{i}: {question}")
            
            try:
                start_time = time.time()
                result = processor.answer_question(question, query_opts)
                query_time = time.time() - start_time
                total_query_time += query_time
                successful_queries += 1
                
                print(f"   A: {result.answer}")
                print(f"   Confidence: {result.confidence:.2f}")
                print(f"   Query time: {query_time:.2f}s")
                
                if hasattr(result, 'chunks_used') and result.chunks_used:
                    print(f"   Chunks used: {len(result.chunks_used)}")
                
            except Exception as e:
                print(f"   ❌ Error answering question: {e}")
        
        print(f"\n4. Performance Summary:")
        print(f"   ✓ Successful queries: {successful_queries}/{len(questions)}")
        if successful_queries > 0:
            print(f"   ✓ Average query time: {total_query_time/successful_queries:.2f}s")
            print(f"   ✓ Total processing time: {processing_time + total_query_time:.2f}s")
        
        print(f"\n5. Getting system statistics...")
        try:
            stats = processor.get_stats()
            print(f"   ✓ Total chunks: {stats.get('total_chunks', 'N/A')}")
            print(f"   ✓ Total queries: {stats.get('total_queries', 'N/A')}")
            print(f"   ✓ Cache hit rate: {stats.get('cache_hit_rate', 'N/A')}")
        except Exception as e:
            print(f"   ⚠️  Could not retrieve statistics: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running this from the correct directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def demo_cli_commands():
    """Show the CLI commands that can be used"""
    print("\n" + "="*60)
    print("CLI COMMANDS DEMO")
    print("="*60)
    
    print("\nYou can also use EchoGem from the command line:")
    print("\n1. Process transcript:")
    print("   py -m echogem.cli process ../examples/sample_transcript.txt --show-chunks")
    
    print("\n2. Ask questions:")
    print("   py -m echogem.cli ask 'What is the main topic discussed?'")
    print("   py -m echogem.cli ask 'Who are the key speakers?' --show-chunks --show-metadata")
    
    print("\n3. Interactive mode:")
    print("   py -m echogem.cli interactive")
    
    print("\n4. Visualize information graph:")
    print("   py -m echogem.cli graph")
    
    print("\n5. System statistics:")
    print("   py -m echogem.cli stats")

def main():
    """Main demo function"""
    print("🚀 EchoGem Basic Workflow Demo")
    print("="*60)
    
    # Check environment
    if not check_environment():
        print("\n⚠️  Please set the required environment variables first.")
        print("   You can still view the demo workflow below.")
    
    # Run the basic workflow demo
    success = demo_basic_workflow()
    
    if success:
        print("\n🎉 Demo completed successfully!")
    else:
        print("\n❌ Demo encountered errors. Please check the output above.")
    
    # Show CLI commands
    demo_cli_commands()
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("\n💡 Try these next:")
    print("   1. Run the CLI commands shown above")
    print("   2. Explore the interactive mode")
    print("   3. Launch the graph visualization")
    print("   4. Check out other demo files")
    
    print("\n📚 For more information:")
    print("   - User Guide: ../docs/USER_GUIDE.md")
    print("   - API Reference: ../docs/API_REFERENCE.md")
    print("   - CLI Guide: ../docs/CLI_GUIDE.md")

if __name__ == "__main__":
    main()
