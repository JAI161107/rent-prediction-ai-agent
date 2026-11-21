"""Unit tests for the ML Valuation Engine."""

import unittest
from rent_agent.models.ml_engine import RentPredictorModel
from rent_agent.models.data_generator import generate_single_listing


class TestRentPredictor(unittest.TestCase):
    def setUp(self):
        self.model = RentPredictorModel()

    def test_basic_prediction_output(self):
        specs = {
            "city": "Chicago",
            "bedrooms": 2,
            "bathrooms": 1.5,
            "sqft": 950,
            "property_type": "Apartment",
            "amenities": {"in_unit_washer_dryer": True},
        }
        res = self.model.predict(specs)

        self.assertIn("predicted_monthly_rent", res)
        self.assertIn("fair_market_range", res)
        self.assertIn("price_per_sqft", res)
        self.assertIn("valuation_breakdown", res)
        self.assertGreater(res["predicted_monthly_rent"], 1000)
        self.assertLess(res["fair_market_range"]["min"], res["predicted_monthly_rent"])
        self.assertGreater(res["fair_market_range"]["max"], res["predicted_monthly_rent"])

    def test_monotonicity_sqft(self):
        """Increasing square footage should increase rent."""
        spec_small = {"city": "Austin", "sqft": 600, "bedrooms": 1}
        spec_large = {"city": "Austin", "sqft": 1200, "bedrooms": 1}

        val_small = self.model.predict(spec_small)["predicted_monthly_rent"]
        val_large = self.model.predict(spec_large)["predicted_monthly_rent"]

        self.assertGreater(val_large, val_small)

    def test_amenities_premium(self):
        """Adding amenities should increase predicted rent."""
        spec_bare = {"city": "Seattle", "sqft": 800, "bedrooms": 1, "amenities": {}}
        spec_amenities = {
            "city": "Seattle",
            "sqft": 800,
            "bedrooms": 1,
            "amenities": {"in_unit_washer_dryer": True, "parking_spot": True},
        }

        val_bare = self.model.predict(spec_bare)["predicted_monthly_rent"]
        val_amenities = self.model.predict(spec_amenities)["predicted_monthly_rent"]

        self.assertGreater(val_amenities, val_bare)

    def test_city_scaling(self):
        """High cost of living cities should predict higher rent for identical specs."""
        specs = {"bedrooms": 2, "bathrooms": 2.0, "sqft": 1000}
        ny_rent = self.model.predict({**specs, "city": "New York"})["predicted_monthly_rent"]
        atl_rent = self.model.predict({**specs, "city": "Atlanta"})["predicted_monthly_rent"]

        self.assertGreater(ny_rent, atl_rent)


if __name__ == "__main__":
    unittest.main()
