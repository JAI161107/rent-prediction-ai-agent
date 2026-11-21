"""Tools exposed to the Rent Prediction AI Agent."""

from typing import Dict, Any, List, Optional
from rent_agent.models.ml_engine import RentPredictorModel
from rent_agent.market.comps_engine import ComparableFinder
from rent_agent.market.trends import get_market_summary, calculate_investment_roi
from rent_agent.config import CITY_METRICS


class AgentTools:
    """Registry of domain tools callable by the AI Agent."""

    def __init__(self):
        self.predictor = RentPredictorModel()
        self.comps_finder = ComparableFinder()

    def predict_rent(self, property_details: Dict[str, Any]) -> Dict[str, Any]:
        """Run ML valuation on property specifications."""
        return self.predictor.predict(property_details)

    def find_comparables(self, property_details: Dict[str, Any], top_k: int = 4) -> List[Dict[str, Any]]:
        """Search database for closely matching comparable rentals."""
        return self.comps_finder.find_comps(property_details, top_k=top_k)

    def get_market_trends(self, city: str) -> Dict[str, Any]:
        """Fetch macroeconomic and seasonal rental metrics for a metro."""
        return get_market_summary(city)

    def calculate_roi(
        self,
        purchase_price: float,
        monthly_rent: float,
        down_payment_pct: float = 0.20,
        monthly_hoa: float = 250.0,
        interest_rate: float = 0.065,
    ) -> Dict[str, Any]:
        """Calculate real estate investment metrics (Cap rate, Cash-on-cash, NOI)."""
        return calculate_investment_roi(
            purchase_price=purchase_price,
            monthly_rent=monthly_rent,
            down_payment_pct=down_payment_pct,
            monthly_hoa=monthly_hoa,
            interest_rate=interest_rate,
        )

    def generate_negotiation_strategy(
        self,
        asking_rent: float,
        predicted_rent: float,
        days_on_market: int = 20,
        city: str = "Chicago",
    ) -> Dict[str, Any]:
        """Generate high-probability negotiation tactics and email script."""
        diff = asking_rent - predicted_rent
        pct_diff = (diff / predicted_rent) * 100.0 if predicted_rent > 0 else 0.0
        city_info = CITY_METRICS.get(city, CITY_METRICS.get("Chicago", {}))
        vac_rate = city_info.get("vacancy_rate", 0.05)

        tactics: List[str] = []
        leverage_score: int = 50  # 0 to 100

        # Assess leverage
        if pct_diff > 8.0:
            tactics.append(f"Property is overpriced by ~{pct_diff:.1f}% compared to algorithmic fair market value.")
            leverage_score += 25
        elif pct_diff < -5.0:
            tactics.append("Asking price is already below market average. Act fast rather than aggressively bargaining.")
            leverage_score -= 20

        if days_on_market >= 35:
            tactics.append(f"Listing has sat on market for {days_on_market} days. Landlord is losing monthly carrying cost.")
            leverage_score += 20
        elif days_on_market < 7:
            tactics.append(f"Fresh listing ({days_on_market} days). Landlord is less inclined to discount price.")
            leverage_score -= 10

        if vac_rate > 0.055:
            tactics.append(f"City vacancy rate is elevated ({vac_rate*100:.1f}%), giving tenants more competitive alternatives.")
            leverage_score += 15

        target_offer = int(round(max(predicted_rent, asking_rent * 0.92) / 10.0) * 10)

        # Counter-proposals if rent price is rigid
        alternative_concessions = [
            "Request 1 month free on an extended 13-14 month lease",
            "Ask to waive or discount parking fees ($150-$200/mo value)",
            "Ask for free pet rent or waived administrative / application fees",
            "Propose a 2-year lease lock with zero escalation clause in exchange for a modest reduction",
        ]

        # Tenant email template
        email_template = f"""Subject: Rental Application Inquiry - {city} Property

Dear Property Manager / Landlord,

I recently toured the property and am very interested in submitting an application. Based on recent comparable units in the neighborhood with similar amenities, fair market value averages approximately ${target_offer:,}/month.

Given my strong credit score, verified income, and readiness to move in immediately with a standard 12-month lease, I would like to propose a monthly rent of ${target_offer:,}/month. 

Alternatively, if the headline rent of ${int(asking_rent):,}/month is firm, I would be pleased to sign at the current rate in exchange for one month concession or inclusive parking.

Looking forward to hearing from you.

Best regards,
[Your Name]
[Your Phone Number]"""

        return {
            "asking_rent": asking_rent,
            "predicted_fair_rent": predicted_rent,
            "overpricing_percentage": round(pct_diff, 1),
            "negotiation_leverage_score": min(100, max(10, leverage_score)),
            "recommended_target_offer": target_offer,
            "monthly_savings_potential": max(0, int(asking_rent - target_offer)),
            "annual_savings_potential": max(0, int((asking_rent - target_offer) * 12)),
            "leverage_points": tactics,
            "alternative_concessions": alternative_concessions,
            "sample_email_script": email_template,
        }
