"""Rental market trends, seasonality metrics, and investment financial indicators."""

from typing import Dict, Any, Optional
from datetime import datetime
from rent_agent.config import CITY_METRICS


def get_market_summary(city: str) -> Dict[str, Any]:
    """Retrieve comprehensive macro rental trends for a specific city."""
    if city not in CITY_METRICS:
        return {
            "error": f"City '{city}' not recognized. Supported: {list(CITY_METRICS.keys())}"
        }

    info = CITY_METRICS[city]
    current_month = datetime.now().month
    peak_month = info["seasonal_peak_month"]

    # Month distance from peak (cosine wave)
    month_dist = abs(current_month - peak_month)
    if month_dist > 6:
        month_dist = 12 - month_dist

    # Seasonal adjustment factor (+/- 3.5%)
    seasonal_factor = 1.0 + (0.035 * (1.0 - (month_dist / 3.0)))

    # Typical 1-bed and 2-bed median estimates
    median_1bed = int(round((info["base_fixed"] + (720 * info["base_sqft_rate"])) * seasonal_factor / 10.0) * 10)
    median_2bed = int(round((info["base_fixed"] + 240 + (1050 * info["base_sqft_rate"])) * seasonal_factor / 10.0) * 10)

    # Market temperature classification
    vac_rate = info["vacancy_rate"]
    if vac_rate < 0.035:
        market_temp = "Extreme Landlord Market (Very Low Vacancy / Strong Pricing Power)"
    elif vac_rate < 0.050:
        market_temp = "Competitive Landlord Market"
    elif vac_rate < 0.065:
        market_temp = "Balanced Market"
    else:
        market_temp = "Tenant-Favorable Market (High Concessions & Negotiations Possible)"

    return {
        "city": city,
        "median_1bed_rent": median_1bed,
        "median_2bed_rent": median_2bed,
        "base_rent_per_sqft": f"${info['base_sqft_rate']:.2f}/sqft",
        "vacancy_rate_pct": f"{vac_rate * 100:.1f}%",
        "market_temperature": market_temp,
        "average_cap_rate": f"{info['average_cap_rate'] * 100:.2f}%",
        "seasonal_adjustment_factor": round(seasonal_factor, 3),
        "peak_season_month": peak_month,
        "neighborhood_count": len(info["neighborhoods"]),
        "top_neighborhoods": list(info["neighborhoods"].keys())[:5],
    }


def calculate_investment_roi(
    purchase_price: float,
    monthly_rent: float,
    annual_property_tax_rate: float = 0.012,
    annual_insurance: float = 1200.0,
    monthly_hoa: float = 250.0,
    maintenance_pct: float = 0.08,
    vacancy_pct: float = 0.05,
    down_payment_pct: float = 0.20,
    interest_rate: float = 0.065,
    loan_term_years: int = 30,
) -> Dict[str, Any]:
    """Calculate key financial metrics for real estate rental property investments."""
    annual_gross_rent = monthly_rent * 12.0
    effective_gross_income = annual_gross_rent * (1.0 - vacancy_pct)

    # Annual Operating Expenses
    property_tax = purchase_price * annual_property_tax_rate
    hoa_annual = monthly_hoa * 12.0
    maintenance_annual = annual_gross_rent * maintenance_pct
    total_operating_expenses = (
        property_tax + annual_insurance + hoa_annual + maintenance_annual
    )

    # Net Operating Income (NOI)
    noi = effective_gross_income - total_operating_expenses

    # Capitalization Rate (Cap Rate)
    cap_rate = (noi / purchase_price) * 100.0 if purchase_price > 0 else 0.0

    # Gross Rental Yield
    gross_yield = (annual_gross_rent / purchase_price) * 100.0 if purchase_price > 0 else 0.0

    # Financing / Mortgage Calculation
    loan_amount = purchase_price * (1.0 - down_payment_pct)
    down_payment = purchase_price * down_payment_pct
    closing_costs = purchase_price * 0.025
    total_initial_cash_invested = down_payment + closing_costs

    # Monthly mortgage payment (P&I)
    if loan_amount > 0 and interest_rate > 0:
        monthly_rate = interest_rate / 12.0
        n_payments = loan_term_years * 12
        monthly_mortgage = (
            loan_amount
            * (monthly_rate * (1 + monthly_rate) ** n_payments)
            / (((1 + monthly_rate) ** n_payments) - 1)
        )
    else:
        monthly_mortgage = 0.0

    annual_debt_service = monthly_mortgage * 12.0
    annual_cash_flow = noi - annual_debt_service
    monthly_cash_flow = annual_cash_flow / 12.0

    # Cash-on-Cash Return
    cash_on_cash = (
        (annual_cash_flow / total_initial_cash_invested) * 100.0
        if total_initial_cash_invested > 0
        else 0.0
    )

    # 1% Rule Check
    meets_one_percent_rule = (monthly_rent / purchase_price) >= 0.01

    return {
        "purchase_price": purchase_price,
        "monthly_rent": monthly_rent,
        "annual_gross_rent": round(annual_gross_rent, 2),
        "effective_gross_income": round(effective_gross_income, 2),
        "total_annual_operating_expenses": round(total_operating_expenses, 2),
        "net_operating_income_noi": round(noi, 2),
        "cap_rate_pct": round(cap_rate, 2),
        "gross_rental_yield_pct": round(gross_yield, 2),
        "monthly_mortgage_pi": round(monthly_mortgage, 2),
        "monthly_net_cash_flow": round(monthly_cash_flow, 2),
        "annual_net_cash_flow": round(annual_cash_flow, 2),
        "total_cash_invested": round(total_initial_cash_invested, 2),
        "cash_on_cash_return_pct": round(cash_on_cash, 2),
        "meets_1_percent_rule": meets_one_percent_rule,
        "verdict": (
            "Strong Cash Flow Investment"
            if cash_on_cash >= 8.0
            else "Moderate Investment Profile"
            if cash_on_cash >= 4.0
            else "Appreciation-Focused / Low Yield"
        ),
    }
