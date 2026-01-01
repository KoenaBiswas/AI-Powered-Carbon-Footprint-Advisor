import streamlit as st
import requests

st.set_page_config(page_title="AI Carbon Footprint Advisor")

st.title("🌍 Carbon Footprint Calculator + AI Advisor")
st.caption("Estimate your impact and get AI-powered suggestions")

#st.title("🌱 AI Carbon Footprint Calculator")

st.write("Calculate your carbon footprint and get AI-powered sustainability advice.")

transport = st.selectbox(
    "How do you usually travel?",
    ["Car", "Bus", "Bike"]
)

electricity = st.number_input(
    "Monthly electricity usage (units)",
    min_value=0,
    step=50
)

diet = st.selectbox(
    "Your diet type",
    ["Vegetarian", "Non-Vegetarian"]
)


def calculate_carbon_footprint(transport, electricity, diet):
    # Transport emissions (kg CO₂ per month)
    if transport == "Car":
        transport_emission = 200
    elif transport == "Bus":
        transport_emission = 36
    else:  # Bike
        transport_emission = 41

    # Electricity emissions (India avg ~0.7 kg CO₂ per unit)
    electricity_emission = electricity * 0.82

    # Diet emissions (monthly average)
    if diet == "Vegetarian":
        diet_emission = 60
    else:
        diet_emission = 100

    total_co2 = transport_emission + electricity_emission + diet_emission
    if total_co2 < 250:
        level = "Low"
    elif total_co2 < 500:
        level = "Medium"
    else:
        level = "High"
    return total_co2, level


def generate_ai_advice(total_co2):
    API_URL = "https://router.huggingface.co/models/google/flan-t5-small"
    headers = {"Authorization": f"Bearer {st.secrets['HF_API_KEY']}"}

    prompt = f"""
    A person has a monthly carbon footprint of {total_co2} kg CO2.
    Explain whether this is low, medium, or high.
    Give 3 simple and practical tips to reduce it.
    Use friendly and easy language.
    """

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=30  # stops hanging if server is slow
        )

        # Safe check: is there content to parse?
        if not response.content:
            return "AI service is busy right now. Please try again."

        result = response.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        else:
            return "AI service is busy right now. Please try again."

    except Exception as e:
        return f"Error contacting AI: {str(e)}"



if st.button("Calculate CO₂"):
    total, level = calculate_carbon_footprint(
        transport,
        electricity,
        diet
    )
    st.info(f"Emission Level: {level}")
    st.success("Carbon footprint calculated!")
    st.metric("🌍 Total CO₂ (kg/month)", round(total, 2))

    st.subheader("🤖 AI Carbon Advisor")

    with st.spinner("Thinking..."):
        ai_response = generate_ai_advice(total)

    st.write(ai_response)
