import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

class AirQualityNARX:
    """
    Combina regresión lineal y NARX para predicción de AQI.
    """

    def __init__(self, df_aqi):
        self.df = df_aqi.copy()
        self.linear_model = None
        self.narx_model = None
        self.lags = 3  # número de rezagos

    # ---------------------------
    # Crear variables rezagadas
    # ---------------------------
    def create_lags(self):
        df_lagged = self.df.copy()
        for col in ['PM25','O3','NO2','AQI']:
            for lag in range(1, self.lags+1):
                df_lagged[f'{col}_t-{lag}'] = df_lagged[col].shift(lag)
        df_lagged = df_lagged.dropna().reset_index(drop=True)
        self.df_lagged = df_lagged

    # ---------------------------
    # Entrenar regresión lineal
    # ---------------------------
    def train_linear(self):
        self.create_lags()
        X_cols = [f'{c}_t-{lag}' for c in ['PM25','O3','NO2'] for lag in range(1,self.lags+1)]
        y = self.df_lagged['AQI']
        X = self.df_lagged[X_cols]
        self.linear_model = LinearRegression()
        self.linear_model.fit(X, y)
        r2 = self.linear_model.score(X, y)
        return r2

    # ---------------------------
    # Predecir con regresión lineal
    # ---------------------------
    def predict_linear(self, steps=6):
        """
        steps: número de horas futuras a predecir
        """
        X_cols = [f'{c}_t-{lag}' for c in ['PM25','O3','NO2'] for lag in range(1,self.lags+1)]
        last_values = self.df_lagged[X_cols].iloc[-1].values.reshape(1,-1)
        preds = []

        for i in range(steps):
            y_pred = self.linear_model.predict(last_values)[0]
            preds.append(y_pred)

            # Actualizar last_values: desplazar valores y agregar predicción
            last_values = np.roll(last_values, -3)  # desplaza los valores de PM25,O3,NO2
            last_values[0,-3:] = [y_pred]*3  # placeholder para AQI futuro (se puede mejorar)

        return preds

    # ---------------------------
    # NARX simple usando rezagos de AQI
    # ---------------------------
    def train_narx(self):
        """
        Modelo NARX simple: predice AQI_t usando AQI_t-1, AQI_t-2, AQI_t-3
        """
        y = self.df_lagged['AQI']
        X = self.df_lagged[[f'AQI_t-{lag}' for lag in range(1,self.lags+1)]]
        self.narx_model = LinearRegression()
        self.narx_model.fit(X, y)
        r2 = self.narx_model.score(X, y)
        return r2

    def predict_narx(self, steps=6):
        last_vals = self.df_lagged[[f'AQI_t-{lag}' for lag in range(1,self.lags+1)]].iloc[-1].values.reshape(1,-1)
        preds = []
        for i in range(steps):
            y_pred = self.narx_model.predict(last_vals)[0]
            preds.append(y_pred)
            last_vals = np.roll(last_vals, -1)
            last_vals[0,-1] = y_pred
        return preds
