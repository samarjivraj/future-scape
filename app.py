import os
from flask import Flask, render_template, request
import openai

app = Flask(__name__)

# --- OpenAI setup ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
client = openai

# --- mapping function ---
def map_quiz_answers(form_data):
    """Map frontend quiz answers to backend expected values"""
    mapping = {
        'meat_dairy': {
            'less_20': 'Less than £20',
            '20_50': '£20-£50', 
            '50_100': '£50-£100',
            'over_100': 'Over £100'
        },
        'transport': {
            'car_petrol': 'Car (petrol/diesel)',
            'car_electric': 'Car (electric/hybrid)',
            'public': 'Public transport',
            'walk_cycle': 'Walking or cycling',
            'home': 'Work/study from home'
        },
        'flights': {
            'none': 'None',
            'short': '1-2 short flights',
            'long': '1-2 long flights',
            '3plus': '3+ flights'
        },
        'home_energy_source': {
            'renewable': 'Electricity from renewable sources',
            'mixed': 'Electricity from mixed grid',
            'gas_oil': 'Gas or oil heating',
            'unsure': 'Unsure'
        },
        'home_efficiency': {
            'very': 'Very energy efficient',
            'some': 'Somewhat efficient',
            'not_very': 'Not very efficient',
            'not_sure': 'Not sure'
        },
        'recycling': {
            'always': 'Always recycle',
            'often': 'Recycle often',
            'sometimes': 'Recycle sometimes',
            'rarely': 'Rarely recycle'
        },
        'sustainable_shopping': {
            'most': 'Buy mostly second-hand or sustainable products',
            'occasionally': 'Occasionally buy sustainably',
            'rarely': 'Rarely buy sustainably'
        },
        'carbon_awareness': {
            'high': 'Highly aware of carbon footprint',
            'medium': 'Somewhat aware of carbon footprint',
            'low': 'Not very aware of carbon footprint'
        },
        'device_usage': {
            'less_2': 'Less than 2 hours a day',
            '2_5': '2-5 hours a day',
            '5_8': '5-8 hours a day',
            '8plus': 'More than 8 hours a day'
        },
        'food_waste': {
            'almost_none': 'Almost no food waste',
            'a_little': 'A little food waste',
            'some': 'Some food waste',
            'a_lot': 'A lot of food waste'
        }
    }

    reverse_mapping = {}
    for field, options in mapping.items():
        for key, value in options.items():
            reverse_mapping[value] = key
    return reverse_mapping

# --- FRONTEND ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/results')
def results():
    # This route can optionally redirect or display a default page
    return render_template('results.html', carbon_kg=0, story="Your results will appear here.", tips=[])

