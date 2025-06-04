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
    .food-image {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
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

# Tourist attractions data - Complete for all cities
ATTRACTIONS = {
    "Kuala Lumpur (Federal Territory)": [
        {"name": "Petronas Twin Towers", "coords": (3.1579, 101.7116), "type": "landmark", "icon": "tower"},
        {"name": "Batu Caves", "coords": (3.2373, 101.6839), "type": "nature", "icon": "mountain"},
        {"name": "Merdeka Square", "coords": (3.1479, 101.6937), "type": "historic", "icon": "landmark"},
        {"name": "KL Tower", "coords": (3.1529, 101.7030), "type": "landmark", "icon": "tower"},
        {"name": "Central Market", "coords": (3.1434, 101.6958), "type": "cultural", "icon": "shopping"}
    ],
    "Putrajaya (Federal Territory)": [
        {"name": "Putra Mosque", "coords": (2.9264, 101.6964), "type": "cultural", "icon": "mosque"},
        {"name": "Putrajaya Lake", "coords": (2.9158, 101.6942), "type": "nature", "icon": "lake"},
        {"name": "Prime Minister's Office", "coords": (2.9264, 101.6964), "type": "landmark", "icon": "building"}
    ],
    "Labuan (Federal Territory)": [
        {"name": "Labuan War Cemetery", "coords": (5.2767, 115.2417), "type": "historic", "icon": "memorial"},
        {"name": "Chimney Museum", "coords": (5.2767, 115.2417), "type": "cultural", "icon": "museum"},
        {"name": "Surrender Point", "coords": (5.2767, 115.2417), "type": "historic", "icon": "landmark"}
    ],
    "George Town (Penang)": [
        {"name": "Kek Lok Si Temple", "coords": (5.4030, 100.2732), "type": "cultural", "icon": "temple"},
        {"name": "Penang Hill", "coords": (5.4289, 100.2569), "type": "nature", "icon": "mountain"},
        {"name": "Georgetown UNESCO Site", "coords": (5.4141, 100.3288), "type": "historic", "icon": "landmark"},
        {"name": "Clan Houses", "coords": (5.4141, 100.3288), "type": "cultural", "icon": "building"}
    ],
    "Johor Bahru (Johor)": [
        {"name": "Sultan Abu Bakar Mosque", "coords": (1.4655, 103.7578), "type": "cultural", "icon": "mosque"},
        {"name": "Johor Bahru City Square", "coords": (1.4655, 103.7578), "type": "shopping", "icon": "shopping"},
        {"name": "Danga Bay", "coords": (1.4419, 103.6793), "type": "nature", "icon": "beach"},
        {"name": "Istana Besar", "coords": (1.4655, 103.7578), "type": "historic", "icon": "palace"}
    ],
    "Alor Setar (Kedah)": [
        {"name": "Alor Setar Tower", "coords": (6.1214, 100.3695), "type": "landmark", "icon": "tower"},
        {"name": "Zahir Mosque", "coords": (6.1214, 100.3695), "type": "cultural", "icon": "mosque"},
        {"name": "Paddy Museum", "coords": (6.1214, 100.3695), "type": "cultural", "icon": "museum"},
        {"name": "Pekan Rabu Market", "coords": (6.1214, 100.3695), "type": "cultural", "icon": "shopping"}
    ],
    "Kota Bharu (Kelantan)": [
        {"name": "Istana Jahar", "coords": (6.1256, 102.2432), "type": "historic", "icon": "palace"},
        {"name": "Central Market", "coords": (6.1256, 102.2432), "type": "cultural", "icon": "shopping"},
        {"name": "State Museum", "coords": (6.1256, 102.2432), "type": "cultural", "icon": "museum"},
        {"name": "Handicraft Village", "coords": (6.1256, 102.2432), "type": "cultural", "icon": "craft"}
    ],
    "Malacca (Malacca)": [
        {"name": "A Famosa", "coords": (2.1896, 102.2501), "type": "historic", "icon": "landmark"},
        {"name": "Christ Church", "coords": (2.1944, 102.2501), "type": "cultural", "icon": "church"},
        {"name": "Jonker Street", "coords": (2.1944, 102.2501), "type": "cultural", "icon": "shopping"},
        {"name": "Stadthuys", "coords": (2.1944, 102.2501), "type": "historic", "icon": "building"},
        {"name": "Malacca River", "coords": (2.1896, 102.2501), "type": "nature", "icon": "river"}
    ],
    "Seremban (Negeri Sembilan)": [
        {"name": "State Museum", "coords": (2.7259, 101.9424), "type": "cultural", "icon": "museum"},
        {"name": "Lake Gardens", "coords": (2.7259, 101.9424), "type": "nature", "icon": "park"},
        {"name": "Centipede Temple", "coords": (2.7259, 101.9424), "type": "cultural", "icon": "temple"},
        {"name": "Minangkabau Architecture", "coords": (2.7259, 101.9424), "type": "cultural", "icon": "building"}
    ],
    "Kuantan (Pahang)": [
        {"name": "Teluk Cempedak Beach", "coords": (3.8077, 103.3260), "type": "nature", "icon": "beach"},
        {"name": "Sultan Ahmad Shah Mosque", "coords": (3.8077, 103.3260), "type": "cultural", "icon": "mosque"},
        {"name": "Kuantan River", "coords": (3.8077, 103.3260), "type": "nature", "icon": "river"},
        {"name": "Natural Batik Village", "coords": (3.8077, 103.3260), "type": "cultural", "icon": "craft"}
    ],
    "Ipoh (Perak)": [
        {"name": "Kellie's Castle", "coords": (4.5975, 101.0901), "type": "historic", "icon": "castle"},
        {"name": "Cave Temples", "coords": (4.5975, 101.0901), "type": "cultural", "icon": "temple"},
        {"name": "Old Town", "coords": (4.5975, 101.0901), "type": "historic", "icon": "landmark"},
        {"name": "Concubine Lane", "coords": (4.5975, 101.0901), "type": "cultural", "icon": "shopping"}
    ],
    "Kangar (Perlis)": [
        {"name": "Perlis State Park", "coords": (6.4414, 100.1986), "type": "nature", "icon": "park"},
        {"name": "Wang Kelian Market", "coords": (6.4414, 100.1986), "type": "cultural", "icon": "shopping"},
        {"name": "Kota Kayang Museum", "coords": (6.4414, 100.1986), "type": "cultural", "icon": "museum"},
        {"name": "Al-Hussain Mosque", "coords": (6.4414, 100.1986), "type": "cultural", "icon": "mosque"}
    ],
    "Kota Kinabalu (Sabah)": [
        {"name": "Mount Kinabalu", "coords": (5.9804, 116.0735), "type": "nature", "icon": "mountain"},
        {"name": "Tunku Abdul Rahman Park", "coords": (5.9804, 116.0735), "type": "nature", "icon": "island"},
        {"name": "Signal Hill Observatory", "coords": (5.9804, 116.0735), "type": "landmark", "icon": "tower"},
        {"name": "Filipino Market", "coords": (5.9804, 116.0735), "type": "cultural", "icon": "shopping"}
    ],
    "Kuching (Sarawak)": [
        {"name": "Sarawak Cultural Village", "coords": (1.5397, 110.3542), "type": "cultural", "icon": "village"},
        {"name": "Kuching Waterfront", "coords": (1.5397, 110.3542), "type": "nature", "icon": "river"},
        {"name": "Cat Museum", "coords": (1.5397, 110.3542), "type": "cultural", "icon": "museum"},
        {"name": "Semenggoh Wildlife Centre", "coords": (1.5397, 110.3542), "type": "nature", "icon": "wildlife"}
    ],
    "Shah Alam (Selangor)": [
        {"name": "Blue Mosque", "coords": (3.0733, 101.5185), "type": "cultural", "icon": "mosque"},
        {"name": "i-City Theme Park", "coords": (3.0733, 101.5185), "type": "entertainment", "icon": "park"},
        {"name": "Shah Alam Lake", "coords": (3.0733, 101.5185), "type": "nature", "icon": "lake"},
        {"name": "Gallery Shah Alam", "coords": (3.0733, 101.5185), "type": "cultural", "icon": "gallery"}
    ],
    "Kuala Terengganu (Terengganu)": [
        {"name": "Crystal Mosque", "coords": (5.3296, 103.1370), "type": "cultural", "icon": "mosque"},
        {"name": "Terengganu State Museum", "coords": (5.3296, 103.1370), "type": "cultural", "icon": "museum"},
        {"name": "Chinatown", "coords": (5.3296, 103.1370), "type": "cultural", "icon": "shopping"},
        {"name": "Drawbridge", "coords": (5.3296, 103.1370), "type": "landmark", "icon": "bridge"}
    ]
}

# Food recommendations with descriptions - Complete for all states
FOOD_RECOMMENDATIONS = {
    "Johor": {
        "dishes": "Laksa Johor, Mee Bandung Muar, Satay, Otak-Otak",
        "description": "Johor's cuisine features rich coconut-based curries and spicy noodle dishes with unique Malay-Javanese influences.",
        "image": "/images/food/johor-laksa.jpg"
    },
    "Kedah": {
        "dishes": "Laksa Kedah, Nasi Ulam, Pulut Panggang, Jeruk Mangga",
        "description": "Known for its rice-based dishes and traditional Malay herbs, Kedah offers authentic northern Malaysian flavors.",
        "image": "/images/food/kl-nasi-lemak.jpg"
    },
    "Kelantan": {
        "dishes": "Nasi Kerabu, Ayam Percik, Solok Lada, Keropok Lekor",
        "description": "Kelantan's colorful blue rice and grilled specialties showcase the state's vibrant culinary heritage.",
        "image": "/images/food/kelantan-nasi-kerabu.jpg"
    },
    "Malacca": {
        "dishes": "Chicken Rice Ball, Cendol, Nyonya Laksa, Satay Celup",
        "description": "Historic Malacca blends Peranakan, Portuguese, and Malay cuisines in unique fusion dishes.",
        "image": "/images/food/malacca-chicken-rice-ball.jpg"
    },
    "Negeri Sembilan": {
        "dishes": "Masak Lemak Cili Api, Rendang Daging, Gulai Tempoyak",
        "description": "Minangkabau-influenced cuisine featuring coconut milk curries and spicy traditional dishes.",
        "image": "/images/food/kl-nasi-lemak.jpg"
    },
    "Pahang": {
        "dishes": "Ikan Patin Masak Tempoyak, Keropok Lekor, Gulai Kawah",
        "description": "River fish specialties and fermented durian dishes highlight Pahang's unique inland cuisine.",
        "image": "/images/food/kl-nasi-lemak.jpg"
    },
    "Penang": {
        "dishes": "Char Kway Teow, Assam Laksa, Penang Rojak, Cendol",
        "description": "UNESCO-recognized street food paradise with Chinese-Malay fusion creating iconic hawker dishes.",
        "image": "/images/food/penang-char-kway-teow.jpg"
    },
    "Perak": {
        "dishes": "Ipoh White Coffee, Taugeh Ayam, Hor Fun, Dim Sum",
        "description": "Famous for its white coffee and fresh bean sprouts, Ipoh offers refined Cantonese-influenced cuisine.",
        "image": "/images/food/ipoh-white-coffee.jpg"
    },
    "Perlis": {
        "dishes": "Laksa Perlis, Harum Manis Mango, Jeruk Kedondong",
        "description": "Malaysia's smallest state offers sweet mangoes and unique northern border flavors.",
        "image": "/images/food/kl-nasi-lemak.jpg"
    },
    "Sabah": {
        "dishes": "Hinava, Ambuyat, Tuhau, Bosou, Pinasakan",
        "description": "Indigenous Kadazan-Dusun cuisine featuring raw fish salads and exotic jungle ingredients.",
        "image": "/images/food/sabah-hinava.jpg"
    },
    "Sarawak": {
        "dishes": "Sarawak Laksa, Kolo Mee, Manok Pansuh, Midin Belacan",
        "description": "Dayak and Chinese influences create unique dishes like bamboo chicken and jungle fern vegetables.",
        "image": "/images/food/sarawak-laksa.jpg"
    },
    "Selangor": {
        "dishes": "Bak Kut Teh, Yong Tau Foo, Hokkien Mee, Satay Kajang",
        "description": "Malaysia's most developed state offers diverse urban cuisine from traditional to modern fusion.",
        "image": "/images/food/kl-nasi-lemak.jpg"
    },
    "Terengganu": {
        "dishes": "Keropok Lekor, Nasi Dagang, Satar, Nekbat",
        "description": "East coast seafood specialties and coconut-rich dishes reflect Terengganu's maritime culture.",
        "image": "/images/food/kl-nasi-lemak.jpg"
    },
    "Federal Territory": {
        "dishes": "Nasi Lemak, Satay, Bak Kut Teh, Roti Canai, Char Kway Teow",
        "description": "Malaysia's capital showcases the best of all regional cuisines in one cosmopolitan food scene.",
        "image": "/images/food/kl-nasi-lemak.jpg"
    }
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
            
            population_data = {
                "Johor Bahru": "1.8 million",
                "Kuala Lumpur": "1.9 million",
                "George Town": "0.7 million",
                "Malacca": "0.5 million",
                "Ipoh": "0.7 million",
                "Kuching": "0.6 million",
                "Kota Kinabalu": "0.5 million",
                "Alor Setar": "0.4 million",
                "Kota Bharu": "0.3 million",
                "Seremban": "0.5 million",
                "Kuantan": "0.6 million",
                "Kangar": "0.1 million",
                "Shah Alam": "0.7 million",
                "Kuala Terengganu": "0.4 million",
                "Putrajaya": "0.1 million",
                "Labuan": "0.1 million"
            }
            st.markdown(f"**Population:** {population_data.get(clean_city, 'Data not available')}")
            
        with col2:
            st.markdown("### 🌟 Did You Know?")
            fun_facts = {
                "Johor Bahru": "Gateway to Singapore via the Causeway",
                "Kuala Lumpur": "Home to the Petronas Twin Towers",
                "George Town": "UNESCO World Heritage Site",
                "Malacca": "Historic trading port and UNESCO World Heritage Site",
                "Ipoh": "Famous for white coffee and limestone caves",
                "Kuching": "Cat City with beautiful riverfront",
                "Kota Kinabalu": "Gateway to Mount Kinabalu",
                "Alor Setar": "Birthplace of former Prime Ministers",
                "Kota Bharu": "Cultural heart of Kelantan",
                "Seremban": "Known for Minangkabau architecture",
                "Kuantan": "Gateway to the East Coast",
                "Kangar": "Malaysia's smallest state capital",
                "Shah Alam": "Planned city with the Blue Mosque",
                "Kuala Terengganu": "Home to the Crystal Mosque",
                "Putrajaya": "Malaysia's administrative capital",
                "Labuan": "Federal territory and duty-free island"
            }
            st.info(fun_facts.get(clean_city, "A beautiful Malaysian city with rich culture"))
    
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
            aqi = aqi_data['list'][0]['main']['aqi'] if aqi_data else 1
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
        food_info = FOOD_RECOMMENDATIONS.get(state, FOOD_RECOMMENDATIONS["Federal Territory"])
        
        # Display food information in columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### **{food_info['dishes']}**")
            st.markdown(f"*{food_info['description']}*")
            
            # Add some popular restaurants/locations
            restaurant_suggestions = {
                "Johor": "📍 **Where to try:** Muar town for authentic Mee Bandung, JB Central for Laksa Johor",
                "Penang": "📍 **Where to try:** Gurney Drive, Penang Road, Georgetown UNESCO area",
                "Malacca": "📍 **Where to try:** Jonker Street, Heeren Street, Cheng Hoon Teng area",
                "Perak": "📍 **Where to try:** Ipoh Old Town, New Town kopitiam, Concubine Lane",
                "Kelantan": "📍 **Where to try:** Siti Khadijah Market, Kota Bharu night market",
                "Sabah": "📍 **Where to try:** Filipino Market KK, Gaya Street Sunday Market",
                "Sarawak": "📍 **Where to try:** Kuching Waterfront, Top Spot Food Court",
                "Federal Territory": "📍 **Where to try:** Jalan Alor, Petaling Street, Bangsar, KLCC"
            }
            
            if state in restaurant_suggestions:
                st.markdown(restaurant_suggestions[state])
            
        with col2:
            # Display the appropriate food image
            try:
                st.image(food_info['image'], caption=f"Signature dishes of {state}", use_container_width=True)
            except:
                # Fallback to a default food image if specific image not found
                st.image("/images/food/kl-nasi-lemak.jpg", caption=f"Local cuisine of {state}", use_container_width=True)
    
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
            icon=folium.Icon(color="red", icon="info-sign", prefix="fa")
        ).add_to(m)
        
        # Add tourist attractions if enabled
        if show_attractions and city in ATTRACTIONS:
            for attr in ATTRACTIONS[city]:
                folium.Marker(
                    location=attr["coords"],
                    popup=attr["name"],
                    tooltip=f"Attraction: {attr['name']}",
                    icon=folium.Icon(
                        color="green" if attr["type"] == "nature" else "blue",
                        icon=attr.get("icon", "info-sign")
                    )
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
    if 'generate_itinerary' in st.session_state:
        st.markdown("## 📝 Suggested 1-Day Itinerary")
        
        if city in ATTRACTIONS and len(ATTRACTIONS[city]) >= 2:
            morning_attr = random.choice(ATTRACTIONS[city])
            afternoon_attr = random.choice([a for a in ATTRACTIONS[city] if a != morning_attr])
            food_info = FOOD_RECOMMENDATIONS.get(state, FOOD_RECOMMENDATIONS["Federal Territory"])
            
            itinerary = f"""
            **Morning (9AM-12PM):** Visit {morning_attr['name']}
            **Lunch (12PM-2PM):** Try {food_info['dishes'].split(',')[0]} at a local restaurant
            **Afternoon (2PM-5PM):** Explore {afternoon_attr['name']}
            **Evening (7PM+):** Dinner featuring {food_info['dishes'].split(',')[1] if ',' in food_info['dishes'] else 'local specialties'}
            
            💡 **Food Tip:** {food_info['description']}
            """
            st.markdown(itinerary)
            st.session_state.itinerary = itinerary
        else:
            st.warning("Not enough attraction data toimport streamlit as st
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
    .food-image {
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
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

# Tourist attractions data - Complete for all cities
ATTRACTIONS = {
    "Kuala Lumpur (Federal Territory)": [
        {"name": "Petronas Twin Towers", "coords": (3.1579, 101.7116), "type": "landmark", "icon": "tower"},
        {"name": "Batu Caves", "coords": (3.2373, 101.6839), "type": "nature", "icon": "mountain"},
        {"name": "Merdeka Square", "coords": (3.1479, 101.6937), "type": "historic", "icon": "landmark"},
        {"name": "KL Tower", "coords": (3.1529, 101.7030), "type": "landmark", "icon": "tower"},
        {"name": "Central Market", "coords": (3.1434, 101.6958), "type": "cultural", "icon": "shopping"}
    ],
    "Putrajaya (Federal Territory)": [
        {"name": "Putra Mosque", "coords": (2.9264, 101.6964), "type": "cultural", "icon": "mosque"},
        {"name": "Putrajaya Lake", "coords": (2.9158, 101.6942), "type": "nature", "icon": "lake"},
        {"name": "Prime Minister's Office", "coords": (2.9264, 101.6964), "type": "landmark", "icon": "building"}
    ],
    "Labuan (Federal Territory)": [
        {"name": "Labuan War Cemetery", "coords": (5.2767, 115.2417), "type": "historic", "icon": "memorial"},
        {"name": "Chimney Museum", "coords": (5.2767, 115.2417), "type": "cultural", "icon": "museum"},
        {"name": "Surrender Point", "coords": (5.2767, 115.2417), "type": "historic", "icon": "landmark"}
    ],
    "George Town (Penang)": [
        {"name": "Kek Lok Si Temple", "coords": (5.4030, 100.2732), "type": "cultural", "icon": "temple"},
        {"name": "Penang Hill", "coords": (5.4289, 100.2569), "type": "nature", "icon": "mountain"},
        {"name": "Georgetown UNESCO Site", "coords": (5.4141, 100.3288), "type": "historic", "icon": "landmark"},
        {"name": "Clan Houses", "coords": (5.4141, 100.3288), "type": "cultural", "icon": "building"}
    ],
    "Johor Bahru (Johor)": [
        {"name": "Sultan Abu Bakar Mosque", "coords": (1.4655, 103.7578), "type": "cultural", "icon": "mosque"},
        {"name": "Johor Bahru City Square", "coords": (1.4655, 103.7578), "type": "shopping", "icon": "shopping"},
        {"name": "Danga Bay", "coords": (1.4419, 103.6793), "type": "nature", "icon": "beach"},
        {"name": "Istana Besar", "coords": (1.4655, 103.7578), "type": "historic", "icon": "palace"}
    ],
    "Alor Setar (Kedah)": [
        {"name": "Alor Setar Tower", "coords": (6.1214, 100.3695), "type": "landmark", "icon": "tower"},
        {"name": "Zahir Mosque", "coords": (6.1214, 100.3695), "type": "cultural", "icon": "mosque"},
        {"name": "Paddy Museum", "coords": (6.1214, 100.3695), "type": "cultural", "icon": "museum"},
        {"name": "Pekan Rabu Market", "coords": (6.1214, 100.3695), "type": "cultural", "icon": "shopping"}
    ],
    "Kota Bharu (Kelantan)": [
        {"name": "Istana Jahar", "coords": (6.1256, 102.2432), "type": "historic", "icon": "palace"},
        {"name": "Central Market", "coords": (6.1256, 102.2432), "type": "cultural", "icon": "shopping"},
        {"name": "State Museum", "coords": (6.1256, 102.2432), "type": "cultural", "icon": "museum"},
        {"name": "Handicraft Village", "coords": (6.1256, 102.2432), "type": "cultural", "icon": "craft"}
    ],
    "Malacca (Malacca)": [
        {"name": "A Famosa", "coords": (2.1896, 102.2501), "type": "historic", "icon": "landmark"},
        {"name": "Christ Church", "coords": (2.1944, 102.2501), "type": "cultural", "icon": "church"},
        {"name": "Jonker Street", "coords": (2.1944, 102.2501), "type": "cultural", "icon": "shopping"},
        {"name": "Stadthuys", "coords": (2.1944, 102.2501), "type": "historic", "icon": "building"},
        {"name": "Malacca River", "coords": (2.1896, 102.2501), "type": "nature", "icon": "river"}
    ],
    "Seremban (Negeri Sembilan)": [
        {"name": "State Museum", "coords": (2.7259, 101.9424), "type": "cultural", "icon": "museum"},
        {"name": "Lake Gardens", "coords": (2.7259, 101.9424), "type": "nature", "icon": "park"},
        {"name": "Centipede Temple", "coords": (2.7259, 101.9424), "type": "cultural", "icon": "temple"},
        {"name": "Minangkabau Architecture", "coords": (2.7259, 101.9424), "type": "cultural", "icon": "building"}
    ],
    "Kuantan (Pahang)": [
        {"name": "Teluk Cempedak Beach", "coords": (3.8077, 103.3260), "type": "nature", "icon": "beach"},
        {"name": "Sultan Ahmad Shah Mosque", "coords": (3.8077, 103.3260), "type": "cultural", "icon": "mosque"},
        {"name": "Kuantan River", "coords": (3.8077, 103.3260), "type": "nature", "icon": "river"},
        {"name": "Natural Batik Village", "coords": (3.8077, 103.3260), "type": "cultural", "icon": "craft"}
    ],
    "Ipoh (Perak)": [
        {"name": "Kellie's Castle", "coords": (4.5975, 101.0901), "type": "historic", "icon": "castle"},
        {"name": "Cave Temples", "coords": (4.5975, 101.0901), "type": "cultural", "icon": "temple"},
        {"name": "Old Town", "coords": (4.5975, 101.0901), "type": "historic", "icon": "landmark"},
        {"name": "Concubine Lane", "coords": (4.5975, 101.0901), "type": "cultural", "icon": "shopping"}
    ],
    "Kangar (Perlis)": [
        {"name": "Perlis State Park", "coords": (6.4414, 100.1986), "type": "nature", "icon": "park"},
        {"name": "Wang Kelian Market", "coords": (6.4414, 100.1986), "type": "cultural", "icon": "shopping"},
        {"name": "Kota Kayang Museum", "coords": (6.4414, 100.1986), "type": "cultural", "icon": "museum"},
        {"name": "Al-Hussain Mosque", "coords": (6.4414, 100.1986), "type": "cultural", "icon": "mosque"}
    ],
    "Kota Kinabalu (Sabah)": [
        {"name": "Mount Kinabalu", "coords": (5.9804, 116.0735), "type": "nature", "icon": "mountain"},
        {"name": "Tunku Abdul Rahman Park", "coords": (5.9804, 116.0735), "type": "nature", "icon": "island"},
        {"name": "Signal Hill Observatory", "coords": (5.9804, 116.0735), "type": "landmark", "icon": "tower"},
        {"name": "Filipino Market", "coords": (5.9804, 116.0735), "type": "cultural", "icon": "shopping"}
    ],
    "Kuching (Sarawak)": [
        {"name": "Sarawak Cultural Village", "coords": (1.5397, 110.3542), "type": "cultural", "icon": "village"},
        {"name": "Kuching Waterfront", "coords": (1.5397, 110.3542), "type": "nature", "icon": "river"},
        {"name": "Cat Museum", "coords": (1.5397, 110.3542), "type": "cultural", "icon": "museum"},
        {"name": "Semenggoh Wildlife Centre", "coords": (1.5397, 110.3542), "type": "nature", "icon": "wildlife"}
    ],
    "Shah Alam (Selangor)": [
        {"name": "Blue Mosque", "coords": (3.0733, 101.5185), "type": "cultural", "icon": "mosque"},
        {"name": "i-City Theme Park", "coords": (3.0733, 101.5185), "type": "entertainment", "icon": "park"},
        {"name": "Shah Alam Lake", "coords": (3.0733, 101.5185), "type": "nature", "icon": "lake"},
        {"name": "Gallery Shah Alam", "coords": (3.0733, 101.5185), "type": "cultural", "icon": "gallery"}
    ],
    "Kuala Terengganu (Terengganu)": [
        {"name": "Crystal Mosque", "coords": (5.3296, 103.1370), "type": "cultural", "icon": "mosque"},
        {"name": "Terengganu State Museum", "coords": (5.3296, 103.1370), "type": "cultural", "icon": "museum"},
        {"name": "Chinatown", "coords": (5.3296, 103.1370), "type": "cultural", "icon": "shopping"},
        {"name": "Drawbridge", "coords": (5.3296, 103.1370), "type": "landmark", "icon": "bridge"}
    ]
}

# Food recommendations with descriptions - Complete for all states
FOOD_RECOMMENDATIONS = {
    "Johor": {
        "dishes": "Laksa Johor, Mee Bandung Muar, Satay, Otak-Otak",
        "description": "Johor's cuisine features rich coconut-based curries and spicy noodle dishes with unique Malay-Javanese influences.",
        "image": "/images/food/johor-laksa.jpg"
    },
    "Kedah": {
        "dishes": "Laksa Kedah, Nasi Ulam, Pulut Panggang, Jeruk Mangga",
        "description": "Known for its rice-based dishes and traditional Malay herbs, Kedah offers authentic northern Malaysian flavors.",
        "image": "/images/food/kl-nasi-lemak.jpg"
    },
    "Kelantan": {
        "dishes": "Nasi Kerabu, Ayam Percik, Solok Lada, Keropok Lekor",
        "description": "Kelantan's colorful blue rice and grilled specialties showcase the state's vibrant culinary heritage.",
        "image": "/images/food/kelantan-nasi-kerabu.jpg"
    },
    "Malacca": {
        "dishes": "Chicken Rice Ball, Cendol, Nyonya Laksa, Satay Celup",
        "description": "Historic Malacca blends Peranakan, Portuguese, and Malay cuisines in unique fusion dishes.",
        "image": "/images/food/malacca-chicken-rice-ball.jpg"
    },
    "Negeri Sembilan": {
        "dishes": "Masak Lemak Cili Api, Rendang Daging, Gulai Tempoyak",
        "description": "Minangkabau-influenced cuisine featuring coconut milk curries and spicy traditional dishes.",
        "image": "/images/food/kl-nasi-lemak.jpg"
    },
    "Pahang": {
        "dishes": "Ikan Patin Masak Tempoyak, Keropok Lekor, Gulai Kawah",
        "description": "River fish specialties and fermented durian dishes highlight Pahang's unique inland cuisine.",
        "image": "/images/food/kl-nasi-lemak.jpg"
    },
    "Penang": {
        "dishes": "Char Kway Teow, Assam Laksa, Penang Rojak, Cendol",
        "description": "UNESCO-recognized street food paradise with Chinese-Malay fusion creating iconic hawker dishes.",
        "image": "/images/food/penang-char-kway-teow.jpg"
    },
    "Perak": {
        "dishes": "Ipoh White Coffee, Taugeh Ayam, Hor Fun, Dim Sum",
        "description": "Famous for its white coffee and fresh bean sprouts, Ipoh offers refined Cantonese-influenced cuisine.",
        "image": "/images/food/ipoh-white-coffee.jpg"
    },
    "Perlis": {
        "dishes": "Laksa Perlis, Harum Manis Mango, Jeruk Kedondong",
        "description": "Malaysia's smallest state offers sweet mangoes and unique northern border flavors.",
        "image": "/images/food/kl-nasi-lemak.jpg"
    },
    "Sabah": {
        "dishes": "Hinava, Ambuyat, Tuhau, Bosou, Pinasakan",
        "description": "Indigenous Kadazan-Dusun cuisine featuring raw fish salads and exotic jungle ingredients.",
        "image": "/images/food/sabah-hinava.jpg"
    },
    "Sarawak": {
        "dishes": "Sarawak Laksa, Kolo Mee, Manok Pansuh, Midin Belacan",
        "description": "Dayak and Chinese influences create unique dishes like bamboo chicken and jungle fern vegetables.",
        "image": "/images/food/sarawak-laksa.jpg"
    },
    "Selangor": {
        "dishes": "Bak Kut Teh, Yong Tau Foo, Hokkien Mee, Satay Kajang",
        "description": "Malaysia's most developed state offers diverse urban cuisine from traditional to modern fusion.",
        "image": "/images/food/kl-nasi-lemak.jpg"
    },
    "Terengganu": {
        "dishes": "Keropok Lekor, Nasi Dagang, Satar, Nekbat",
        "description": "East coast seafood specialties and coconut-rich dishes reflect Terengganu's maritime culture.",
        "image": "/images/food/kl-nasi-lemak.jpg"
    },
    "Federal Territory": {
        "dishes": "Nasi Lemak, Satay, Bak Kut Teh, Roti Canai, Char Kway Teow",
        "description": "Malaysia's capital showcases the best of all regional cuisines in one cosmopolitan food scene.",
        "image": "/images/food/kl-nasi-lemak.jpg"
    }
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
            
            population_data = {
                "Johor Bahru": "1.8 million",
                "Kuala Lumpur": "1.9 million",
                "George Town": "0.7 million",
                "Malacca": "0.5 million",
                "Ipoh": "0.7 million",
                "Kuching": "0.6 million",
                "Kota Kinabalu": "0.5 million",
                "Alor Setar": "0.4 million",
                "Kota Bharu": "0.3 million",
                "Seremban": "0.5 million",
                "Kuantan": "0.6 million",
                "Kangar": "0.1 million",
                "Shah Alam": "0.7 million",
                "Kuala Terengganu": "0.4 million",
                "Putrajaya": "0.1 million",
                "Labuan": "0.1 million"
            }
            st.markdown(f"**Population:** {population_data.get(clean_city, 'Data not available')}")
            
        with col2:
            st.markdown("### 🌟 Did You Know?")
            fun_facts = {
                "Johor Bahru": "Gateway to Singapore via the Causeway",
                "Kuala Lumpur": "Home to the Petronas Twin Towers",
                "George Town": "UNESCO World Heritage Site",
                "Malacca": "Historic trading port and UNESCO World Heritage Site",
                "Ipoh": "Famous for white coffee and limestone caves",
                "Kuching": "Cat City with beautiful riverfront",
                "Kota Kinabalu": "Gateway to Mount Kinabalu",
                "Alor Setar": "Birthplace of former Prime Ministers",
                "Kota Bharu": "Cultural heart of Kelantan",
                "Seremban": "Known for Minangkabau architecture",
                "Kuantan": "Gateway to the East Coast",
                "Kangar": "Malaysia's smallest state capital",
                "Shah Alam": "Planned city with the Blue Mosque",
                "Kuala Terengganu": "Home to the Crystal Mosque",
                "Putrajaya": "Malaysia's administrative capital",
                "Labuan": "Federal territory and duty-free island"
            }
            st.info(fun_facts.get(clean_city, "A beautiful Malaysian city with rich culture"))
    
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
            aqi = aqi_data['list'][0]['main']['aqi'] if aqi_data else 1
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
        food_info = FOOD_RECOMMENDATIONS.get(state, FOOD_RECOMMENDATIONS["Federal Territory"])
        
        # Display food information in columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### **{food_info['dishes']}**")
            st.markdown(f"*{food_info['description']}*")
            
            # Add some popular restaurants/locations
            restaurant_suggestions = {
                "Johor": "📍 **Where to try:** Muar town for authentic Mee Bandung, JB Central for Laksa Johor",
                "Penang": "📍 **Where to try:** Gurney Drive, Penang Road, Georgetown UNESCO area",
                "Malacca": "📍 **Where to try:** Jonker Street, Heeren Street, Cheng Hoon Teng area",
                "Perak": "📍 **Where to try:** Ipoh Old Town, New Town kopitiam, Concubine Lane",
                "Kelantan": "📍 **Where to try:** Siti Khadijah Market, Kota Bharu night market",
                "Sabah": "📍 **Where to try:** Filipino Market KK, Gaya Street Sunday Market",
                "Sarawak": "📍 **Where to try:** Kuching Waterfront, Top Spot Food Court",
                "Federal Territory": "📍 **Where to try:** Jalan Alor, Petaling Street, Bangsar, KLCC"
            }
            
            if state in restaurant_suggestions:
                st.markdown(restaurant_suggestions[state])
            
        with col2:
            # Display the appropriate food image
            try:
                st.image(food_info['image'], caption=f"Signature dishes of {state}", use_container_width=True)
            except:
                # Fallback to a default food image if specific image not found
                st.image("/images/food/kl-nasi-lemak.jpg", caption=f"Local cuisine of {state}", use_container_width=True)
    
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
            icon=folium.Icon(color="red", icon="info-sign", prefix="fa")
        ).add_to(m)
        
        # Add tourist attractions if enabled
        if show_attractions and city in ATTRACTIONS:
            for attr in ATTRACTIONS[city]:
                folium.Marker(
                    location=attr["coords"],
                    popup=attr["name"],
                    tooltip=f"Attraction: {attr['name']}",
                    icon=folium.Icon(
                        color="green" if attr["type"] == "nature" else "blue",
                        icon=attr.get("icon", "info-sign")
                    )
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
    if 'generate_itinerary' in st.session_state:
        st.markdown("## 📝 Suggested 1-Day Itinerary")
        
        if city in ATTRACTIONS and len(ATTRACTIONS[city]) >= 2:
            morning_attr = random.choice(ATTRACTIONS[city])
            afternoon_attr = random.choice([a for a in ATTRACTIONS[city] if a != morning_attr])
            food_info = FOOD_RECOMMENDATIONS.get(state, FOOD_RECOMMENDATIONS["Federal Territory"])
            
            itinerary = f"""
            **Morning (9AM-12PM):** Visit {morning_attr['name']}
            **Lunch (12PM-2PM):** Try {food_info['dishes'].split(',')[0]} at a local restaurant
            **Afternoon (2PM-5PM):** Explore {afternoon_attr['name']}
            **Evening (7PM+):** Dinner featuring {food_info['dishes'].split(',')[1] if ',' in food_info['dishes'] else 'local specialties'}
            
            💡 **Food Tip:** {food_info['description']}
            """
            st.markdown(itinerary)
            st.session_state.itinerary = itinerary
        else:
            st.warning("Not enough attraction data to generate itinerary")
    
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
            
            # Add weather icons
            for i, date in enumerate(dates):
                icon = max(set(forecast_days[date]['icons']), key=forecast_days[date]['icons'].count)
                fig.add_layout_image(
                    dict(
                        source=get_weather_icon(icon),
                        xref="x",
                        yref="y",
                        x=date,
                        y=max(avg_temps) + (max(avg_temps)-min(avg_temps))*0.2,
                        sizex=0.8,
                        sizey=0.8,
                        xanchor="center",
                        yanchor="middle"
                    )
                )
            
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
                    desc = max(set(forecast_days[dates[i]]['descriptions']), key=forecast_days[dates[i]]['descriptions'].count)
                    
                    st.image(get_weather_icon(icon), width=50)
                    st.markdown(f"**{avg_temps[i]} {temp_unit}**")
                    st.markdown(f"{desc.title()}")
                    st.markdown(f"Humidity: {avg_humidity[i]}%")
        else:
            st.warning("Forecast data not available")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please try selecting a different city or check your internet connection")

# ============ FOOTER ============
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #A9A9A9; font-size: 0.9em;">
        <p>Smart Malaysia Travel Companion • Data from OpenWeatherMap</p>
        <p>Map data © OpenStreetMap contributors • Icons by OpenWeather</p>
    </div>
""", unsafe_allow_html=True)

