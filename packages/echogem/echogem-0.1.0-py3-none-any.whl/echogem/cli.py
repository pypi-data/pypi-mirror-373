#!/usr/bin/env python3
"""
Command-line interface for EchoGem library.
"""

import argparse
import os
import sys
from typing import Optional
from .processor import Processor


def setup_environment():
    """Check and setup required environment variables"""
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


def process_transcript(processor: Processor, file_path: str, show_chunks: bool = False):
    """Process a transcript file"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        processor.chunk_and_process(file_path, output_chunks=show_chunks)
        print(f"✅ Successfully processed transcript: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error processing transcript: {e}")
        return False


def ask_question(processor: Processor, question: str, show_chunks: bool = False, show_metadata: bool = False):
    """Ask a question and get an answer"""
    try:
        result = processor.answer_question(
            question, 
            show_chunks=show_chunks, 
            show_metadata=show_metadata
        )
        
        print(f"\n🤖 ANSWER:")
        print(f"{result.answer}")
        
        if result.chunks_used:
            print(f"\n📊 Used {len(result.chunks_used)} chunks (confidence: {result.confidence:.2f})")
        
        return True
    except Exception as e:
        print(f"❌ Error answering question: {e}")
        return False


def interactive_mode(processor: Processor):
    """Run in interactive mode for asking multiple questions"""
    print("\n🎯 Interactive Mode - Ask questions about your transcript!")
    print("Type 'quit' or 'exit' to end, 'help' for commands")
    
    while True:
        try:
            question = input("\n❓ Question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif question.lower() in ['help', 'h']:
                print("\n📚 Available commands:")
                print("  help, h     - Show this help")
                print("  quit, exit, q - Exit interactive mode")
                print("  stats       - Show system statistics")
                print("  clear       - Clear all data")
                print("  chunks <k>  - Show top k chunks for a question")
                print("  Any other text will be treated as a question")
                continue
            elif question.lower() == 'stats':
                stats = processor.get_stats()
                print(f"\n📊 System Statistics:")
                print(f"  Usage cache size: {stats.get('usage_cache_size', 'N/A')}")
                print(f"  Chunk index: {stats.get('chunks', 'N/A')}")
                print(f"  PA index: {stats.get('prompt_answers', 'N/A')}")
                continue
            elif question.lower() == 'clear':
                confirm = input("⚠️  This will delete ALL data. Are you sure? (yes/no): ")
                if confirm.lower() == 'yes':
                    processor.clear_all_data()
                    print("✅ All data cleared")
                continue
            elif question.lower().startswith('chunks '):
                try:
                    k = int(question.split()[1])
                    test_question = input("Enter a question to find relevant chunks: ").strip()
                    chunks = processor.pick_chunks(test_question, k=k)
                    if chunks:
                        print(f"\n📝 Top {len(chunks)} relevant chunks:")
                        for i, chunk in enumerate(chunks, 1):
                            print(f"\n{i}. {chunk.title}")
                            print(f"   Content: {chunk.content[:150]}...")
                            print(f"   Keywords: {chunk.keywords}")
                    else:
                        print("❌ No chunks found")
                except (ValueError, IndexError):
                    print("❌ Usage: chunks <number>")
                continue
            elif not question:
                continue
            
            # Process the question
            ask_question(processor, question, show_chunks=False, show_metadata=False)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="EchoGem - Intelligent Transcript Processing and Question Answering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a transcript file
  echogem process transcript.txt
  
  # Process and show chunk details
  echogem process transcript.txt --show-chunks
  
  # Ask a single question
  echogem ask "What is the main topic discussed?"
  
  # Ask with chunk details
  echogem ask "What is the main topic discussed?" --show-chunks --show-metadata
  
  # Interactive mode
  echogem interactive
  
  # Show system statistics
  echogem stats
  
  # Clear all data
  echogem clear
  
  # Visualize information graph
  echogem graph
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process a transcript file')
    process_parser.add_argument('file', help='Path to transcript file')
    process_parser.add_argument('--show-chunks', action='store_true', help='Show chunk details')
    
    # Ask command
    ask_parser = subparsers.add_parser('ask', help='Ask a question')
    ask_parser.add_argument('question', help='Question to ask')
    ask_parser.add_argument('--show-chunks', action='store_true', help='Show retrieved chunks')
    ask_parser.add_argument('--show-metadata', action='store_true', help='Show chunk metadata')
    
    # Interactive command
    subparsers.add_parser('interactive', help='Run in interactive mode')
    
    # Stats command
    subparsers.add_parser('stats', help='Show system statistics')
    
    # Clear command
    subparsers.add_parser('clear', help='Clear all stored data')
    
    # Graph command
    graph_parser = subparsers.add_parser('graph', help='Visualize information graph')
    graph_parser.add_argument('--usage-cache', default="usage_cache_store.csv", 
                             help='Path to usage cache CSV file')
    graph_parser.add_argument('--width', type=int, default=1200, help='Screen width')
    graph_parser.add_argument('--height', type=int, default=800, help='Screen height')
    graph_parser.add_argument('--export', help='Export graph to JSON file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Check environment (except for graph command)
    if args.command != 'graph' and not setup_environment():
        sys.exit(1)
    
    try:
        if args.command == 'graph':
            # Import and run graph visualizer
            from .graphe import GraphVisualizer
            
            visualizer = GraphVisualizer(
                usage_cache_path=args.usage_cache,
                screen_width=args.width,
                screen_height=args.height
            )
            
            if args.export:
                visualizer.export_graph(args.export)
            else:
                visualizer.run()
                
        else:
            # Initialize processor for other commands
            processor = Processor()
            
            if args.command == 'process':
                success = process_transcript(processor, args.file, args.show_chunks)
                sys.exit(0 if success else 1)
                
            elif args.command == 'ask':
                success = ask_question(processor, args.question, args.show_chunks, args.show_metadata)
                sys.exit(0 if success else 1)
                
            elif args.command == 'interactive':
                interactive_mode(processor)
                
            elif args.command == 'stats':
                stats = processor.get_stats()
                print(f"\n📊 System Statistics:")
                print(f"  Usage cache size: {stats.get('usage_cache_size', 'N/A')}")
                print(f"  Chunk index: {stats.get('chunks', 'N/A')}")
                print(f"  PA index: {stats.get('prompt_answers', 'N/A')}")
                
            elif args.command == 'clear':
                confirm = input("⚠️  This will delete ALL data. Are you sure? (yes/no): ")
                if confirm.lower() == 'yes':
                    processor.clear_all_data()
                    print("✅ All data cleared")
                else:
                    print("❌ Operation cancelled")
                    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
