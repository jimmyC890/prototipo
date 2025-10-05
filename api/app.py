from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from processing import nitrogen_dioxide_consumer as n
from processing import ozone_consumer as o
from processing import pm25_consumer as p
from forecasting.air_quality_forecast import AirQualityForecast
from chatbot.chatbot_aqi import AirQualityChatbot

app = FastAPI(title="Air Guardian API")

# Permitir CORS para Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Leer CSVs y procesar AQI ---
no2 = n.read_nitrogen_dioxide("./data/nitrogen_dioxide.csv")
o3  = o.read_ozone("./data/ozone.csv")
pm25 = p.read_pm25("./data/pm25.csv")

forecast = AirQualityForecast(no2, o3, pm25)
df_aqi = forecast.calculate_aqi()

# --- Crear chatbot y generar recomendaciones ---
chatbot = AirQualityChatbot(df_aqi)
df_recommendations = chatbot.generate_recommendations()

# ---------------------------------------
# Endpoint para usuarios normales
# ---------------------------------------
@app.get("/api/recommendations/normal")
def recommendations_normal():
    result = []
    for _, row in df_recommendations.iterrows():
        rec = row['Recomendación']
        result.append({
            "FechaHora": row['FechaHora'],
            "Recomendación": rec['saludable']
        })
    return result

# ---------------------------------------
# Endpoint para usuarios con EPOC
# ---------------------------------------
@app.get("/api/recommendations/epoc")
def recommendations_epoc():
    result = []
    for _, row in df_recommendations.iterrows():
        rec = row['Recomendación']
        result.append({
            "FechaHora": row['FechaHora'],
            "Recomendación": rec['EPOC']
        })
    return result

# ---------------------------------------
# Endpoint para usuarios con Asma
# ---------------------------------------
@app.get("/api/recommendations/asma")
def recommendations_asma():
    result = []
    for _, row in df_recommendations.iterrows():
        rec = row['Recomendación']
        result.append({
            "FechaHora": row['FechaHora'],
            "Recomendación": rec['asma']
        })
    return result

@app.get("/api/aqi")
def get_current_aqi():
    """
    Devuelve el AQI más reciente y el nivel de calidad del aire
    usando AirQualityForecast.
    """
    # Usando los DataFrames ya procesados
    # df_aqi fue creado con:
    # forecast = AirQualityForecast(no2, o3, pm25)
    # df_aqi = forecast.calculate_aqi()
    
    latest = df_aqi.iloc[-1]  # último registro
    return {
        "FechaHora": latest['FechaHora'],
        "AQI": float(latest['AQI']),
        "Nivel_AQI": latest['Nivel_AQI']
    }