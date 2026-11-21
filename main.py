"""Command-line interface (CLI) entry point for ApexRent AI Agent."""

import argparse
import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rent_agent.agent.core import RentPredictionAgent
from rent_agent.models.trainer import train_and_calibrate
from rent_agent.config import CITY_METRICS


def cmd_predict(args):
    """Run rent valuation on specified property features."""
    agent = RentPredictionAgent()
    specs = {
        "city": args.city,
        "neighborhood": args.neighborhood or "",
        "property_type": args.type,
        "bedrooms": args.beds,
        "bathrooms": args.baths,
        "sqft": args.sqft,
        "year_built": args.year,
        "condition": args.condition,
        "amenities": {
            "in_unit_washer_dryer": args.laundry,
            "parking_spot": args.parking,
            "private_balcony": args.balcony,
            "central_ac": args.ac,
            "pet_friendly": args.pets,
        },
    }

    result = agent.tools.predict_rent(specs)
    print("\n" + "=" * 60)
    print(f"🏠 APEXRENT AI VALUATION REPORT - {args.city.upper()}")
    print("=" * 60)
    print(f"Property: {args.beds} Bed, {args.baths} Bath ({args.sqft} sqft) - {args.type}")
    print(f"Predicted Fair Monthly Rent: ${result['predicted_monthly_rent']:,} / month")
    print(f"Fair Market Range (90% CI): ${result['fair_market_range']['min']:,} - ${result['fair_market_range']['max']:,}")
    print(f"Price per Sq Ft:             ${result['price_per_sqft']}/sqft")
    print(f"Market Percentile:           Top {100 - result['market_percentile']}% in {args.city}")
    print("\nValuation Breakdown:")
    for k, v in result["valuation_breakdown"].items():
        if k != "amenity_breakdown":
            print(f"  • {k.replace('_', ' ').title()}: {v}")
    print("=" * 60 + "\n")


