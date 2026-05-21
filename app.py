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
    filas = st.number_input("Número de Filas", min_value=2, max_value=10, value=2, step=1)
with col_dim2:
    columnas = st.number_input("Número de Columnas", min_value=2, max_value=10, value=2, step=1)

# Selector dinámico para el Nivel de Significancia
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
        # Valores por defecto automáticos según el tamaño elegido
        val_defecto = 1  # Ponemos 1 por defecto para evitar ceros problemáticos
        if filas == 2 and columnas == 2:
            matriz_defecto = [[36, 52], [26, 86]]
            val_defecto = matriz_defecto[i][j]
        elif filas == 2 and columnas == 3:
            matriz_defecto = [[20, 19, 15], [10, 16, 35]]
            val_defecto = matriz_defecto[i][j]
            
        val = fila_inputs[j].number_input(f"Fila {i+1}, Col {j+1}", value=int(val_defecto), min_value=0, key=f"fo_{i}_{j}")
        valores_fila.append(val)
    datos_fo.append(valores_fila)

# Convertir a matriz de Numpy
fo = np.array(datos_fo)

# --- PROCESAMIENTO MATEMÁTICO SEGURO ---
# Verificamos que la suma total sea mayor a cero y que no haya filas/columnas vacías
if fo.sum() <= 0:
    st.warning("⚠️ Por favor introduce valores mayores a cero en la tabla para realizar los cálculos.")
else:
    totales_filas = fo.sum(axis=1)
    totales_columnas = fo.sum(axis=0)
    n = fo.sum()

    # Validar que ningún total de fila o columna sea cero para evitar divisiones inválidas
    if np.any(totales_filas == 0) or np.any(totales_columnas == 0):
        st.error("❌ Error: No puedes tener una fila o columna completa con valores en cero.")
    else:
        # 1. Calcular frecuencias esperadas
        fe = np.outer(totales_filas, totales_columnas) / n

        # 2. Aplicar la fórmula universal evitando divisiones por cero
        with np.errstate(divide='ignore', invalid='ignore'):
            numerador = (fo - fe) ** 2
            # Evitamos dividir si fe tiene algún cero (reemplazando temporalmente por 1)
            fe_segura = np.where(fe == 0, 1, fe)
            division_chi = numerador / fe_segura
            # Si fe era cero, el resultado debe ser cero
            division_chi = np.where(fe == 0, 0, division_chi)
            chi2_calculado = np.sum(division_chi)

        # 3. Grados de libertad
        gl = (int(columnas) - 1) * (int(filas) - 1)

        # 4. Búsqueda del Valor Crítico
        valor_critico = chi2.ppf(1 - alfa, gl)

        # --- MOSTRAR RESULTADOS ---
        st.subheader("2. Resultados del Análisis Estadístico")

        c1, c2, c3 = st.columns(3)
        c1.metric("$\\chi^2$ Calculado", f"{chi2_calculado:.2f}")
        c2.metric("Valor Crítico (Tabla)", f"{valor_critico:.2f}")
        c3.metric("Grados de Libertad ($gl$)", f"{gl}")

        # Conclusión automática
        st.subheader("3. Conclusión de la Hipótesis")
        if chi2_calculado > valor_critico:
            st.error(f"❌ **Se rechaza la Hipótesis Nula ($H_0$).** El valor calculado ({chi2_calculado:.2f}) es MAYOR que el valor crítico de la tabla ({valor_critico:.2f}). Las variables NO son independientes.")
        else:
            st.success(f"✅ **No se rechaza la Hipótesis Nula ($H_0$).** El valor calculado ({chi2_calculado:.2f}) es MENOR o IGUAL que el valor crítico de la tabla ({valor_critico:.2f}). Las variables son independientes.")

        # --- GRÁFICA DE LA DISTRIBUCIÓN ---
        st.subheader("4. Visualización Gráfica")
        limite_x = float(max(valor_critico + 5, chi2_calculado + 5, 15))
        x = np.linspace(0, limite_x, 1000)
        y = chi2.pdf(x, gl)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(x, y, color='purple', lw=2, label=f'Curva de Distribución $\chi^2$ (gl = {gl})')

        x_rechazo = np.linspace(valor_critico, limite_x, 100)
        ax.fill_between(x_rechazo, chi2.pdf(x_rechazo, gl), color='red', alpha=0.3, label=f'Región de Rechazo ($\\alpha$ = {alfa})')

        ax.axvline(chi2_calculado, color='blue', linestyle='--', lw=2, label=f'Tu $\chi^2$ Calculado = {chi2_calculado:.2f}')

        ax.set_title("Ubicación del Estadístico y Región de Rechazo", fontsize=14)
        ax.set_xlabel("Valor de $\chi^2$")
        ax.set_ylabel("Densidad de Probabilidad")
        ax.legend()
        ax.grid(True, alpha=0.2)

        st.pyplot(fig)
