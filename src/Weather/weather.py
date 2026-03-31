from flask import Flask, render_template, request, jsonify
import requests
from pathlib import Path
import os
from dotenv import load_dotenv
from vault_local import get_vault

# Try to load from Vault, fall back to .env
def get_api_key():
    """Get API key from local Vault or environment variables"""
    try:
        vault = get_vault()
        secret = vault.read_secret_version(path='weather/openweather')
        api_key = secret['data']['data'].get('api_key')
        if api_key:
            print("✅ API key loaded from Vault")
            return api_key
    except Exception as e:
        print(f"⚠️  Vault access failed ({str(e)}), falling back to .env")
    
    # Fall back to .env
    load_dotenv()
    api_key = os.getenv('OPENWEATHER_API_KEY', 'YOUR_API_KEY_HERE')
    if api_key != 'YOUR_API_KEY_HERE':
        print("✅ API key loaded from .env")
    return api_key

app = Flask(__name__, template_folder='templates', static_folder='static')

# OpenWeatherMap API configuration
OPENWEATHER_API_KEY = get_api_key()
OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5'

# Units: metric for Celsius
UNITS = 'metric'
LANG = 'fr'  # French


@app.route('/')
def index():
    """Display the weather search form"""
    return render_template('index.html')


@app.route('/meteo', methods=['POST'])
def get_weather():
    """Fetch weather data for a given city"""
    try:
        city = request.form.get('city', '').strip()
        
        if not city:
            return render_template('index.html', error='Veuillez entrer le nom d\'une ville')
        
        # Fetch current weather and forecast
        current_weather = fetch_current_weather(city)
        forecast = fetch_forecast(city)
        
        if not current_weather:
            return render_template('index.html', error=f'Ville non trouvée: {city}')
        
        # Extract 5-day forecast (one per day at noon)
        forecast_data = process_forecast(forecast)
        
        return render_template(
            'index.html',
            city=current_weather,
            forecast=forecast_data,
            searched_city=city
        )
    
    except Exception as e:
        return render_template('index.html', error=f'Erreur: {str(e)}')


def fetch_current_weather(city):
    """Fetch current weather data from OpenWeatherMap API"""
    try:
        params = {
            'q': city,
            'appid': OPENWEATHER_API_KEY,
            'units': UNITS,
            'lang': LANG
        }
        
        response = requests.get(
            f'{OPENWEATHER_BASE_URL}/weather',
            params=params,
            timeout=10
        )
        
        if response.status_code == 404:
            return None
        
        response.raise_for_status()
        data = response.json()
        
        return {
            'name': data['name'],
            'country': data['sys']['country'],
            'temperature': round(data['main']['temp'], 1),
            'feels_like': round(data['main']['feels_like'], 1),
            'temp_min': round(data['main']['temp_min'], 1),
            'temp_max': round(data['main']['temp_max'], 1),
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': round(data['wind']['speed'], 1),
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
            'main': data['weather'][0]['main']
        }
    
    except requests.exceptions.RequestException as e:
        raise Exception(f'Erreur lors de l\'appel API météo: {str(e)}')


def fetch_forecast(city):
    """Fetch 5-day forecast from OpenWeatherMap API"""
    try:
        params = {
            'q': city,
            'appid': OPENWEATHER_API_KEY,
            'units': UNITS,
            'lang': LANG,
            'cnt': 40  # 5 days * 8 (3-hour intervals)
        }
        
        response = requests.get(
            f'{OPENWEATHER_BASE_URL}/forecast',
            params=params,
            timeout=10
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise Exception(f'Erreur lors du chargement des prévisions: {str(e)}')


def process_forecast(forecast_data):
    """Process forecast data to get one forecast per day"""
    processed = []
    seen_days = set()
    
    for item in forecast_data['list']:
        date = item['dt_txt'].split(' ')[0]  # YYYY-MM-DD
        
        # Skip if we already have a forecast for this day
        if date in seen_days:
            continue
        
        seen_days.add(date)
        
        processed.append({
            'date': date,
            'temp': round(item['main']['temp'], 1),
            'temp_min': round(item['main']['temp_min'], 1),
            'temp_max': round(item['main']['temp_max'], 1),
            'description': item['weather'][0]['description'],
            'icon': item['weather'][0]['icon'],
            'main': item['weather'][0]['main'],
            'humidity': item['main']['humidity'],
            'wind_speed': round(item['wind']['speed'], 1)
        })
        
        if len(processed) >= 5:
            break
    
    return processed


if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    Path('templates').mkdir(exist_ok=True)
    Path('static').mkdir(exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)