def cmd_chat(args):
    """Start interactive terminal chat session with the AI Agent."""
    agent = RentPredictionAgent()
    print("\n🤖 ApexRent AI Agent Interactive Console")
    print("Type your questions (e.g. 'predict rent for 2bed in Seattle with parking' or 'quit' to exit).\n")

    while True:
        try:
            user_input = input("You > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break

            response = agent.chat(user_input)
            print(f"\n{response}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


def cmd_comps(args):
    """Find comparable listings."""
    agent = RentPredictionAgent()
    specs = {
        "city": args.city,
        "bedrooms": args.beds,
        "bathrooms": args.baths,
        "sqft": args.sqft,
    }
    comps = agent.tools.find_comparables(specs, top_k=args.limit)
    print(f"\n📍 Top {len(comps)} Comparable Listings in {args.city}:")
    print("-" * 65)
    for c in comps:
        print(f"• ID: {c['id']} | {c['neighborhood']} ({c['property_type']})")
        print(f"  Specs: {c['bedrooms']} bed, {c['bathrooms']} bath, {c['sqft']} sqft")
        print(f"  Rent:  ${c['monthly_rent']:,}/mo | Similarity: {c['similarity_pct']}")
        print("-" * 65)


def cmd_roi(args):
    """Calculate real estate investment returns."""
    agent = RentPredictionAgent()
    res = agent.tools.calculate_roi(
        purchase_price=args.price,
        monthly_rent=args.rent,
        down_payment_pct=args.down / 100.0,
        monthly_hoa=args.hoa,
    )
    print("\n" + "=" * 55)
    print("💰 REAL ESTATE INVESTMENT ROI ANALYSIS")
    print("=" * 55)
    print(f"Purchase Price:       ${args.price:,.0f}")
    print(f"Monthly Rent:         ${args.rent:,.0f}")
    print(f"Cap Rate:             {res['cap_rate_pct']}%")
    print(f"Gross Rental Yield:   {res['gross_rental_yield_pct']}%")
    print(f"Monthly Net Cashflow: ${res['monthly_net_cash_flow']:,.2f}")
    print(f"Cash-on-Cash Return:  {res['cash_on_cash_return_pct']}%")
    print(f"1% Rule Passed:       {'Yes' if res['meets_1_percent_rule'] else 'No'}")
    print(f"Verdict:              {res['verdict']}")
    print("=" * 55 + "\n")


def cmd_train(args):
    """Retrain and evaluate model weights."""
    print("Starting model training pipeline...")
    model, metrics = train_and_calibrate()
    print("\nEvaluation Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")


def cmd_api(args):
    """Run REST API server."""
    from rent_agent.api.app import app, run_simple_server
    if app:
        import uvicorn
        print(f"Launching FastAPI on port {args.port}...")
        uvicorn.run("rent_agent.api.app:app", host="0.0.0.0", port=args.port, reload=True)
    else:
        print(f"Launching Standalone HTTP Server on port {args.port}...")
        run_simple_server(port=args.port)


def cmd_ui(args):
    """Run Streamlit dashboard."""
    import subprocess
    cmd = [sys.executable, "-m", "streamlit", "run", "rent_agent/ui/dashboard.py"]
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(
        description="ApexRent AI - Real Estate Rent Prediction Agent & Valuation Suite",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Predict
    p_pred = subparsers.add_parser("predict", help="Estimate rent for a property")
    p_pred.add_argument("--city", default="Chicago", choices=list(CITY_METRICS.keys()))
    p_pred.add_argument("--neighborhood", default=None)
    p_pred.add_argument("--type", default="Apartment")
    p_pred.add_argument("--beds", type=int, default=2)
    p_pred.add_argument("--baths", type=float, default=1.5)
    p_pred.add_argument("--sqft", type=int, default=950)
    p_pred.add_argument("--year", type=int, default=2015)
    p_pred.add_argument("--condition", default="Standard / Well Maintained")
    p_pred.add_argument("--laundry", action="store_true", help="In-unit laundry")
    p_pred.add_argument("--parking", action="store_true", help="Parking spot included")
    p_pred.add_argument("--balcony", action="store_true", help="Private balcony")
    p_pred.add_argument("--ac", action="store_true", help="Central AC")
    p_pred.add_argument("--pets", action="store_true", help="Pet friendly")
    p_pred.set_defaults(func=cmd_predict)

    # Chat
    p_chat = subparsers.add_parser("chat", help="Interactive conversational AI agent")
    p_chat.set_defaults(func=cmd_chat)

    # Comps
    p_comps = subparsers.add_parser("comps", help="Search comparable listings")
    p_comps.add_argument("--city", default="Chicago")
    p_comps.add_argument("--beds", type=int, default=2)
    p_comps.add_argument("--baths", type=float, default=1.5)
    p_comps.add_argument("--sqft", type=int, default=950)
    p_comps.add_argument("--limit", type=int, default=5)
    p_comps.set_defaults(func=cmd_comps)

    # ROI
    p_roi = subparsers.add_parser("roi", help="Calculate investment returns and cap rate")
    p_roi.add_argument("--price", type=float, required=True, help="Purchase price ($)")
    p_roi.add_argument("--rent", type=float, required=True, help="Expected monthly rent ($)")
    p_roi.add_argument("--down", type=float, default=20.0, help="Down payment percent (e.g. 20)")
    p_roi.add_argument("--hoa", type=float, default=250.0, help="Monthly HOA fee ($)")
    p_roi.set_defaults(func=cmd_roi)

    # Train
    p_train = subparsers.add_parser("train", help="Train and calibrate valuation model")
    p_train.set_defaults(func=cmd_train)

    # API
    p_api = subparsers.add_parser("api", help="Start REST API backend")
    p_api.add_argument("--port", type=int, default=8000)
    p_api.set_defaults(func=cmd_api)

    # UI
    p_ui = subparsers.add_parser("ui", help="Start Streamlit web dashboard")
    p_ui.set_defaults(func=cmd_ui)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
