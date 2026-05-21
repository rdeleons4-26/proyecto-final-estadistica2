import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chi2

# Configuración de diseño de la página
st.set_page_config(page_title="App Chi-Cuadrada Avanzada", layout="centered")

st.title("📊 App de Prueba de Hipótesis: Chi-cuadrada ($\chi^2$)")
st.write("Calculadora universal basada en frecuencias observadas ($f_o$) y esperadas ($f_e$).")

# --- SELECCIÓN DEL TAMAÑO DE LA TABLA ---
st.subheader("🛠️ Configuración del Cuadro de Contingencia")

col_dim1, col_dim2 = st.columns(2)
with col_dim1:
    filas = st.number_input("Número de Filas (Categorías de Variable 1)", min_value=2, max_value=10, value=2, step=1)
with col_dim2:
    columnas = st.number_input("Número de Columnas (Categorías de Variable 2)", min_value=2, max_value=10, value=2, step=1)

# Selector dinámico para el Nivel de Significancia (el 0.05 de tu cuaderno)
alfa = st.slider("Selecciona el Nivel de Significancia ($\\alpha$)", min_value=0.01, max_value=0.10, value=0.05, step=0.01)

# --- ENTRADA DE DATOS DINÁMICA ---
st.subheader("1. Ingresa las Frecuencias Observadas ($f_o$)")
st.write("Escribe los valores de tu tabla en las casillas de abajo:")

# Crear una matriz de entradas numéricas dinámicas
datos_fo = []
for i in range(int(filas)):
    fila_inputs = st.columns(int(columnas))
    valores_fila = []
    for j in range(int(columnas)):
        # Valores por defecto para que no aparezca vacía (ejemplo 2x2 de clase)
        val_defecto = 0
        if filas == 2 and columnas == 2:
            matriz_defecto = [[36, 52], [26, 86]]
            val_defecto = matriz_defecto[i][j]
        elif filas == 2 and columnas == 3:
            # Ejemplo 2 del cuaderno (3 años, 4 años, 5 años)
            matriz_defecto = [[20, 19, 15], [10, 16, 35]]
            val_defecto = matriz_defecto[i][j]
            
        val = fila_inputs[j].number_input(f"Fila {i+1}, Col {j+1}", value=val_defecto, key=f"fo_{i}_{j}")
        valores_fila.append(val)
    datos_fo.append(valores_fila)

# Convertir a matriz de Numpy
fo = np.array(datos_fo)

# Validar que los datos no sean todos ceros para evitar errores matemáticos
if fo.sum() == 0:
    st.warning("⚠️ Por favor introduce valores mayores a cero en la tabla para realizar los cálculos.")
else:
    # --- PROCESAM
