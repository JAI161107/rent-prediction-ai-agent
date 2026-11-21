"""Quick interactive demo showcase for ApexRent AI Agent."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rent_agent.agent.core import RentPredictionAgent


def main():
    print("=" * 70)
    print("🏢 APEXRENT AI AGENT - FULL CAPABILITIES SHOWCASE")
    print("=" * 70)

    agent = RentPredictionAgent()

    queries = [
        "What is the estimated fair rent for a 2-bedroom 2-bath apartment in Chicago West Loop with in-unit laundry and parking?",
        "My landlord is asking $3,400 in Austin, but it has been on the market for 40 days. How do I negotiate?",
        "If I buy a property in Miami for $420,000 and rent it for $2,700/mo, what is my cap rate and cash flow?",
    ]

    for i, q in enumerate(queries, 1):
        print(f"\n[Test Case #{i}] User: \"{q}\"")
        print("-" * 70)
        response = agent.chat(q)
        print(response)
        print("-" * 70)

    print("\n✅ Showcase completed successfully!")


if __name__ == "__main__":
    main()
