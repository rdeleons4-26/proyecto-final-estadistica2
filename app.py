import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chi2

# Configuración del diseño de la página con el título de pestaña limpio
st.set_page_config(page_title="Prueba de Hipótesis Chi-cuadrada", layout="centered")

# Inyección de CSS para estilo de alta gama inspirado en la paleta de la imagen
st.markdown("""
    <style>
    /* Fondo blanco puro */
    .main {
        background-color: #ffffff;
    }
    
    /* Título centrado con tipografía elegante tipo Serif y tamaño más grande */
    .titulo-centrado {
        color: #6c1d45;
        font-family: 'Georgia', 'Times New Roman', serif;
        font-weight: normal;
        text-align: center;
        font-size: 2.8rem; /* Letra más grande para el título principal */
        margin-top: 25px;
        margin-bottom: 25px;
        line-height: 1.2;
    }
    
    /* Estilos para encabezados de secciones */
    h3 {
        color: #6c1d45;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 500;
    }
    
    /* Tarjetas de resultados métricos limpias */
    .stMetric {
        background-color: #ffffff;
        padding: 12px;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #f2ebef;
    }
    </style>
    """, unsafe_allow_html=True)

# Título maquetado con HTML puro (usando el código correcto para mostrar el símbolo de Chi-cuadrada)
st.markdown('<div class="titulo-centrado">Aplicación: Prueba de Hipótesis Chi-cuadrada (&chi;&sup2;)</div>', unsafe_allow_html=True)
st.write("Calculadora universal basada en frecuencias observadas ($f_o$) y esperadas ($f_e$).")

# --- SELECCIÓN DEL TAMAÑO DE LA TABLA ---
st.subheader("Configuración del Cuadro de Contingencia")

col_dim1, col_dim2 = st.columns(2)
with col_dim1:
    filas = st.number_input("Número de Filas", min_value=2, max_value=10, value=2, step=1)
with col_dim2:
    columnas = st.number_input("Número de Columnas", min_value=2, max_value=10, value=2, step=1)

# Selector dinámico para el Nivel de Significancia
alfa = st.slider("Selecciona el Nivel de Significancia ($\\alpha$)", min_value=0.01, max_value=0.10, value=0.05, step=0.01)

# --- ENTRADA DE DATOS DINÁMICA ---
st.subheader("1. Ingrese las Frecuencias Observadas ($f_o$)")
st.write("Escribe los valores de tu tabla en las casillas de abajo:")

# Crear una matriz de entradas numéricas dinámicas
datos_fo = []
for i in range(int(filas)):
    fila_inputs = st.columns(int(columnas))
    valores_fila = []
    for j in range(int(columnas)):
        val_defecto = 1  
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
if fo.sum() <= 0:
    st.warning("Por favor introduce valores mayores a cero en la tabla para realizar los cálculos.")
else:
    totales_filas = fo.sum(axis=1)
    totales_columnas = fo.sum(axis=0)
    n = fo.sum()

    if np.any(totales_filas == 0) or np.any(totales_columnas == 0):
        st.error("Error: No puedes tener una fila o columna completa con valores en cero.")
    else:
        # 1. Calcular frecuencias esperadas
        fe = np.outer(totales_filas, totales_columnas) / n

        # 2. Aplicar la fórmula universal evitando divisiones por cero
        with np.errstate(divide='ignore', invalid='ignore'):
            numerador = (fo - fe) ** 2
            fe_segura = np.where(fe == 0, 1, fe)
            division_chi = numerador / fe_segura
            division_chi = np.where(fe == 0, 0, division_chi)
            chi2_calculado = np.sum(division_chi)

        # 3. Grados de libertad
        gl = (int(columnas) - 1) * (int(filas) - 1)

        # 4. Búsqueda del Valor Crítico
        valor_critico = chi2.ppf(1 - alfa, gl)

        # --- MOSTRAR RESULTADOS ---
        st.subheader("2. Resultados del Análisis Estadístico")

        c1, c2, c3 = st.columns(3)
        c1.metric("$\chi^2$ Calculado", f"{chi2_calculado:.2f}")
        c2.metric("Valor Crítico (Tabla)", f"{valor_critico:.2f}")
        c3.metric("Grados de Libertad ($gl$)", f"{gl}")

        # Conclusión automática sin emojis
        st.subheader("3. Conclusión de la Hipótesis")
        if chi2_calculado > valor_critico:
            st.error(f"Se rechaza la Hipótesis Nula ($H_0$). El valor calculado ({chi2_calculado:.2f}) es MAYOR que el valor crítico de la tabla ({valor_critico:.2f}). Las variables NO son independientes.")
        else:
            st.success(f"No se rechaza la Hipótesis Nula ($H_0$). El valor calculado ({chi2_calculado:.2f}) es MENOR o IGUAL que el valor crítico de la tabla ({valor_critico:.2f}). Las variables son independientes.")

        # --- GRÁFICA DE LA DISTRIBUCIÓN ---
        st.subheader("Visualización Gráfica")
        limite_x = float(max(valor_critico + 5, chi2_calculado + 5, 15))
        x = np.linspace(0, limite_x, 1000)
        y = chi2.pdf(x, gl)

        # Diseño limpio de la gráfica
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#ffffff')
        ax.set_facecolor('#ffffff')
        
        # Curva en el tono ciruela/vino de la marca
        ax.plot(x, y, color='#6c1d45', lw=2.5, label=f'Curva de Distribución $\chi^2$ (gl = {gl})')

        # Región de rechazo con el rosa empolvado suave del fondo de la imagen
        x_rechazo = np.linspace(valor_critico, limite_x, 100)
        ax.fill_between(x_rechazo, chi2.pdf(x_rechazo, gl), color='#ebd5dd', alpha=0.8, label=f'Región de Rechazo ($\\alpha$ = {alfa})')

        # Tu Chi calculado en una línea discontinua color gris elegante
        ax.axvline(chi2_calculado, color='#555555', linestyle='--', lw=2, label=f'Tu $\chi^2$ Calculado = {chi2_calculado:.2f}')

        ax.set_title("Ubicación del Estadístico y Región de Rechazo", fontsize=12, color='#6c1d45', family='serif')
        ax.set_xlabel("Valor de $\chi^2$")
        ax.set_ylabel("Densidad de Probabilidad")
        ax.legend(facecolor='white', frameon=True)
        
        # Remover bordes superior y derecho para un minimalismo total
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')

        st.pyplot(fig)
