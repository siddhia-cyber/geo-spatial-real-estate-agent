import streamlit as st
import requests

# App config
st.set_page_config(
    page_title="Geo RAG Real Estate Agent",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000/api/ask"



# Sidebar filters
st.sidebar.title("🔍 Search Filters")

location = st.sidebar.text_input("Location", value="Mumbai")
radius_km = st.sidebar.slider("Search Radius (km)", 1, 30, 10)

bhk = st.sidebar.selectbox(
    "BHK",
    options=[0, 1, 2, 3, 4],
    format_func=lambda x: "Any" if x == 0 else f"{x} BHK"
)

max_price = st.sidebar.number_input(
    "Max Price (₹)",
    min_value=0,
    step=500000,
    value=0,
    help="Enter 0 for no limit"
)

require_gym = st.sidebar.checkbox("Gym Required")


# Main UI
st.title("🏠 Geo-Spatial Real Estate Agent")
st.write("Search properties using natural language + filters")

query = st.text_input(
    "What are you looking for?",
    placeholder="e.g. 2 BHK flat under 80 lac with gym"
)

search_btn = st.button("Search")

# Search action
if search_btn:
    if not query.strip():
        st.warning("Please enter a search query.")
    else:
        payload = {
            "query": query,
            "location": location,
            "radius_km": radius_km,
            "bhk": bhk,
            "max_price": max_price,
            "require_gym": require_gym
        }

        with st.spinner("Searching properties..."):
            try:
                response = requests.post(API_URL, json=payload, timeout=60)

                if response.status_code != 200:
                    st.error("Error from backend.")
                else:
                    data = response.json()

                    
                    # Explanation
                    st.subheader("📌 Explanation")
                    st.write(data.get("explanation", ""))

                    
                    # Results
                    results = data.get("results", [])

                    st.subheader(f"🏘 Results ({len(results)})")

                    if not results:
                        st.info("No matching properties found.")
                    else:
                        for idx, r in enumerate(results, 1):
                            with st.container():
                                st.markdown(f"### {idx}. {r['locality']}")
                                col1, col2, col3 = st.columns(3)

                                col1.write(f"**Price:** ₹ {r['price']}")
                                col2.write(f"**BHK:** {r['bhk']}")
                                col3.write(f"**Area:** {r['area_sqft']} sqft")

                                if r.get("amenities"):
                                    st.write("**Amenities:**", ", ".join(r["amenities"]))

                                st.caption(f"Reason: {r['reason']}")
                                st.divider()

            except Exception as e:
                st.error(f"Request failed: {e}")


