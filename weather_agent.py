import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

# --- 1. CONFIGURATION ---
# Set these as environment variables in GitHub Actions or your local machine
SENDER_EMAIL = os.getenv('SENDER_EMAIL') 
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD') # Use an App Password, not your real password
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')

# Coordinates for the requested Departamentos
LOCATIONS = {
    "San Pedro": {"lat": -24.0, "lon": -56.5},
    "Canindeyú": {"lat": -24.0, "lon": -54.5},
    "Itapúa": {"lat": -27.3, "lon": -55.9},
    "Caaguazú": {"lat": -25.4, "lon": -56.4},
    "Presidente Hayes (Villa Hayes)": {"lat": -25.1, "lon": -57.6},
    "Boquerón": {"lat": -22.3, "lon": -60.0},
    "Alto Paraná": {"lat": -25.5, "lon": -54.6}
}

def fetch_weather():
    """Fetches daily forecast from Open-Meteo API for all locations."""
    weather_report = []
    
    for name, coords in LOCATIONS.items():
        url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=America/Asuncion"
        
        response = requests.get(url)
        data = response.json()
        
        # Get today's data (index 0)
        daily = data['daily']
        max_temp = daily['temperature_2m_max'][0]
        min_temp = daily['temperature_2m_min'][0]
        rain_prob = daily['precipitation_probability_max'][0]
        
        weather_report.append(
            f"📍 {name}:\n   Max: {max_temp}°C | Min: {min_temp}°C | Rain Probability: {rain_prob}%\n"
        )
    
    return "\n".join(weather_report)

def send_email(weather_text):
    """Sends the formatted weather data via email."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"🌤️ Paraguay Daily Weather Update - {today}"
    
    body = "Here is your daily weather forecast for the key departments in Paraguay:\n\n"
    body += weather_text
    body += "\nStay safe and have a great day!\n- Your Weather Agent"
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Configure for Gmail SMTP
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, text)
        server.quit()
        print("Weather email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    report = fetch_weather()
    send_email(report)