import os
import requests
from flask import Flask, render_template, request
from openai import OpenAI

# initialize Flask app
app = Flask(__name__)

# load environment variables (works locally with .env, and on Render via dashboard)
CARBON_API_KEY = os.getenv("CARBON_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# initialize OpenAI client (v1.0+ syntax)
client = OpenAI(api_key=OPENAI_API_KEY)

# home route — mystical crystal ball page
@app.route('/')
def index():
    return render_template('index.html')

# quiz route — shows the 10-question form
@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

# handle form submission and generate future story
@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # === 1. get form data from your 10 questions ===
        meat_dairy = request.form.get('meat_dairy')          # Q1
        transport = request.form.get('transport')            # Q2
        flights = request.form.get('flights')                # Q3
        home_energy_source = request.form.get('home_energy_source')  # Q4
        home_efficiency = request.form.get('home_efficiency')        # Q5
        recycling = request.form.get('recycling')            # Q6
        sustainable_shopping = request.form.get('sustainable_shopping')  # Q7
        carbon_awareness = request.form.get('carbon_awareness')      # Q8
        device_usage = request.form.get('device_usage')      # Q9
        food_waste = request.form.get('food_waste')          # Q10

        total_carbon_kg = 0

        # === 2. map answers to CO2 estimates (kg/year) ===

        # Q1: meat & dairy spending → diet footprint
        meat_co2 = {
            "less_20": 1800,
            "20_50": 2400,
            "50_100": 3200,
            "over_100": 4000
        }
        total_carbon_kg += meat_co2.get(meat_dairy, 3000)

        # Q2: transport
        transport_co2 = {
            "car_petrol": 2500,       # avg UK car user
            "car_electric": 800,      # much lower grid-dependent
            "public": 800,
            "walk_cycle": 200,
            "home": 300               # includes occasional trips
        }
        total_carbon_kg += transport_co2.get(transport, 1000)

        # Q3: flights
        flight_co2 = {
            "none": 0,
            "short": 500,             # 1-2 short return = ~500 kg
            "long": 2000,             # 1-2 long-haul
            "3plus": 3500             # 3+ flights
        }
        total_carbon_kg += flight_co2.get(flights, 0)

        # Q4: home Energy Source
        energy_source_co2 = {
            "renewable": 500,
            "mixed": 1200,
            "gas_oil": 2200,
            "unsure": 1500
        }
        base_home = energy_source_co2.get(home_energy_source, 1500)

        # Q5: home Efficiency (adjust base)
        efficiency_factor = {
            "very": 0.7,
            "some": 0.9,
            "not_very": 1.2,
            "not_sure": 1.0
        }
        total_carbon_kg += base_home * efficiency_factor.get(home_efficiency, 1.0)

        # Q6: recycling (reduces footprint by up to 20%)
        recycling_savings = {
            "always": 0.85,
            "often": 0.9,
            "sometimes": 0.95,
            "rarely": 1.0
        }
        total_carbon_kg *= recycling_savings.get(recycling, 1.0)

        # Q7: sustainable Shopping (small reduction)
        if sustainable_shopping == "most":
            total_carbon_kg *= 0.9
        elif sustainable_shopping == "occasionally":
            total_carbon_kg *= 0.95

        # Q9: device Usage → Electricity
        device_hours_to_kwh = {
            "less_2": 300,   # ~300 kWh/year
            "2_5": 600,
            "5_8": 1000,
            "8plus": 1500
        }
        device_kwh = device_hours_to_kwh.get(device_usage, 800)
        # estimate CO2 from electricity (UK grid: ~0.233 kg/kWh)
        total_carbon_kg += device_kwh * 0.233

        # Q10: Food Waste
        food_waste_co2 = {
            "almost_none": 100,
            "a_little": 300,
            "some": 600,
            "a_lot": 1000
        }
        total_carbon_kg += food_waste_co2.get(food_waste, 500)

        # round final value
        carbon_display = round(total_carbon_kg, 1)

        # === build rich context for the AI ===
        lifestyle_context = []

        # diet
        if meat_dairy == "less_20":
            lifestyle_context.append("follows a mostly plant-based diet")
        elif meat_dairy == "over_100":
            lifestyle_context.append("consumes large amounts of meat and dairy")

        # transport
        if transport == "walk_cycle":
            lifestyle_context.append("walks or cycles daily")
        elif transport == "car_petrol":
            lifestyle_context.append("relies heavily on petrol cars")
        elif transport == "public":
            lifestyle_context.append("uses public transport regularly")

        # flights
        if flights == "3plus":
            lifestyle_context.append("flies frequently for travel")
        elif flights == "none":
            lifestyle_context.append("never flies")

        # home energy
        if home_energy_source == "renewable":
            lifestyle_context.append("powers their home with renewable energy")
        elif home_energy_source == "gas_oil":
            lifestyle_context.append("heats their home with fossil fuels")

        # waste & consumption
        if food_waste == "a_lot":
            lifestyle_context.append("wastes significant amounts of food")
        elif food_waste == "almost_none":
            lifestyle_context.append("minimizes food waste")

        if recycling == "always":
            lifestyle_context.append("recycles diligently")
        elif recycling == "rarely":
            lifestyle_context.append("rarely recycles")

        if sustainable_shopping == "most":
            lifestyle_context.append("buys second-hand and sustainable goods")

        # combine into a natural sentence
        if lifestyle_context:
            behavior_summary = "; ".join(lifestyle_context)
        else:
            behavior_summary = "lives an average modern lifestyle"

        # === AI prompt ===
        prompt = f"""
        You are a climate storyteller in the year 2050. Imagine a world where every person on Earth lived exactly like a specific individual whose lifestyle is described below.

        This person: {behavior_summary}.

        Based on this collective behavior, describe the state of the planet in 2050 in 120–150 words. Include vivid details about:
        - Climate and weather patterns
        - Cities and infrastructure
        - Nature, oceans, and wildlife
        - Daily human life and society

        Be poetic but grounded in climate science. End with 2 specific, hopeful bullet pointed actions people could take today to create a better future.
        """

        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.8
        )
        story = chat_completion.choices[0].message.content.strip()

        # === 4. render result ===
        return render_template('results.html', carbon_kg=carbon_display, story=story)

    except Exception as e:
        return f"<h2>Oops! Something went wrong.</h2><p>{str(e)}</p><a href='/quiz'>← Try Again</a>", 500


# required for Render deployment
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)