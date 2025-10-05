import pandas as pd

class AirQualityChatbot:
    """
    Chatbot para dar recomendaciones a personas con bronquitis o EPOC
    según el AQI horario.
    """

    def __init__(self, df_aqi: pd.DataFrame):
        self.df_aqi = df_aqi.copy()

    def generate_recommendations(self):
        """
        Genera recomendaciones creativas para cada hora
        suavizando los mensajes y evitando negaciones directas.
        """
        def recommend(row):
            aqi = row['AQI']
            if aqi <= 50:  # nivel “estable”
              return {
              "asma": "Aire seguro — ideal para actividades al aire libre.",
              "EPOC": "Condiciones estables — puedes salir con precaución.",
              "saludable": "Excelente momento para salir y respirar aire fresco."
            }
            elif 51 <= aqi <= 100:  # nivel “intermedio bajo”
                return {
                    "asma": "Nivel moderado: puede sentirse molesto en personas con asma, evita esfuerzos prolongados al aire libre.",
                    "EPOC": "Intermedio: limita actividades intensas y monitorea síntomas.",
                    "saludable": "Buen aire para la mayoría, aunque personas sensibles podrían notar molestias."
                }
            elif 101 <= aqi <= 150:  # nivel “intermedio superior” (más riesgo para sensibles)
                return {
                    "asma": "Aire intermedio-riesgoso: evita estar mucho tiempo fuera, lleva tu medicación.",
                    "EPOC": "Precaución elevada: reduce la exposición al aire exterior intenso.",
                    "saludable": "Actividad moderada permitida, pero no prolongada."
                }
            else:  # nivel “peligroso” (AQI > 150)
                return {
                    "asma": "¡Peligro! Quédate en el interior, usa máscara si sales, evita cualquier esfuerzo.",
                    "EPOC": "Condiciones peligrosas: permanece en espacios protegidos y evita exposición externa.",
                    "saludable": "Evita salir lo más posible; permanece en ambientes protectores."
                }
                
        self.df_aqi['Recomendación'] = self.df_aqi.apply(recommend, axis=1)
        return self.df_aqi[['FechaHora','AQI','Nivel_AQI','Recomendación']]

    def recommend_for_hour(self, hour_index: int):
        """
        Devuelve la recomendación para una hora específica (0-index).
        """
        if 0 <= hour_index < len(self.df_aqi):
            row = self.df_aqi.iloc[hour_index]
            return f"{row['FechaHora']}: {row['Recomendación']}"
        else:
            return "Hora fuera de rango."
