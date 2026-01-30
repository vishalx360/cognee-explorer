"""
Cognee Example: Building AI Memory from Text Data

This example demonstrates how to use Cognee to:
1. Add documents/text to the knowledge base
2. Process them into a knowledge graph (cognify)
3. Search the knowledge base

Configuration is loaded from .env file automatically.
"""

import asyncio
from dotenv import load_dotenv

# Load environment variables BEFORE importing cognee
load_dotenv()

import cognee


async def main():
    print("=" * 60)
    print("Cognee AI Memory Example")
    print("=" * 60)

    # Reset any previous data (optional, for clean runs)
    print("\n1. Resetting previous data...")
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)
    print("   Done!")

    # Sample documents about a fictional company
    documents = [
        """
        Acme Corporation was founded in 2020 by Alice Johnson and Bob Smith.
        The company specializes in sustainable energy solutions, particularly
        solar panel technology and battery storage systems.
        """,
        """
        Alice Johnson serves as the CEO of Acme Corporation. She previously
        worked at Tesla for 10 years as a senior engineer. Alice holds a PhD
        in Materials Science from MIT.
        """,
        """
        Bob Smith is the CTO of Acme Corporation. He is an expert in battery
        technology and holds 15 patents in energy storage. Bob was a co-founder
        of a previous startup called GreenTech that was acquired by Google.
        """,
        """
        Acme Corporation recently launched their flagship product called
        SolarMax 3000, a residential solar panel system with integrated
        battery storage. It can power an average home for 48 hours during
        outages.
        """,
    ]

    # Add documents to Cognee
    print("\n2. Adding documents to Cognee...")
    for i, doc in enumerate(documents, 1):
        await cognee.add(doc.strip())
        print(f"   Added document {i}/{len(documents)}")
    print("   Done!")

    # Process documents into knowledge graph
    print("\n3. Cognifying (building knowledge graph)...")
    print("   This extracts entities and relationships...")
    await cognee.cognify()
    print("   Done!")

    # Search the knowledge base
    print("\n4. Searching the knowledge base...")
    print("-" * 60)

    queries = [
        "Who founded Acme Corporation?",
        "What is the SolarMax 3000?",
        "What is Alice Johnson's background?",
        "What companies did Bob Smith work for before?",
    ]

    for query in queries:
        print(f"\nQ: {query}")
        try:
            results = await cognee.search(query)
            if results:
                # Handle different result formats
                result = results[0]
                if isinstance(result, str):
                    answer = result
                elif hasattr(result, 'text'):
                    answer = result.text
                elif isinstance(result, dict):
                    # Cognee returns search_result key with list of answers
                    search_result = result.get('search_result', [])
                    if search_result:
                        answer = search_result[0] if isinstance(search_result, list) else search_result
                    else:
                        answer = str(result)
                else:
                    answer = str(result)
                print(f"A: {answer}")
            else:
                print("A: No results found")
        except Exception as e:
            print(f"A: Error during search - {e}")

    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
