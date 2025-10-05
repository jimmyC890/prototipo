import pandas as pd

class AirQualityForecast:
    """
    Capa de forecasting para calcular AQI por hora
    a partir de NO2, O3 y PM2.5 de SINAICA.
    """

    def __init__(self, df_no2, df_o3, df_pm25):
        self.df_no2 = df_no2.copy()
        self.df_o3 = df_o3.copy()
        self.df_pm25 = df_pm25.copy()
        self.df_all = None

    # ---------------------------------------
    # Función para calcular AQI individual
    # ---------------------------------------
    @staticmethod
    def calc_aqi(conc, pollutant):
        breakpoints = []
        if pollutant=='PM25':
            breakpoints = [(0,12,0,50),(12.1,35.4,51,100),(35.5,55.4,101,150),
                           (55.5,150.4,151,200),(150.5,250.4,201,300),(250.5,350.4,301,400),(350.5,500,401,500)]
        elif pollutant=='O3':
            breakpoints = [(0,54,0,50),(55,70,51,100),(71,85,101,150),(86,105,151,200),(106,200,201,300)]
        elif pollutant=='NO2':
            breakpoints = [(0,53,0,50),(54,100,51,100),(101,360,101,150),(361,649,151,200),(650,1249,201,300)]
        for C_low,C_high,I_low,I_high in breakpoints:
            if C_low <= conc <= C_high:
                return ((I_high-I_low)/(C_high-C_low))*(conc-C_low)+I_low
        return None

    # ---------------------------------------
    # Unir datasets y convertir unidades
    # ---------------------------------------
    def prepare_data(self):
        # Eliminar filas vacías
        self.df_no2 = self.df_no2.dropna(subset=['Valor'])
        self.df_o3  = self.df_o3.dropna(subset=['Valor'])
        self.df_pm25= self.df_pm25.dropna(subset=['Valor'])

        # Convertir NO2 y O3 de ppm a ppb
        self.df_no2['Valor'] = self.df_no2['Valor'] * 1000
        self.df_o3['Valor']  = self.df_o3['Valor'] * 1000

        # Renombrar columnas
        self.df_no2.rename(columns={'Valor':'NO2'}, inplace=True)
        self.df_o3.rename(columns={'Valor':'O3'}, inplace=True)
        self.df_pm25.rename(columns={'Valor':'PM25'}, inplace=True)

        # Crear columna FechaHora para unir
        for df in [self.df_no2, self.df_o3, self.df_pm25]:
            df['FechaHora'] = df['Fecha'].astype(str) + " " + df['Hora']

        # Unir datasets
        self.df_all = self.df_no2[['FechaHora','NO2']].merge(
            self.df_o3[['FechaHora','O3']], on='FechaHora', how='outer'
        ).merge(
            self.df_pm25[['FechaHora','PM25']], on='FechaHora', how='outer'
        )

        self.df_all = self.df_all.sort_values('FechaHora').reset_index(drop=True)

    # ---------------------------------------
    # Calcular AQI
    # ---------------------------------------
    def calculate_aqi(self):
        if self.df_all is None:
            self.prepare_data()

        self.df_all['AQI_PM25'] = self.df_all['PM25'].apply(lambda x: self.calc_aqi(x,'PM25'))
        self.df_all['AQI_O3'] = self.df_all['O3'].apply(lambda x: self.calc_aqi(x,'O3'))
        self.df_all['AQI_NO2'] = self.df_all['NO2'].apply(lambda x: self.calc_aqi(x,'NO2'))

        # AQI final por hora
        self.df_all['AQI'] = self.df_all[['AQI_PM25','AQI_O3','AQI_NO2']].max(axis=1)

        # Clasificación
        def classify_aqi(aqi):
            if aqi<=50: return "Bueno"
            elif aqi<=100: return "Moderado"
            elif aqi<=150: return "Insalubre para grupos sensibles"
            elif aqi<=200: return "Insalubre"
            elif aqi<=300: return "Muy insalubre"
            else: return "Peligroso"

        self.df_all['Nivel_AQI'] = self.df_all['AQI'].apply(classify_aqi)

        return self.df_all
