import streamlit as st
import requests
import plotly.graph_objects as go
import datetime
import folium
from streamlit_folium import folium_static
import random
from PIL import Image

# ============ SETTINGS ============
st.set_page_config(
    page_title="Smart Malaysia Travel Companion", 
    layout="wide", 
    page_icon="🌴",
    initial_sidebar_state="expanded"
)

# Custom CSS for vibrant UI
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .sidebar .sidebar-content {
        background-color: #1A1C23;
    }
    h1 {
        color: #4F8BF9;
        border-bottom: 2px solid #4F8BF9;
        padding-bottom: 10px;
    }
    h2 {
        color: #FF4B4B;
    }
    .stMetric {
        background-color: #1E293B;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stAlert {
        border-radius: 10px;
    }
    .city-selector {
        background-color: #2D3746;
        border-radius: 8px;
        padding: 10px;
    }
    .food-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        color: white;
    }
    .attraction-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        color: white;
    }
    @media screen and (max-width: 600px) {
        .stMetric { padding: 8px; }
    }
    </style>
""", unsafe_allow_html=True)

# ============ HEADER ============
col1, col2 = st.columns([1, 3])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Flag_of_Malaysia.svg/1200px-Flag_of_Malaysia.svg.png", 
             width=100)
with col2:
    st.markdown("<h1 style='text-align: left;'>🌴 Smart Malaysia Travel Companion</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left; color: #A9A9A9;'>Your complete guide to Malaysian travel with real-time data</p>", unsafe_allow_html=True)

# ============ DATA CONFIGURATION ============
API_KEY = "15aee72fdd4a19cc0c56ea7607bf6af1"  # OpenWeatherMap free tier

STATE_CAPITALS = {
    "Johor": {"capital": "Johor Bahru", "coords": (1.4927, 103.7414)},
    "Kedah": {"capital": "Alor Setar", "coords": (6.1214, 100.3695)},
    "Kelantan": {"capital": "Kota Bharu", "coords": (6.1256, 102.2432)},
    "Malacca": {"capital": "Malacca", "coords": (2.1896, 102.2501)},
    "Negeri Sembilan": {"capital": "Seremban", "coords": (2.7259, 101.9424)},
    "Pahang": {"capital": "Kuantan", "coords": (3.8077, 103.3260)},
    "Penang": {"capital": "George Town", "coords": (5.4141, 100.3288)},
    "Perak": {"capital": "Ipoh", "coords": (4.5975, 101.0901)},
    "Perlis": {"capital": "Kangar", "coords": (6.4414, 100.1986)},
    "Sabah": {"capital": "Kota Kinabalu", "coords": (5.9804, 116.0735)},
    "Sarawak": {"capital": "Kuching", "coords": (1.5397, 110.3542)},
    "Selangor": {"capital": "Shah Alam", "coords": (3.0733, 101.5185)},
    "Terengganu": {"capital": "Kuala Terengganu", "coords": (5.3296, 103.1370)},
    "Federal Territories": {
        "Kuala Lumpur": (3.1390, 101.6869),
        "Putrajaya": (2.9264, 101.6964),
        "Labuan": (5.2767, 115.2417)
    }
}

# Enhanced tourist attractions data
ATTRACTIONS = {
    "Kuala Lumpur (Federal Territory)": [
        {"name": "Petronas Twin Towers", "coords": (3.1579, 101.7116), "type": "landmark", "icon": "tower", "description": "Iconic twin skyscrapers with observation deck"},
        {"name": "Batu Caves", "coords": (3.2373, 101.6839), "type": "nature", "icon": "mountain", "description": "Hindu temple complex in limestone caves"},
        {"name": "Merdeka Square", "coords": (3.1479, 101.6937), "type": "historic", "icon": "landmark", "description": "Historic square where Malaysian independence was declared"},
        {"name": "KL Tower", "coords": (3.1569, 101.7031), "type": "landmark", "icon": "tower", "description": "Communications tower with revolving restaurant"},
        {"name": "Central Market", "coords": (3.1439, 101.6958), "type": "shopping", "icon": "shopping-cart", "description": "Cultural heritage site with local crafts"}
    ],
    "George Town (Penang)": [
        {"name": "Kek Lok Si Temple", "coords": (5.4030, 100.2732), "type": "cultural", "icon": "temple", "description": "Largest Buddhist temple in Malaysia"},
        {"name": "Penang Hill", "coords": (5.4289, 100.2569), "type": "nature", "icon": "mountain", "description": "Hill station with panoramic views"},
        {"name": "Armenian Street", "coords": (5.4175, 100.3347), "type": "cultural", "icon": "road", "description": "Historic street with street art"},
        {"name": "Gurney Drive", "coords": (5.4378, 100.3108), "type": "food", "icon": "utensils", "description": "Famous food court by the sea"}
    ],
    "Johor Bahru (Johor)": [
        {"name": "Sultan Abu Bakar State Mosque", "coords": (1.4655, 103.7578), "type": "cultural", "icon": "mosque", "description": "Beautiful mosque with Victorian architecture"},
        {"name": "Johor Bahru City Square", "coords": (1.4648, 103.7618), "type": "shopping", "icon": "shopping-cart", "description": "Major shopping mall in city center"},
        {"name": "Danga Bay", "coords": (1.4308, 103.6715), "type": "nature", "icon": "water", "description": "Waterfront development with parks"}
    ],
    "Malacca (Malacca)": [
        {"name": "A Famosa", "coords": (2.1913, 102.2486), "type": "historic", "icon": "fort", "description": "Portuguese fortress ruins"},
        {"name": "Christ Church", "coords": (2.1944, 102.2487), "type": "historic", "icon": "church", "description": "Dutch colonial church"},
        {"name": "Jonker Street", "coords": (2.1949, 102.2473), "type": "cultural", "icon": "road", "description": "Historic street with night market"}
    ],
    "Kota Kinabalu (Sabah)": [
        {"name": "Mount Kinabalu", "coords": (6.0745, 116.5581), "type": "nature", "icon": "mountain", "description": "Highest peak in Malaysia"},
        {"name": "Tunku Abdul Rahman Park", "coords": (5.9667, 116.0167), "type": "nature", "icon": "island", "description": "Marine park with coral reefs"},
        {"name": "Gaya Street", "coords": (5.9788, 116.0753), "type": "shopping", "icon": "shopping-cart", "description": "Sunday market street"}
    ],
    "Kuching (Sarawak)": [
        {"name": "Sarawak Cultural Village", "coords": (1.7472, 110.4306), "type": "cultural", "icon": "home", "description": "Living museum of Sarawak's heritage"},
        {"name": "Kuching Waterfront", "coords": (1.5583, 110.3472), "type": "scenic", "icon": "water", "description": "Scenic promenade along Sarawak River"},
        {"name": "Semenggoh Nature Reserve", "coords": (1.4167, 110.3167), "type": "nature", "icon": "tree", "description": "Orangutan rehabilitation center"}
    ]
}

# Enhanced food recommendations with descriptions
FOOD_RECOMMENDATIONS = {
    "Johor": {
        "dishes": ["Laksa Johor", "Mee Bandung", "Satay", "Kacang Pool"],
        "description": "Johor cuisine features unique noodle dishes and Middle Eastern influences"
    },
    "Penang": {
        "dishes": ["Char Kway Teow", "Assam Laksa", "Penang Rojak", "Cendol"],
        "description": "Street food paradise with UNESCO recognition for culinary heritage"
    },
    "Kuala Lumpur": {
        "dishes": ["Nasi Lemak", "Satay", "Bak Kut Teh", "Hokkien Mee"],
        "description": "Melting pot of Malaysian, Chinese, and Indian cuisines"
    },
    "Malacca": {
        "dishes": ["Chicken Rice Ball", "Cendol", "Nyonya Laksa", "Satay Celup"],
        "description": "Peranakan and Portuguese-influenced cuisine"
    },
    "Kedah": {
        "dishes": ["Nasi Ulam", "Laksa Kedah", "Rendang Tok", "Gulai Tempoyak"],
        "description": "Traditional Malay cuisine with royal heritage"
    },
    "Sabah": {
        "dishes": ["Hinava", "Ambuyat", "Tuhau", "Beaufort Mee"],
        "description": "Indigenous Bornean flavors with fresh seafood"
    },
    "Sarawak": {
        "dishes": ["Sarawak Laksa", "Kolo Mee", "Midin", "Dabai"],
        "description": "Unique Bornean ingredients and Chinese influences"
    }
}

# City population and fun facts
CITY_INFO = {
    "Johor Bahru": {"population": "1.8 million", "fact": "Gateway to Singapore via the Causeway"},
    "Kuala Lumpur": {"population": "1.9 million", "fact": "Home to the Petronas Twin Towers"},
    "George Town": {"population": "0.7 million", "fact": "UNESCO World Heritage Site"},
    "Malacca": {"population": "0.9 million", "fact": "Historic trading port with Portuguese heritage"},
    "Kota Kinabalu": {"population": "0.5 million", "fact": "Gateway to Mount Kinabalu"},
    "Kuching": {"population": "0.7 million", "fact": "Cat City of Borneo"},
    "Kuantan": {"population": "0.6 million", "fact": "Capital of Pahang with beautiful beaches"},
    "Ipoh": {"population": "0.8 million", "fact": "Famous for white coffee and limestone caves"},
    "Shah Alam": {"population": "0.7 million", "fact": "Planned city with the Blue Mosque"},
}

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("### 🗺️ Location Settings")
    use_auto = st.checkbox("Auto-detect my location", value=False)
    
    # Create city options list with state labels
    CITY_OPTIONS = []
    for state, data in STATE_CAPITALS.items():
        if state == "Federal Territories":
            for city, coords in data.items():
                CITY_OPTIONS.append(f"{city} (Federal Territory)")
        else:
            CITY_OPTIONS.append(f"{data['capital']} ({state})")
    
    if use_auto:
        try:
            ipinfo_token = "5616c393bcf417"  # Free tier token
            ipinfo_url = f"https://ipinfo.io/json?token={ipinfo_token}"
            ip_data = requests.get(ipinfo_url).json()
            detected_city = ip_data.get("city", "Kuala Lumpur")
            
            # Find closest match
            selected_city = "Kuala Lumpur (Federal Territory)"  # Default
            for city_option in CITY_OPTIONS:
                if detected_city.lower() in city_option.lower():
                    selected_city = city_option
                    break
            
            st.success(f"Detected: {selected_city.split('(')[0].strip()}")
            city = selected_city
        except:
            st.error("Auto-detection failed. Please select manually.")
            city = st.selectbox("Select City", CITY_OPTIONS, index=0)
    else:
        city = st.selectbox("Select City", CITY_OPTIONS, index=0)
    
    st.markdown("---")
    st.markdown("### 🌦️ Weather Units")
    temp_unit = st.radio("Temperature Unit", ["°C", "°F"], horizontal=True)
    
    st.markdown("---")
    st.markdown("### 📊 Display Options")
    show_map = st.checkbox("Show Interactive Map", value=True)
    show_forecast = st.checkbox("Show 5-Day Forecast", value=True)
    show_details = st.checkbox("Show City Details", value=True)
    show_attractions = st.checkbox("Show Tourist Attractions", value=True)
    
    st.markdown("---")
    st.markdown("### 🆘 Emergency Contacts")
    st.write("**Police:** 999")
    st.write("**Tourism Police:** +603-2149 6590")
    st.write("**Ambulance:** 999")
    st.write("**Tourist Helpline:** 1-300-88-5050")
    
    if st.button("🛎️ Generate 1-Day Itinerary"):
        st.session_state.generate_itinerary = True

# ============ WEATHER FUNCTIONS ============
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_weather(city_name, unit='metric'):
    clean_city = city_name.split("(")[0].strip()
    unit_param = 'metric' if unit == '°C' else 'imperial'
    url = f"https://api.openweathermap.org/data/2.5/weather?q={clean_city},MY&units={unit_param}&appid={API_KEY}"
    return requests.get(url).json()

@st.cache_data(ttl=3600)
def get_forecast(city_name, unit='metric'):
    clean_city = city_name.split("(")[0].strip()
    unit_param = 'metric' if unit == '°C' else 'imperial'
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={clean_city},MY&units={unit_param}&appid={API_KEY}"
    return requests.get(url).json()

@st.cache_data(ttl=3600)
def get_air_quality(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    return requests.get(url).json()

def get_weather_icon(icon_code):
    return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

# ============ MAIN CONTENT ============
try:
    # Get clean city name without state
    clean_city = city.split("(")[0].strip()
    state = city.split("(")[1].replace(")", "").strip()
    city_coords = STATE_CAPITALS[state]["coords"] if state != "Federal Territory" else STATE_CAPITALS["Federal Territories"][clean_city]
    
    # Get weather data
    weather_data = get_weather(clean_city, temp_unit)
    forecast_data = get_forecast(clean_city, temp_unit)
    aqi_data = get_air_quality(city_coords[0], city_coords[1])
    
    # ============ CITY INTRO SECTION ============
    st.markdown(f"## 🌆 {clean_city}")
    
    if show_details:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"### 🏛️ {state if state != 'Federal Territory' else 'Federal Territories'}")
            st.markdown(f"**Capital City**")
            
            city_data = CITY_INFO.get(clean_city, {"population": "Data not available", "fact": "Beautiful Malaysian city"})
            st.markdown(f"**Population:** {city_data['population']}")
            
        with col2:
            st.markdown("### 🌟 Did You Know?")
            st.info(city_data['fact'])
    
    # ============ CURRENT WEATHER ============
    st.markdown(f"## ⛅ Current Weather in {clean_city}")
    
    if weather_data and "main" in weather_data:
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            st.markdown("### 🌡️ Temperature")
            temp = weather_data['main']['temp']
            st.markdown(f"<h1 style='color: #FF4B4B;'>{temp} {temp_unit}</h1>", unsafe_allow_html=True)
            st.markdown(f"Feels like: {weather_data['main']['feels_like']} {temp_unit}")
            st.markdown(f"Min: {weather_data['main']['temp_min']} {temp_unit} | Max: {weather_data['main']['temp_max']} {temp_unit}")
            
        with col2:
            st.markdown("### 📊 Conditions")
            weather_desc = weather_data['weather'][0]['description'].title()
            icon_code = weather_data['weather'][0]['icon']
            st.image(get_weather_icon(icon_code), width=70)
            st.markdown(f"**{weather_desc}**")
            st.markdown(f"Humidity: {weather_data['main']['humidity']}%")
            
            # Air Quality
            aqi_levels = ["Good", "Fair", "Moderate", "Poor", "Very Poor"]
            aqi = aqi_data['list'][0]['main']['aqi'] if aqi_data and 'list' in aqi_data else 1
            aqi_color = ["#00E400", "#FFFF00", "#FF7E00", "#FF0000", "#8F3F97"][aqi-1]
            st.markdown(f"**Air Quality:** <span style='color:{aqi_color}'>{aqi_levels[aqi-1]}</span>", unsafe_allow_html=True)
            
        with col3:
            st.markdown("### 💨 Wind & Atmosphere")
            wind_speed = weather_data['wind']['speed']
            wind_dir = weather_data['wind'].get('deg', 'N/A')
            st.markdown(f"**Wind:** {wind_speed} {'m/s' if temp_unit == '°C' else 'mph'} ({wind_dir}°)")
            visibility = weather_data.get('visibility', 'N/A')
            if visibility != 'N/A':
                visibility = f"{visibility/1000} km" if temp_unit == '°C' else f"{visibility/1609:.1f} miles"
            st.markdown(f"**Visibility:** {visibility}")
            pressure = weather_data['main']['pressure']
            st.markdown(f"**Pressure:** {pressure} hPa")
            
            # Packing suggestions
            with st.expander("🧳 Packing Suggestions"):
                items = ["Universal Adapter", "Passport"]
                if weather_data['main']['temp'] > 30:
                    items.extend(["Sunscreen", "Hat", "Light Clothing"])
                if 'rain' in weather_data:
                    items.append("Umbrella/Raincoat")
                for item in items:
                    st.checkbox(item, key=f"pack_{item}")
    else:
        st.error("Failed to fetch current weather data")
    
    # ============ LOCAL FOOD RECOMMENDATIONS ============
    with st.expander("🍜 Must-Try Local Foods"):
        state_key = state if state in FOOD_RECOMMENDATIONS else "Kuala Lumpur"
        food_data = FOOD_RECOMMENDATIONS.get(state_key, {"dishes": ["Nasi Lemak"], "description": "Malaysian cuisine"})
        
        st.markdown(f"<div class='food-card'>", unsafe_allow_html=True)
        st.markdown(f"**Popular Dishes:** {', '.join(food_data['dishes'])}")
        st.markdown(f"*{food_data['description']}*")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ============ TOURIST ATTRACTIONS ============
    if show_attractions and city in ATTRACTIONS:
        st.markdown("## 🎯 Top Attractions")
        attraction_cols = st.columns(min(3, len(ATTRACTIONS[city])))
        for i, attraction in enumerate(ATTRACTIONS[city][:3]):  # Show top 3
            with attraction_cols[i % 3]:
                st.markdown(f"<div class='attraction-card'>", unsafe_allow_html=True)
                st.markdown(f"**{attraction['name']}**")
                st.markdown(f"{attraction['description']}")
                st.markdown(f"*{attraction['type'].title()}*")
                st.markdown("</div>", unsafe_allow_html=True)
    
    # ============ INTERACTIVE MAP ============
    if show_map:
        st.markdown("## 🗺️ Interactive Map")
        
        # Create base map
        m = folium.Map(location=city_coords, zoom_start=12, tiles="OpenStreetMap")
        
        # Add marker for selected city
        folium.Marker(
            location=city_coords,
            popup=f"{clean_city}",
            tooltip="Your Location",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
        
        # Add tourist attractions if enabled
        if show_attractions and city in ATTRACTIONS:
            for attr in ATTRACTIONS[city]:
                color = {"nature": "green", "cultural": "blue", "historic": "purple", 
                        "shopping": "orange", "food": "pink"}.get(attr["type"], "gray")
                folium.Marker(
                    location=attr["coords"],
                    popup=f"<b>{attr['name']}</b><br>{attr['description']}",
                    tooltip=f"Attraction: {attr['name']}",
                    icon=folium.Icon(color=color)
                ).add_to(m)
        
        # Add circle for visibility if available
        if weather_data and 'visibility' in weather_data and isinstance(weather_data['visibility'], int):
            folium.Circle(
                location=city_coords,
                radius=weather_data['visibility'],
                color="#3186cc",
                fill=True,
                fill_color="#3186cc",
                fill_opacity=0.2,
                weight=2
            ).add_to(m)
        
        # Display the map
        folium_static(m, width=900, height=500)
    
    # ============ ITINERARY GENERATOR ============
    if 'generate_itinerary' in st.session_state and st.session_state.generate_itinerary:
        st.markdown("## 📝 Suggested 1-Day Itinerary")
        
        if city in ATTRACTIONS and len(ATTRACTIONS[city]) >= 2:
            attractions = ATTRACTIONS[city]
            morning_attr = random.choice(attractions)
            afternoon_attr = random.choice([a for a in attractions if a != morning_attr])
            
            state_key = state if state in FOOD_RECOMMENDATIONS else "Kuala Lumpur"
            food_data = FOOD_RECOMMENDATIONS.get(state_key, {"dishes": ["local cuisine"]})
            lunch_dish = random.choice(food_data["dishes"])
            
            itinerary = f"""
            **Morning (9AM-12PM):** Visit {morning_attr['name']}
            _{morning_attr['description']}_
            
            **Lunch (12PM-2PM):** Try {lunch_dish} at a local restaurant
            
            **Afternoon (2PM-5PM):** Explore {afternoon_attr['name']}
            _{afternoon_attr['description']}_
            
            **Evening (7PM+):** Dinner at a local restaurant featuring {state_key} cuisine
            """
            st.markdown(itinerary)
            
            # Weather advisory for the day
            if weather_data and 'main' in weather_data:
                temp = weather_data['main']['temp']
                if temp > 32:
                    st.warning("⚠️ Hot weather expected - bring sunscreen and stay hydrated!")
                elif 'rain' in weather_data:
                    st.info("🌧️ Rain possible - consider indoor attractions or bring an umbrella!")
                    
            st.session_state.generate_itinerary = False
        else:
            # Generate generic itinerary
            state_key = state if state in FOOD_RECOMMENDATIONS else "Kuala Lumpur"
            food_data = FOOD_RECOMMENDATIONS.get(state_key, {"dishes": ["local cuisine"]})
            
            generic_itinerary = f"""
            **Morning (9AM-12PM):** Explore the city center and local markets
            
            **Lunch (12PM-2PM):** Try {random.choice(food_data["dishes"])} at a recommended restaurant
            
            **Afternoon (2PM-5PM):** Visit cultural sites and take photos
            
            **Evening (7PM+):** Experience local nightlife and street food
            """
            st.markdown(generic_itinerary)
            st.info("💡 More specific attractions will be added for this city soon!")
            st.session_state.generate_itinerary = False
    
    # ============ 5-DAY FORECAST ============
    if show_forecast:
        st.markdown("## 📅 5-Day Weather Forecast")
        
        if forecast_data and 'list' in forecast_data:
            # Process forecast data
            forecast_days = {}
            for item in forecast_data['list']:
                date = datetime.datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                if date not in forecast_days:
                    forecast_days[date] = {
                        'temps': [],
                        'icons': [],
                        'descriptions': [],
                        'humidity': []
                    }
                forecast_days[date]['temps'].append(item['main']['temp'])
                forecast_days[date]['icons'].append(item['weather'][0]['icon'])
                forecast_days[date]['descriptions'].append(item['weather'][0]['description'])
                forecast_days[date]['humidity'].append(item['main']['humidity'])
            
            # Create forecast chart
            fig = go.Figure()
            
            # Add temperature trace
            dates = sorted(forecast_days.keys())
            avg_temps = [round(sum(forecast_days[date]['temps'])/len(forecast_days[date]['temps']), 1) for date in dates]
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=avg_temps,
                mode='lines+markers',
                name='Temperature',
                line=dict(color='#FF7043', width=3),
                marker=dict(size=10, color='#FF7043'),
                hovertemplate='%{y}' + temp_unit
            ))
            
            # Add humidity trace
            avg_humidity = [round(sum(forecast_days[date]['humidity'])/len(forecast_days[date]['humidity']), 1) for date in dates]
            
            fig.add_trace(go.Bar(
                x=dates,
                y=avg_humidity,
                name='Humidity',
                marker_color='#4FC3F7',
                opacity=0.6,
                yaxis='y2'
            ))
            
            # Update layout
            fig.update_layout(
                template="plotly_dark",
                xaxis_title="Date",
                yaxis_title=f"Temperature ({temp_unit})",
                yaxis2=dict(
                    title="Humidity (%)",
                    overlaying="y",
                    side="right",
                    range=[0, 100]
                ),
                hovermode="x unified",
                plot_bgcolor='#1E293B',
                paper_bgcolor='#0E1117',
                font=dict(color='#FAFAFA'),
                height=450,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Daily forecast details
            st.markdown("### 📊 Daily Forecast Details")
            cols = st.columns(len(dates))
            for i, col in enumerate(cols):
                with col:
                    day_name = datetime.datetime.strptime(dates[i], '%Y-%m-%d').strftime('%a')
                    st.markdown(f"**{day_name} ({dates[i]})**")
                    
                    # Get most common icon and description
                    icon = max(set(forecast_days[dates[i]]['icons']), key=forecast_days[dates[i]]['icons'].count)
                    desc = max(set(forecast_days[dates[i]]['descriptions']), key
