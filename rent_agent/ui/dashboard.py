"""Streamlit Web Dashboard for ApexRent AI."""

import json
from rent_agent.config import CITY_METRICS, PROPERTY_TYPE_MULTIPLIERS, CONDITION_FACTORS, AMENITY_VALUES
from rent_agent.agent.core import RentPredictionAgent

try:
    import streamlit as st

    def render_app():
        st.set_page_config(
            page_title="ApexRent AI - Real Estate Valuation Agent",
            page_icon="🏢",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        st.title("🏢 ApexRent AI - Intelligent Rental Valuation & Market Agent")
        st.markdown(
            "Algorithmic rent estimation, comparable listings analysis, negotiation playbooks, and investment analytics."
        )

        agent = RentPredictionAgent()

        tab1, tab2, tab3, tab4 = st.tabs([
            "🔮 Rent Valuation & Breakdown",
            "💬 AI Rental Advisory Chat",
            "📊 Market Trends & Comps",
            "💰 Investor ROI & Cap Rate",
        ])

        # TAB 1: Valuation
        with tab1:
            col_left, col_right = st.columns([1, 1], gap="large")

            with col_left:
                st.subheader("Property Specifications")
                city = st.selectbox("Metropolitan Area", list(CITY_METRICS.keys()), index=0)
                city_neighborhoods = list(CITY_METRICS[city]["neighborhoods"].keys())
                neighborhood = st.selectbox("Neighborhood", city_neighborhoods)

                c1, c2 = st.columns(2)
                with c1:
                    prop_type = st.selectbox("Property Type", list(PROPERTY_TYPE_MULTIPLIERS.keys()))
                    bedrooms = st.number_input("Bedrooms", min_value=0, max_value=8, value=2, step=1)
                    sqft = st.number_input("Square Footage (sqft)", min_value=250, max_value=8000, value=950, step=25)
                with c2:
                    condition = st.selectbox("Condition / Finish", list(CONDITION_FACTORS.keys()), index=1)
                    bathrooms = st.number_input("Bathrooms", min_value=1.0, max_value=6.0, value=1.5, step=0.5)
                    year_built = st.number_input("Year Built", min_value=1900, max_value=2026, value=2016, step=1)

                st.markdown("**Amenities & Features:**")
                ac1, ac2 = st.columns(2)
                amenities = {}
                amenity_list = list(AMENITY_VALUES.keys())
                midpoint = len(amenity_list) // 2
                with ac1:
                    for k in amenity_list[:midpoint]:
                        amenities[k] = st.checkbox(k.replace("_", " ").title(), value=True if "washer" in k or "ac" in k else False)
                with ac2:
                    for k in amenity_list[midpoint:]:
                        amenities[k] = st.checkbox(k.replace("_", " ").title(), value=False)

                walk_score = st.slider("Walk Score", 10, 100, 82)
                transit_score = st.slider("Transit Score", 10, 100, 78)

            with col_right:
                st.subheader("Fair Market Valuation")
                specs = {
                    "city": city,
                    "neighborhood": neighborhood,
                    "property_type": prop_type,
                    "bedrooms": bedrooms,
                    "bathrooms": bathrooms,
                    "sqft": sqft,
                    "year_built": year_built,
                    "condition": condition,
                    "amenities": amenities,
                    "walk_score": walk_score,
                    "transit_score": transit_score,
                }

                val = agent.tools.predict_rent(specs)

                m1, m2, m3 = st.columns(3)
                m1.metric("Predicted Monthly Rent", f"${val['predicted_monthly_rent']:,}")
                m2.metric("Price per Sq Ft", f"${val['price_per_sqft']}/sqft")
                m3.metric("Market Percentile", f"Top {100 - val['market_percentile']}%")

                st.info(
                    f"🎯 **Fair Market Range (90% Confidence):** ${val['fair_market_range']['min']:,} - ${val['fair_market_range']['max']:,} / month"
                )

                st.markdown("#### Valuation Factor Attribution")
                bd = val["valuation_breakdown"]
                st.write({
                    "Base City & Property Rate": f"${bd['city_base_fixed']:,}",
                    "Square Footage Contribution": f"${bd['square_footage_contribution']:,}",
                    "Beds & Baths Contribution": f"${bd['beds_baths_contribution']:,}",
                    "Total Amenities Premium": f"${bd['amenities_total']:,}",
                    "Walk & Transit Bonus": f"${bd['walk_and_transit_bonus']:,}",
                    "Building Age Factor": f"${bd['building_age_adjustment']:,}",
                    "Finish / Condition Multiplier": f"{bd['condition_multiplier']}x",
                })

        # TAB 2: Agent Chat
        with tab2:
            st.subheader("💬 Chat with ApexRent AI Agent")
            st.caption("Ask questions about rent estimates, lease negotiations, or real estate investment advice.")

            if "messages" not in st.session_state:
                st.session_state["messages"] = [
                    {
                        "role": "assistant",
                        "content": "Hello! I am your AI Rental Intelligence Advisor. Ask me for rent valuations, comparable listings, lease negotiation tactics, or investment Cap Rate calculations!",
                    }
                ]

            for msg in st.session_state["messages"]:
                st.chat_message(msg["role"]).write(msg["content"])

            if prompt := st.chat_input("E.g., What should I pay for a 2-bed in Chicago West Loop with in-unit laundry?"):
                st.session_state["messages"].append({"role": "user", "content": prompt})
                st.chat_message("user").write(prompt)

                with st.spinner("AI Agent analyzing market data..."):
                    reply = agent.chat(prompt)
                    st.session_state["messages"].append({"role": "assistant", "content": reply})
                    st.chat_message("assistant").markdown(reply)

        # TAB 3: Market Trends & Comps
        with tab3:
            st.subheader("📊 Metro Trends & Comparable Listings")
            target_city = st.selectbox("Select Metro Area to Inspect", list(CITY_METRICS.keys()), key="trend_city")
            trends = agent.tools.get_market_trends(target_city)

            tc1, tc2, tc3, tc4 = st.columns(4)
            tc1.metric("Median 1-Bed", f"${trends['median_1bed_rent']:,}")
            tc2.metric("Median 2-Bed", f"${trends['median_2bed_rent']:,}")
            tc3.metric("Vacancy Rate", trends["vacancy_rate_pct"])
            tc4.metric("Avg Cap Rate", trends["average_cap_rate"])

            st.write(f"**Market Climate:** {trends['market_temperature']}")

            st.markdown("#### Sample Recent Comps in Market")
            sample_specs = {"city": target_city, "bedrooms": 2, "bathrooms": 2.0, "sqft": 1000}
            comps = agent.tools.find_comparables(sample_specs, top_k=6)
            for c in comps:
                st.markdown(
                    f"- **{c['id']}** | {c['neighborhood']} ({c['property_type']}) | {c['bedrooms']}b / {c['bathrooms']}ba | {c['sqft']} sqft | **${c['monthly_rent']:,}/mo** | *Similarity: {c['similarity_pct']}*"
                )

        # TAB 4: Investor ROI
        with tab4:
            st.subheader("💰 Investment Cash Flow & Cap Rate Calculator")
            ic1, ic2 = st.columns(2)
            with ic1:
                purchase_price = st.number_input("Purchase Price ($)", min_value=50000, max_value=10000000, value=420000, step=10000)
                expected_rent = st.number_input("Expected Monthly Rent ($)", min_value=500, max_value=50000, value=2650, step=50)
                down_pct = st.slider("Down Payment (%)", 0, 100, 20) / 100.0
            with ic2:
                hoa_monthly = st.number_input("Monthly HOA ($)", min_value=0, max_value=3000, value=280, step=25)
                interest_rate = st.slider("Mortgage Interest Rate (%)", 3.0, 12.0, 6.5, step=0.1) / 100.0

            roi = agent.tools.calculate_roi(
                purchase_price=purchase_price,
                monthly_rent=expected_rent,
                down_payment_pct=down_pct,
                monthly_hoa=hoa_monthly,
                interest_rate=interest_rate,
            )

            rc1, rc2, rc3, rc4 = st.columns(4)
            rc1.metric("Cap Rate", f"{roi['cap_rate_pct']}%")
            rc2.metric("Gross Yield", f"{roi['gross_rental_yield_pct']}%")
            rc3.metric("Monthly Cash Flow", f"${roi['monthly_net_cash_flow']:,.2f}")
            rc4.metric("Cash-on-Cash Return", f"{roi['cash_on_cash_return_pct']}%")

            st.success(f"**Verdict:** {roi['verdict']} | 1% Rule: {'Passed' if roi['meets_1_percent_rule'] else 'Not Met'}")

except ImportError:
    def render_app():
        print("Streamlit not installed. Install with `pip install streamlit` to run web UI.")


if __name__ == "__main__":
    render_app()
