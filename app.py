# Add this helper function at the top of app.py
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
            }, 'home_efficiency': {
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
        

    
    # Reverse mapping for display
    reverse_mapping = {}
    for field, options in mapping.items():
        for key, value in options.items():
            reverse_mapping[value] = key
    
    return reverse_mapping

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Debug: Print received form data
        print("Received form data:", request.form)
        
        # === 1. get form data from your 10 questions ===
        meat_dairy = request.form.get('meat_dairy')
        transport = request.form.get('transport') 
        flights = request.form.get('flights')
        home_energy_source = request.form.get('home_energy_source')
        home_efficiency = request.form.get('home_efficiency')
        recycling = request.form.get('recycling')
        sustainable_shopping = request.form.get('sustainable_shopping')
        carbon_awareness = request.form.get('carbon_awareness')
        device_usage = request.form.get('device_usage')
        food_waste = request.form.get('food_waste')

        # Check if all required fields are present
        required_fields = [meat_dairy, transport, flights, home_energy_source, 
                          home_efficiency, recycling, sustainable_shopping, 
                          carbon_awareness, device_usage, food_waste]
        
        if None in required_fields or "" in required_fields:
            missing_fields = []
            fields = ['meat_dairy', 'transport', 'flights', 'home_energy_source', 
                     'home_efficiency', 'recycling', 'sustainable_shopping', 
                     'carbon_awareness', 'device_usage', 'food_waste']
            for i, field in enumerate(fields):
                if not required_fields[i]:
                    missing_fields.append(field)
            
            return f"<h2>Missing fields: {', '.join(missing_fields)}</h2><a href='/quiz'>← Back to Quiz</a>", 400

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
            "car_petrol": 2500,
            "car_electric": 800,
            "public": 800,
            "walk_cycle": 200,
            "home": 300
        }
        total_carbon_kg += transport_co2.get(transport, 1000)

        # Q3: flights
        flight_co2 = {
            "none": 0,
            "short": 500,
            "long": 2000,
            "3plus": 3500
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
            "less_2": 300,
            "2_5": 600,
            "5_8": 1000,
            "8plus": 1500
        }
        device_kwh = device_hours_to_kwh.get(device_usage, 800)
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

        print(f"Generating AI story for: {behavior_summary}")
        
        # Check if OpenAI API key is available
        if not OPENAI_API_KEY:
            # Fallback story if OpenAI is not configured
            story = f"""In 2050, the world shaped by lifestyles like yours presents a mixed picture. {behavior_summary}. 

The climate shows both challenges and opportunities. While some regions face intensified weather patterns, global cooperation has led to innovative solutions in renewable energy and sustainable agriculture.

Cities have transformed with green infrastructure, vertical gardens, and efficient public transport systems. Nature shows remarkable resilience where conservation efforts have been prioritized.

• Transition to renewable energy sources for home and transport
• Support local, sustainable food systems and reduce waste

The future remains unwritten - your choices today shape tomorrow's world."""
        else:
            try:
                chat_completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=250,
                    temperature=0.8
                )
                story = chat_completion.choices[0].message.content.strip()
                print("AI story generated successfully")
            except Exception as e:
                print(f"OpenAI API error: {e}")
                story = "Unable to generate story at this time. Please try again later."

        # === 4. render result ===
        return render_template('results.html', carbon_kg=carbon_display, story=story)

    except Exception as e:
        print(f"Error in calculate route: {e}")
        return f"""
        <h2>Oops! Something went wrong.</h2>
        <p>Error: {str(e)}</p>
        <p>Please try again or contact support if the problem persists.</p>
        <a href='/quiz'>← Back to Quiz</a>
        """, 500

# Add a test route to check if the app is working
@app.route('/test')
def test():
    return "Flask app is working!"