# --- CALCULATE ROUTE ---
@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # --- form data ---
        form_fields = [
            'meat_dairy', 'transport', 'flights', 'home_energy_source',
            'home_efficiency', 'recycling', 'sustainable_shopping',
            'carbon_awareness', 'device_usage', 'food_waste'
        ]
        form_data = {field: request.form.get(field) for field in form_fields}
        missing_fields = [k for k, v in form_data.items() if not v]
        if missing_fields:
            return f"<h2>Missing fields: {', '.join(missing_fields)}</h2><a href='/quiz'>← Back to Quiz</a>", 400

        # --- calculate carbon footprint (same as your current code) ---
        total_carbon_kg = 0
        # Meat & dairy
        meat_co2 = {"less_20": 1800, "20_50": 2400, "50_100": 3200, "over_100": 4000}
        total_carbon_kg += meat_co2.get(form_data['meat_dairy'], 3000)
        # Transport
        transport_co2 = {"car_petrol": 2500, "car_electric": 800, "public": 800, "walk_cycle": 200, "home": 300}
        total_carbon_kg += transport_co2.get(form_data['transport'], 1000)
        # Flights
        flight_co2 = {"none": 0, "short": 500, "long": 2000, "3plus": 3500}
        total_carbon_kg += flight_co2.get(form_data['flights'], 0)
        # Home energy
        energy_source_co2 = {"renewable": 500, "mixed": 1200, "gas_oil": 2200, "unsure": 1500}
        base_home = energy_source_co2.get(form_data['home_energy_source'], 1500)
        efficiency_factor = {"very": 0.7, "some": 0.9, "not_very": 1.2, "not_sure": 1.0}
        total_carbon_kg += base_home * efficiency_factor.get(form_data['home_efficiency'], 1.0)
        # Recycling
        recycling_savings = {"always": 0.85, "often": 0.9, "sometimes": 0.95, "rarely": 1.0}
        total_carbon_kg *= recycling_savings.get(form_data['recycling'], 1.0)
        # Sustainable shopping
        if form_data['sustainable_shopping'] == "most":
            total_carbon_kg *= 0.9
        elif form_data['sustainable_shopping'] == "occasionally":
            total_carbon_kg *= 0.95
        # Device usage
        device_hours_to_kwh = {"less_2": 300, "2_5": 600, "5_8": 1000, "8plus": 1500}
        device_kwh = device_hours_to_kwh.get(form_data['device_usage'], 800)
        total_carbon_kg += device_kwh * 0.233
        # Food waste
        food_waste_co2 = {"almost_none": 100, "a_little": 300, "some": 600, "a_lot": 1000}
        total_carbon_kg += food_waste_co2.get(form_data['food_waste'], 500)

        carbon_display = round(total_carbon_kg, 1)

        # --- lifestyle summary ---
        lifestyle_context = []
        if form_data['meat_dairy'] == "less_20":
            lifestyle_context.append("follows a mostly plant-based diet")
        elif form_data['meat_dairy'] == "over_100":
            lifestyle_context.append("consumes large amounts of meat and dairy")
        if form_data['transport'] == "walk_cycle":
            lifestyle_context.append("walks or cycles daily")
        elif form_data['transport'] == "car_petrol":
            lifestyle_context.append("relies heavily on petrol cars")
        elif form_data['transport'] == "public":
            lifestyle_context.append("uses public transport regularly")
        if form_data['flights'] == "3plus":
            lifestyle_context.append("flies frequently for travel")
        elif form_data['flights'] == "none":
            lifestyle_context.append("never flies")
        if form_data['home_energy_source'] == "renewable":
            lifestyle_context.append("powers their home with renewable energy")
        elif form_data['home_energy_source'] == "gas_oil":
            lifestyle_context.append("heats their home with fossil fuels")
        if form_data['food_waste'] == "a_lot":
            lifestyle_context.append("wastes significant amounts of food")
        elif form_data['food_waste'] == "almost_none":
            lifestyle_context.append("minimizes food waste")
        if form_data['recycling'] == "always":
            lifestyle_context.append("recycles diligently")
        elif form_data['recycling'] == "rarely":
            lifestyle_context.append("rarely recycles")
        if form_data['sustainable_shopping'] == "most":
            lifestyle_context.append("buys second-hand and sustainable goods")

        behavior_summary = "; ".join(lifestyle_context) if lifestyle_context else "lives an average modern lifestyle"

        # --- AI prompt ---
        prompt = f"""
        You are a climate storyteller in the year 2050. Imagine a world where everyone lived like this person:

        {behavior_summary}.

        Describe the world in 2050 (120–150 words). Include climate, cities, nature, wildlife, daily life.
        Then end with 2 bullet-pointed actionable tips for sustainability today.
        """

        # --- generate story ---
        story = ""
        tips = []
        if not OPENAI_API_KEY:
            story = f"In 2050, the world shaped by lifestyles like yours presents a mixed picture. {behavior_summary}."
            tips = [
                "Transition to renewable energy sources for home and transport",
                "Support local, sustainable food systems and reduce waste"
            ]
        else:
            try:
                chat_completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.8
                )
                story_full = chat_completion.choices[0].message.content.strip()
                if "•" in story_full:
                    parts = story_full.split("•")
                    story = parts[0].strip()
                    tips = ["•" + tip.strip() for tip in parts[1:]]
                else:
                    story = story_full
                    tips = []
            except Exception as e:
                print(f"OpenAI API error: {e}")
                story = "Unable to generate story at this time. Please try again later."
                tips = []

        return render_template('results.html', carbon_kg=carbon_display, story=story, tips=tips)

    except Exception as e:
        print(f"Error in calculate route: {e}")
        return f"""
        <h2>Oops! Something went wrong.</h2>
        <p>Error: {str(e)}</p>
        <p>Please try again or contact support if the problem persists.</p>
        <a href='/quiz'>← Back to Quiz</a>
        """, 500

# --- test route ---
@app.route('/test')
def test():
    return "Flask app is working!"

if __name__ == "__main__":
    app.run(debug=True)
