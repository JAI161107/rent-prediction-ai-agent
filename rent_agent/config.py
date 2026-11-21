"""Configuration and domain constants for the Rent Prediction AI Agent."""

from pathlib import Path
from typing import Dict, Any

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "rent_agent" / "models"
SAMPLE_DATA_PATH = DATA_DIR / "sample_listings.json"
MODEL_CHECKPOINT_PATH = DATA_DIR / "rent_model_weights.json"

# Supported Metropolitan Markets with baseline rent per square foot and city premium
CITY_METRICS: Dict[str, Dict[str, Any]] = {
    "New York": {
        "base_sqft_rate": 4.85,
        "base_fixed": 1200,
        "vacancy_rate": 0.024,
        "average_cap_rate": 0.041,
        "seasonal_peak_month": 8,  # August
        "neighborhoods": {
            "Manhattan - Downtown": 1.45,
            "Manhattan - Midtown": 1.35,
            "Manhattan - Upper East/West": 1.25,
            "Brooklyn - Williamsburg/DUMBO": 1.22,
            "Brooklyn - Park Slope": 1.10,
            "Queens - Astoria/LIC": 0.95,
            "Bronx - South": 0.70,
            "Staten Island": 0.65,
        },
    },
    "San Francisco": {
        "base_sqft_rate": 4.50,
        "base_fixed": 1100,
        "vacancy_rate": 0.048,
        "average_cap_rate": 0.038,
        "seasonal_peak_month": 9,  # September
        "neighborhoods": {
            "SoMa / Financial District": 1.30,
            "Mission / Castro": 1.25,
            "Marina / Pacific Heights": 1.35,
            "Sunset / Richmond": 0.95,
            "Nob Hill": 1.15,
            "Bayview": 0.75,
        },
    },
    "Los Angeles": {
        "base_sqft_rate": 3.40,
        "base_fixed": 900,
        "vacancy_rate": 0.039,
        "average_cap_rate": 0.046,
        "seasonal_peak_month": 7,  # July
        "neighborhoods": {
            "Santa Monica / Venice": 1.40,
            "Beverly Hills / West Hollywood": 1.35,
            "Downtown LA": 1.10,
            "Silver Lake / Echo Park": 1.15,
            "Pasadena": 1.00,
            "San Fernando Valley": 0.85,
        },
    },
    "Chicago": {
        "base_sqft_rate": 2.60,
        "base_fixed": 650,
        "vacancy_rate": 0.052,
        "average_cap_rate": 0.065,
        "seasonal_peak_month": 6,  # June
        "neighborhoods": {
            "West Loop / Fulton Market": 1.35,
            "River North / Loop": 1.25,
            "Lincoln Park / Lakeview": 1.15,
            "Wicker Park / Logan Square": 1.05,
            "Hyde Park": 0.90,
            "Bridgeport / Pilsen": 0.82,
        },
    },
    "Austin": {
        "base_sqft_rate": 2.45,
        "base_fixed": 600,
        "vacancy_rate": 0.068,
        "average_cap_rate": 0.058,
        "seasonal_peak_month": 8,
        "neighborhoods": {
            "Downtown / Rainey": 1.40,
            "South Congress (SoCo)": 1.25,
            "East Austin": 1.15,
            "Domain / North Burnet": 1.10,
            "Mueller": 1.08,
            "South Lamar": 1.05,
            "Round Rock / Suburban": 0.78,
        },
    },
    "Seattle": {
        "base_sqft_rate": 3.20,
        "base_fixed": 800,
        "vacancy_rate": 0.045,
        "average_cap_rate": 0.049,
        "seasonal_peak_month": 7,
        "neighborhoods": {
            "South Lake Union / Belltown": 1.30,
            "Capitol Hill": 1.20,
            "Ballard / Fremont": 1.12,
            "Queen Anne": 1.18,
            "West Seattle": 0.92,
            "University District": 0.88,
        },
    },
    "Miami": {
        "base_sqft_rate": 3.35,
        "base_fixed": 850,
        "vacancy_rate": 0.042,
        "average_cap_rate": 0.055,
        "seasonal_peak_month": 1,  # Winter peak
        "neighborhoods": {
            "Brickell": 1.35,
            "Miami Beach / South Beach": 1.40,
            "Wynwood / Edgewater": 1.20,
            "Downtown Miami": 1.15,
            "Coral Gables": 1.18,
            "Little Havana": 0.82,
        },
    },
    "Boston": {
        "base_sqft_rate": 3.75,
        "base_fixed": 950,
        "vacancy_rate": 0.028,
        "average_cap_rate": 0.044,
        "seasonal_peak_month": 9,  # Student cycle peak (Sept 1)
        "neighborhoods": {
            "Back Bay / Beacon Hill": 1.40,
            "Seaport District": 1.45,
            "South End": 1.25,
            "Cambridge / Kendall": 1.30,
            "Fenway / Kenmore": 1.10,
            "Allston / Brighton": 0.90,
        },
    },
    "Denver": {
        "base_sqft_rate": 2.50,
        "base_fixed": 650,
        "vacancy_rate": 0.056,
        "average_cap_rate": 0.052,
        "seasonal_peak_month": 6,
        "neighborhoods": {
            "LoDo / RiNo": 1.30,
            "Cherry Creek": 1.35,
            "Cap Hill / Uptown": 1.10,
            "Highlands / LoHi": 1.20,
            "Baker / Wash Park": 1.12,
            "Aurora / Suburban": 0.80,
        },
    },
    "Atlanta": {
        "base_sqft_rate": 2.20,
        "base_fixed": 550,
        "vacancy_rate": 0.062,
        "average_cap_rate": 0.068,
        "seasonal_peak_month": 7,
        "neighborhoods": {
            "Buckhead": 1.35,
            "Midtown": 1.30,
            "Inman Park / Old Fourth Ward": 1.22,
            "Virginia Highland": 1.18,
            "West End": 0.85,
            "Decatur / East": 1.05,
        },
    },
}

# Property type adjustment multipliers
PROPERTY_TYPE_MULTIPLIERS: Dict[str, float] = {
    "Apartment": 1.00,
    "Condo": 1.08,
    "Townhouse": 1.12,
    "Single-Family House": 1.20,
    "Studio": 0.92,
}

# Amenity pricing premiums ($/month contribution)
AMENITY_VALUES: Dict[str, float] = {
    "in_unit_washer_dryer": 160.0,
    "central_ac": 110.0,
    "parking_spot": 175.0,
    "private_balcony": 95.0,
    "dishwasher": 65.0,
    "pet_friendly": 50.0,
    "fitness_center": 80.0,
    "swimming_pool": 75.0,
    "doorman_concierge": 140.0,
    "hardwood_floors": 70.0,
    "rooftop_deck": 85.0,
    "furnished": 350.0,
}

# Condition tier adjustments
CONDITION_FACTORS: Dict[str, float] = {
    "Brand New / Luxury": 1.18,
    "Recently Renovated": 1.08,
    "Standard / Well Maintained": 1.00,
    "Dated / Needs Update": 0.88,
}
