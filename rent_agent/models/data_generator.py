"""Synthetic rental listing generator reflecting real-world market distributions."""

import random
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from rent_agent.config import (
    CITY_METRICS,
    PROPERTY_TYPE_MULTIPLIERS,
    AMENITY_VALUES,
    CONDITION_FACTORS,
    SAMPLE_DATA_PATH,
)


def generate_single_listing(listing_id: int, city: Optional[str] = None) -> Dict[str, Any]:
    """Generate a single realistic rental property listing."""
    if not city or city not in CITY_METRICS:
        city = random.choice(list(CITY_METRICS.keys()))

    city_info = CITY_METRICS[city]
    neighborhood = random.choice(list(city_info["neighborhoods"].keys()))
    neigh_mult = city_info["neighborhoods"][neighborhood]

    property_type = random.choices(
        ["Apartment", "Condo", "Townhouse", "Single-Family House", "Studio"],
        weights=[0.45, 0.25, 0.12, 0.13, 0.05],
    )[0]

    if property_type == "Studio":
        bedrooms = 0
        bathrooms = 1.0
        sqft = int(random.gauss(520, 90))
        sqft = max(300, min(850, sqft))
    else:
        bedrooms = random.choices([1, 2, 3, 4], weights=[0.40, 0.35, 0.18, 0.07])[0]
        if bedrooms == 1:
            bathrooms = 1.0
            sqft = int(random.gauss(720, 110))
            sqft = max(450, min(1100, sqft))
        elif bedrooms == 2:
            bathrooms = random.choice([1.0, 1.5, 2.0, 2.0])
            sqft = int(random.gauss(1050, 160))
            sqft = max(750, min(1600, sqft))
        elif bedrooms == 3:
            bathrooms = random.choice([2.0, 2.0, 2.5, 3.0])
            sqft = int(random.gauss(1550, 240))
            sqft = max(1100, min(2400, sqft))
        else:
            bathrooms = random.choice([2.5, 3.0, 3.5, 4.0])
            sqft = int(random.gauss(2200, 350))
            sqft = max(1600, min(3800, sqft))

    year_built = int(random.choices(
        [random.randint(1920, 1969), random.randint(1970, 1999), random.randint(2000, 2024)],
        weights=[0.25, 0.35, 0.40],
    )[0])

    condition = random.choices(
        ["Brand New / Luxury", "Recently Renovated", "Standard / Well Maintained", "Dated / Needs Update"],
        weights=[0.20, 0.35, 0.35, 0.10],
    )[0]

    # Generate amenities
    amenities = {
        "in_unit_washer_dryer": random.random() < 0.65,
        "central_ac": random.random() < 0.75,
        "parking_spot": random.random() < 0.55,
        "private_balcony": random.random() < 0.40,
        "dishwasher": random.random() < 0.80,
        "pet_friendly": random.random() < 0.60,
        "fitness_center": random.random() < 0.45,
        "swimming_pool": random.random() < 0.30,
        "doorman_concierge": random.random() < 0.25,
        "hardwood_floors": random.random() < 0.70,
        "rooftop_deck": random.random() < 0.30,
        "furnished": random.random() < 0.12,
    }

    walk_score = random.randint(45, 99)
    transit_score = random.randint(40, 98)

    # Base pricing calculation with realistic variance
    base_sqft_cost = sqft * city_info["base_sqft_rate"] * neigh_mult
    base_fixed_cost = city_info["base_fixed"] * PROPERTY_TYPE_MULTIPLIERS[property_type]
    bed_bath_cost = (bedrooms * 220) + ((bathrooms - 1.0) * 160)

    amenity_cost = sum(
        AMENITY_VALUES[key] for key, val in amenities.items() if val
    )

    condition_factor = CONDITION_FACTORS[condition]

    # Add walk score bonus
    walk_bonus = (walk_score - 50) * 2.5 if walk_score > 50 else 0

    subtotal = (base_sqft_cost + base_fixed_cost + bed_bath_cost + amenity_cost + walk_bonus) * condition_factor

    # Natural market noise +/- 5%
    noise_factor = random.uniform(0.96, 1.04)
    monthly_rent = int(round(subtotal * noise_factor / 10.0) * 10)
    monthly_rent = max(700, monthly_rent)

    return {
        "id": f"PROP-{listing_id:05d}",
        "city": city,
        "neighborhood": neighborhood,
        "property_type": property_type,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "sqft": sqft,
        "year_built": year_built,
        "condition": condition,
        "amenities": amenities,
        "walk_score": walk_score,
        "transit_score": transit_score,
        "monthly_rent": monthly_rent,
        "price_per_sqft": round(monthly_rent / sqft, 2),
        "days_on_market": random.randint(2, 65),
    }


def generate_dataset(num_samples: int = 1500, output_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Generate a full synthetic dataset and optionally write to disk."""
    random.seed(42)  # For reproducibility
    listings = [generate_single_listing(i + 1) for i in range(num_samples)]

    if output_path is None:
        output_path = SAMPLE_DATA_PATH

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(listings, f, indent=2)

    return listings


if __name__ == "__main__":
    data = generate_dataset(2000)
    print(f"Generated {len(data)} realistic rental listings saved to {SAMPLE_DATA_PATH}")
