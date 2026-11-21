"""Unit tests for the autonomous Rent Prediction Agent and Tools."""

import unittest
from rent_agent.agent.core import RentPredictionAgent
from rent_agent.agent.tools import AgentTools


class TestAgent(unittest.TestCase):
    def setUp(self):
        self.agent = RentPredictionAgent()
        self.tools = AgentTools()

    def test_comps_retrieval(self):
        target = {
            "city": "Chicago",
            "bedrooms": 2,
            "bathrooms": 2.0,
            "sqft": 1050,
            "property_type": "Apartment",
        }
        comps = self.tools.find_comparables(target, top_k=3)
        self.assertLessEqual(len(comps), 3)
        if comps:
            self.assertEqual(comps[0]["city"], "Chicago")
            self.assertIn("similarity_score", comps[0])

    def test_negotiation_strategy_generator(self):
        strat = self.tools.generate_negotiation_strategy(
            asking_rent=3200,
            predicted_rent=2800,
            days_on_market=45,
            city="Austin",
        )
        self.assertIn("sample_email_script", strat)
        self.assertIn("recommended_target_offer", strat)
        self.assertGreater(strat["annual_savings_potential"], 0)
        self.assertGreaterEqual(strat["negotiation_leverage_score"], 50)

    def test_roi_calculation(self):
        roi = self.tools.calculate_roi(purchase_price=500000, monthly_rent=3200)
        self.assertIn("cap_rate_pct", roi)
        self.assertIn("net_operating_income_noi", roi)
        self.assertGreater(roi["annual_gross_rent"], 30000)

    def test_agent_chat_reasoning(self):
        # Test valuation inquiry
        reply_val = self.agent.chat("What is the fair rent for a 2 bedroom apartment in Chicago?")
        self.assertIn("Fair Market Rent Valuation", reply_val)
        self.assertIn("Chicago", reply_val)

        # Test negotiation inquiry
        reply_neg = self.agent.chat("My landlord is asking $3,000 in Austin. How should I negotiate?")
        self.assertIn("Negotiation Playbook", reply_neg)

        # Test ROI inquiry
        reply_roi = self.agent.chat("What is the cap rate and ROI if I buy a condo for $400,000 and rent it for $2,600?")
        self.assertIn("Investment Analysis", reply_roi)
        self.assertIn("Cap Rate", reply_roi)


if __name__ == "__main__":
    unittest.main()
