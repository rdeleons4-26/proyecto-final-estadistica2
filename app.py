import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chi2

# Configuración de diseño de la página
st.set_page_config(page_title="App Chi-Cuadrada", layout="centered")

st.title("📊 App de Prueba de Hipótesis: Chi-cuadrada ($\chi^2$)")
st.write("Calculadora automatizada basada en frecuencias observadas ($f_o$) y esperadas ($f_e$).")

st.info("💡 Los datos precargados corresponden al ejemplo de clase (Masculino/Femenino). ¡Puedes cambiarlos por los de cualquier otro problema!")

# --- ENTRADA DE DATOS (Frecuencias Observadas) ---
st.subheader("1. Ingresa las Frecuencias Observadas ($f_o$)")

col1, col2 = st.columns(2)
with col1:
    fo_11 = st.number_input("Fila 1, Columna 1 (ej. Masculino - Técnicas)", value=36)
    fo_21 = st.number_input("Fila 2, Columna 1 (ej. Femenino - Técnicas)", value=26)
with col2:
    fo_12 = st.number_input("Fila 1, Columna 2 (ej. Masculino - Humanística)", value=52)
    fo_22 = st.number_input("Fila 2, Columna 2 (ej. Femenino - Humanística)", value=86)

# Selector dinámico para el Nivel de Significancia (el 0.05 de tu cuaderno)
alfa = st.slider("Selecciona el Nivel de Significancia ($\\alpha$)", min_value=0.01, max_value=0.10, value=0.05, step=0.01)

# Construcción de la matriz con los datos del usuario
fo = np.array([[fo_11, fo_12], [fo_21, fo_22]])

# --- PROCESAMIENTO MATEMÁTICO (La fórmula de tu cuaderno) ---
totales_filas = fo.sum(axis=1)
totales_columnas = fo.sum(axis=0)
n = fo.sum()

# 1. Calcular frecuencias esperadas: fe = (total fila * total columna) / n
fe = np.outer(totales_filas, totales_columnas) / n

# 2. Aplicar tu fórmula universal: Σ [ (fo - fe)^2 / fe ]
chi2_calculado = np.sum((fo - fe)**2 / fe)

# 3. Grados de libertad: gl = (C-1)*(F-1)
filas, columnas = fo.shape
gl = (columnas - 1) * (filas - 1)

# 4. Búsqueda automática del Valor Crítico en la tabla interna de Python
valor_critico = chi2.ppf(1 - alfa, gl)

# --- MOSTRAR RESULTADOS Y CONCLUSIÓN ---
st.subheader("2. Resultados del Análisis Estadístico")

c1, c2, c3 = st.columns(3)
c1.metric("$\\chi^2$ Calculado", f"{chi2_calculado:.2f}")
c2.metric("Valor Crítico (Tabla)", f"{valor_critico:.2f}")
c3.metric("Grados de Libertad ($gl$)", f"{gl}")

# Criterio de decisión automático
st.subheader("3. Conclusión de la Hipótesis")
if chi2_calculado > valor_critico:
    st.error(f"❌ **Se rechaza la Hipótesis Nula ($H_0$).** El valor calculado ({chi2_calculado:.2f}) es MAYOR que el valor crítico de la tabla ({valor_critico:.2f}). Las variables NO son independientes; existe una relación significativa entre ellas.")
else:
    st.success(f"✅ **No se rechaza la Hipótesis Nula ($H_0$).** El valor calculado ({chi2_calculado:.2f}) es MENOR o IGUAL que el valor crítico de la tabla ({valor_critico:.2f}). Las variables son independientes.")

# --- GRÁFICA DE LA DISTRIBUCIÓN ---
st.subheader("4. Visualización Gráfica")
x = np.linspace(0, valor_critico + 5, 1000)
y = chi2.pdf(x, gl)

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(x, y, color='purple', lw=2, label=f'Curva de Distribución $\chi^2$ (gl = {gl})')

# Sombreado de la región de rechazo basada en el alfa
x_rechazo = np.linspace(valor_critico, valor_critico + 5, 100)
ax.fill_between(x_rechazo, chi2.pdf(x_rechazo, gl), color='red', alpha=0.3, label=f'Región de Rechazo ($\\alpha$ = {alfa})')

# Línea guía que muestra dónde cayó nuestro cálculo
ax.axvline(chi2_calculado, color='blue', linestyle='--', lw=2, label=f'Tu $\chi^2$ Calculado = {chi2_calculado:.2f}')

ax.set_title("Ubicación del Estadístico y Región de Rechazo", fontsize=14)
ax.set_xlabel("Valor de $\chi^2$")
ax.set_ylabel("Densidad de Probabilidad")
ax.legend()
ax.grid(True, alpha=0.2)

st.pyplot(fig)
