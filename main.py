import pandas as pd
from processing import nitrogen_dioxide_consumer as n
from processing import ozone_consumer as o
from processing import pm25_consumer as p
from forecasting.air_quality_forecast import AirQualityForecast
from chatbot.chatbot_aqi import AirQualityChatbot
from forecasting.air_quality_narx import AirQualityNARX
from fastapi import FastAPI


if __name__ == "__main__":
  app = FastAPI()
  
  no2 = n.read_nitrogen_dioxide("./data/nitrogen_dioxide.csv")
  o3 = o.read_ozone("./data/ozone.csv")
  pm25 = p.read_pm25("./data/pm25.csv")
  
  print(no2, o3, pm25)

  # --- Crear objeto forecasting ---
  forecast = AirQualityForecast(no2, o3, pm25)

  # --- Calcular AQI por hora ---
  df_aqi = forecast.calculate_aqi()

  # --- Mostrar resultados ---
  print(df_aqi[['FechaHora','PM25','O3','NO2','AQI','Nivel_AQI']].head(24))

  # --- Crear chatbot ---
  chatbot = AirQualityChatbot(df_aqi)
  df_recommendations = chatbot.generate_recommendations()

  # --- Mostrar recomendaciones para primeras 24 horas ---
  print(df_recommendations.head(24))

  # --- Entrenar linear + NARX ---
  narx = AirQualityNARX(df_aqi)
  r2_linear = narx.train_linear()
  print("R² Linear:", r2_linear)

  r2_narx = narx.train_narx()
  print("R² NARX:", r2_narx)

  # --- Predicción próximas 6 horas ---
  pred_linear = narx.predict_linear(steps=6)
  pred_narx   = narx.predict_narx(steps=6)

  print("Predicción Linear:", pred_linear)
  print("Predicción NARX:", pred_narx)

  # --- Aquí colocas la gráfica ---
  import matplotlib.pyplot as plt

  plt.figure(figsize=(10,5))
  plt.plot(range(len(df_aqi)), df_aqi['AQI'], label='AQI Histórico', marker='o')
  plt.plot(range(len(df_aqi), len(df_aqi)+len(pred_linear)), pred_linear, 'r--', label='Predicción Linear', marker='x')
  plt.plot(range(len(df_aqi), len(df_aqi)+len(pred_narx)), pred_narx, 'g--', label='Predicción NARX', marker='s')
  plt.xlabel('Hora')
  plt.ylabel('AQI')
  plt.title('Predicción de calidad del aire: Linear vs NARX')
  plt.legend()
  plt.grid(True)
  plt.show()
  
  

