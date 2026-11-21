"""Core Autonomous AI Agent logic for real estate rent prediction and advisory."""

import os
import re
import json
from typing import Dict, Any, List, Optional
from rent_agent.agent.tools import AgentTools
from rent_agent.agent.prompts import AGENT_SYSTEM_PROMPT
from rent_agent.config import CITY_METRICS


class RentPredictionAgent:
    """Intelligent autonomous agent for rent forecasting and market advisory."""

    def __init__(self, api_key: Optional[str] = None):
        self.tools = AgentTools()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.history: List[Dict[str, str]] = []

    def run_valuation(self, property_specs: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete valuation workflow: prediction + comps + market context."""
        prediction = self.tools.predict_rent(property_specs)
        comps = self.tools.find_comparables(property_specs, top_k=4)
        city = property_specs.get("city", "Chicago")
        trends = self.tools.get_market_trends(city)

        return {
            "valuation": prediction,
            "comparables": comps,
            "market_trends": trends,
        }

    def chat(self, user_message: str) -> str:
        """Process conversational user inquiry and return synthesized analysis."""
        self.history.append({"role": "user", "content": user_message})

        # Check if external LLM client should be initialized
        if self.api_key and os.getenv("GEMINI_API_KEY"):
            try:
                response_text = self._chat_with_gemini(user_message)
                self.history.append({"role": "assistant", "content": response_text})
                return response_text
            except Exception:
                pass  # Fallback to local heuristic agent

        # Autonomous local reasoning engine
        response_text = self._local_reasoning_pipeline(user_message)
        self.history.append({"role": "assistant", "content": response_text})
        return response_text

    def _local_reasoning_pipeline(self, query: str) -> str:
        """Domain-specific local ReAct intent dispatcher with tool invocation."""
        lower_q = query.lower()

        # Intent 1: Investment ROI / Cap Rate inquiry
        if any(w in lower_q for w in ["roi", "cap rate", "investment", "cash flow", "buy to rent"]):
            price_match = re.search(r"\$?([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{5,7})", query)
            rent_match = re.search(r"rent(?:\s+it)?(?:\s+for|\s+at|\s+of)?\s*\$?([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{3,5})", query, re.IGNORECASE)
            price = float(price_match.group(1).replace(",", "")) if price_match else 400000.0
            rent = float(rent_match.group(1).replace(",", "")) if rent_match else 2400.0

            roi = self.tools.calculate_roi(purchase_price=price, monthly_rent=rent)
            return (
                f"### 📈 Real Estate Investment Analysis\n\n"
                f"- **Purchase Price:** ${price:,.0f}\n"
                f"- **Projected Monthly Rent:** ${rent:,.0f}\n"
                f"- **Capitalization Rate (Cap Rate):** **{roi['cap_rate_pct']}%**\n"
                f"- **Gross Rental Yield:** **{roi['gross_rental_yield_pct']}%**\n"
                f"- **Estimated Monthly Cash Flow:** **${roi['monthly_net_cash_flow']:,.2f}**\n"
                f"- **Cash-on-Cash Return:** **{roi['cash_on_cash_return_pct']}%**\n"
                f"- **1% Rule Status:** {'✅ Met' if roi['meets_1_percent_rule'] else '⚠️ Below 1% guideline'}\n\n"
                f"**Investment Verdict:** {roi['verdict']}"
            )

        # Intent 2: Negotiation strategy inquiry
        if any(w in lower_q for w in ["negotiat", "lower rent", "asking", "landlord wants", "raise"]):
            asking_match = re.search(r"\$?([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{3,6})", query)
            asking_price = float(asking_match.group(1).replace(",", "")) if asking_match else 2500.0
            city = self._detect_city(query) or "Chicago"
            fair_rent = asking_price * 0.92  # approximate baseline

            strat = self.tools.generate_negotiation_strategy(
                asking_rent=asking_price,
                predicted_rent=fair_rent,
                city=city,
            )

            tactics_md = "\n".join(f"- {t}" for t in strat["leverage_points"])
            concessions_md = "\n".join(f"- {c}" for c in strat["alternative_concessions"])

            return (
                f"### 🤝 Lease Negotiation Playbook ({city})\n\n"
                f"- **Asking Rent:** ${strat['asking_rent']:,.0f}\n"
                f"- **Recommended Target Offer:** **${strat['recommended_target_offer']:,}/mo**\n"
                f"- **Potential Annual Savings:** **${strat['annual_savings_potential']:,}**\n"
                f"- **Tenant Leverage Score:** **{strat['negotiation_leverage_score']} / 100**\n\n"
                f"#### Key Leverage Arguments:\n{tactics_md}\n\n"
                f"#### Alternative Concessions to Request:\n{concessions_md}\n\n"
                f"#### ✉️ Ready-to-Send Email Script:\n```text\n{strat['sample_email_script']}\n```"
            )

        # Intent 3: General Rent Valuation / Prediction
        city = self._detect_city(query) or "New York"
        beds = self._detect_number(query, ["bed", "br", "bedroom"]) or 2
        baths = self._detect_number(query, ["bath", "ba", "bathroom"]) or 1.5
        sqft = self._detect_number(query, ["sqft", "sq ft", "square feet"]) or (650 if beds <= 1 else 1050)

        amenities = {
            "in_unit_washer_dryer": "laundry" in lower_q or "washer" in lower_q,
            "parking_spot": "parking" in lower_q or "garage" in lower_q,
            "private_balcony": "balcony" in lower_q or "patio" in lower_q,
            "central_ac": "ac" in lower_q or "air conditioning" in lower_q,
            "pet_friendly": "pet" in lower_q or "dog" in lower_q or "cat" in lower_q,
            "furnished": "furnished" in lower_q,
        }

        prop_specs = {
            "city": city,
            "property_type": "Apartment",
            "bedrooms": beds,
            "bathrooms": baths,
            "sqft": sqft,
            "amenities": amenities,
        }

        res = self.run_valuation(prop_specs)
        v = res["valuation"]
        m = res["market_trends"]

        comps_md = ""
        for i, comp in enumerate(res["comparables"][:3], 1):
            comps_md += f"  {i}. **{comp['neighborhood']}** - {comp['bedrooms']} bed, {comp['bathrooms']} bath ({comp['sqft']} sqft): **${comp['monthly_rent']:,}/mo** (Similarity: {comp['similarity_pct']})\n"

        return (
            f"### 🏠 Fair Market Rent Valuation\n\n"
            f"**Location:** {city} | **Layout:** {beds} Bed, {baths} Bath ({sqft} sqft)\n\n"
            f"- **Estimated Monthly Rent:** **${v['predicted_monthly_rent']:,}/month**\n"
            f"- **Fair Market Range (90% CI):** **${v['fair_market_range']['min']:,} - ${v['fair_market_range']['max']:,}**\n"
            f"- **Price Per Sq Ft:** **${v['price_per_sqft']}/sqft**\n"
            f"- **City Market Temperature:** {m.get('market_temperature', 'Normal')}\n"
            f"- **City Vacancy Rate:** {m.get('vacancy_rate_pct', 'N/A')}\n\n"
            f"#### 📍 Top Nearby Comparable Listings:\n{comps_md}\n"
            f"💡 *Tip: You can ask me to draft a negotiation counter-offer or run an investment ROI analysis on this property!*"
        )

    def _detect_city(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for city in CITY_METRICS.keys():
            if city.lower() in text_lower:
                return city
        if "ny" in text_lower or "nyc" in text_lower or "manhattan" in text_lower or "brooklyn" in text_lower:
            return "New York"
        if "sf" in text_lower or "bay area" in text_lower:
            return "San Francisco"
        if "la" in text_lower:
            return "Los Angeles"
        return None

    def _detect_number(self, text: str, keywords: List[str]) -> Optional[float]:
        for kw in keywords:
            pattern = rf"(\d+(?:\.\d+)?)\s*(?:-|–)?\s*{kw}"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
            pattern2 = rf"{kw}\s*(?:of|:)?\s*(\d+(?:\.\d+)?)"
            match2 = re.search(pattern2, text, re.IGNORECASE)
            if match2:
                return float(match2.group(1))
        return None

    def _chat_with_gemini(self, user_prompt: str) -> str:
        """Call Gemini API when API key is configured."""
        import urllib.request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{AGENT_SYSTEM_PROMPT}\n\nUser Question: {user_prompt}"}]}
            ]
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]
