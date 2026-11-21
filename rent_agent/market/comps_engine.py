"""Comparable Listings (Comps) Search Engine for real estate rental analysis."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from rent_agent.config import SAMPLE_DATA_PATH
from rent_agent.models.data_generator import generate_dataset


class ComparableFinder:
    """Finds closely matching comparable rental properties."""

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or SAMPLE_DATA_PATH
        self.listings: List[Dict[str, Any]] = []
        self._load_data()

    def _load_data(self):
        """Load listings or generate initial dataset if missing."""
        if not self.data_path.exists():
            self.listings = generate_dataset(num_samples=2000, output_path=self.data_path)
        else:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.listings = json.load(f)

    def calculate_similarity(self, target: Dict[str, Any], candidate: Dict[str, Any]) -> float:
        """Calculate weighted similarity score between 0.0 and 1.0."""
        score = 0.0

        # City match is required for high similarity
        if target.get("city", "").lower() != candidate.get("city", "").lower():
            return 0.0

        score += 0.25  # Base city match

        # Neighborhood match
        target_neigh = target.get("neighborhood", "").lower()
        cand_neigh = candidate.get("neighborhood", "").lower()
        if target_neigh and cand_neigh and target_neigh == cand_neigh:
            score += 0.20
        elif not target_neigh:
            score += 0.10

        # Bedroom match
        t_beds = target.get("bedrooms", 1)
        c_beds = candidate.get("bedrooms", 1)
        bed_diff = abs(t_beds - c_beds)
        if bed_diff == 0:
            score += 0.18
        elif bed_diff == 1:
            score += 0.08

        # Bathroom match
        t_baths = target.get("bathrooms", 1.0)
        c_baths = candidate.get("bathrooms", 1.0)
        bath_diff = abs(t_baths - c_baths)
        if bath_diff == 0:
            score += 0.10
        elif bath_diff <= 0.5:
            score += 0.06

        # Sqft proximity
        t_sqft = target.get("sqft", 850)
        c_sqft = candidate.get("sqft", 850)
        sqft_pct_diff = abs(t_sqft - c_sqft) / max(t_sqft, 1)
        sqft_score = max(0.0, 0.15 * (1.0 - (sqft_pct_diff / 0.35)))
        score += sqft_score

        # Property type
        t_type = target.get("property_type", "Apartment")
        c_type = candidate.get("property_type", "Apartment")
        if t_type == c_type:
            score += 0.07

        # Amenities overlap
        t_amen = target.get("amenities", {})
        c_amen = candidate.get("amenities", {})
        if t_amen and c_amen:
            t_keys = {k for k, v in t_amen.items() if v}
            c_keys = {k for k, v in c_amen.items() if v}
            union = len(t_keys | c_keys)
            if union > 0:
                jaccard = len(t_keys & c_keys) / union
                score += 0.05 * jaccard

        return min(1.0, round(score, 3))

    def find_comps(
        self,
        target_property: Dict[str, Any],
        top_k: int = 5,
        max_price_variance: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Find the top-K comparable listings ranked by similarity."""
        scored_listings = []

        for item in self.listings:
            sim = self.calculate_similarity(target_property, item)
            if sim > 0.35:  # Minimum threshold
                item_copy = dict(item)
                item_copy["similarity_score"] = sim
                item_copy["similarity_pct"] = f"{int(sim * 100)}%"
                scored_listings.append(item_copy)

        # Sort by similarity descending
        scored_listings.sort(key=lambda x: x["similarity_score"], reverse=True)

        return scored_listings[:top_k]
