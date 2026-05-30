import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chi2

st.set_page_config(page_title="Prueba de Hipótesis Chi-cuadrada", layout="centered")

st.markdown("""
    <style>
    /* Importar tipografía*/
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap');

    /* Fondo */
    .main {
        background-color: #ffffff;
    }
    
    /* Título principal*/
    .titulo-premium {
        color: #6c1d45;
        font-family: 'Playfair Display', 'Didot', 'Georgia', serif;
        font-weight: 400;
        text-align: center;
        font-size: 2.8rem;
        margin-top: 30px;
        margin-bottom: 25px;
        line-height: 1.2;
    }

    /* Subtítulos*/
    .subtitulo-centrado {
        color: #6c1d45;
        font-family: 'Playfair Display', 'Didot', 'Georgia', serif;
        text-align: center;
        font-size: 1.8rem;
        margin-top: 35px;
        margin-bottom: 20px;
    }
    
    /* Estilos para encabezados */
    h3 {
        color: #6c1d45;
        font-family: 'Helvetica Neue', Helvetica, Times New Roman, sans-serif;
        font-weight: 500;
    }
    
    .stMetric {
        background-color: #ffffff;
        padding: 12px;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #f2ebef;
    }
    </style>
    """, unsafe_allow_html=True)

# Título
st.markdown('<div class="titulo-premium">Prueba de Hipótesis con Chi-cuadrada (&chi;&sup2;)</div>', unsafe_allow_html=True)
st.write("Calculadora universal basada en frecuencias observadas ($f_o$) y esperadas ($f_e$).")

st.subheader("Configuración del Cuadro de Contingencia")

col_dim1, col_dim2 = st.columns(2)
with col_dim1:
    filas = st.number_input("Número de Filas", min_value=2, max_value=10, value=2, step=1)
with col_dim2:
    columnas = st.number_input("Número de Columnas", min_value=2, max_value=10, value=2, step=1)

# Selector dinámico para el Nivel de Significancia
alfa = st.slider("Selecciona el Nivel de Significancia ($\\alpha$)", min_value=0.01, max_value=0.10, value=0.05, step=0.01)

#Entrada de datos dinamica
st.subheader("1. Ingrese las Frecuencias Observadas ($f_o$)")
st.write("Escribe los valores de tu tabla en las casillas de abajo:")
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
    
fo = np.array(datos_fo)

if fo.sum() <= 0:
    st.warning("Por favor introduce valores mayores a cero en la tabla para realizar los cálculos.")
else:
    totales_filas = fo.sum(axis=1)
    totales_columnas = fo.sum(axis=0)
    n = fo.sum()

    if np.any(totales_filas == 0) or np.any(totales_columnas == 0):
        st.error("Error: No puedes tener una fila o columna completa con valores en cero.")
    else:
        #Calcular frecuencias esperadas
        fe = np.outer(totales_filas, totales_columnas) / n

        #Mostrar tabla de frecuencias esperadas
        st.subheader("2. Frecuencias Esperadas Calculadas ($f_e$)")
        st.write("Valores teóricos calculados automáticamente bajo el supuesto de independencia:")
        
        st.dataframe(fe, column_config={str(j): f"Col {j+1}" for j in range(int(columnas))}, use_container_width=True)

        #Aplicar la fórmula universal evitando divisiones por cero
        with np.errstate(divide='ignore', invalid='ignore'):
            numerador = (fo - fe) ** 2
            fe_segura = np.where(fe == 0, 1, fe)
            division_chi = numerador / fe_segura
            division_chi = np.where(fe == 0, 0, division_chi)
            chi2_calculado = np.sum(division_chi)

        #Grados de libertad
        gl = (int(columnas) - 1) * (int(filas) - 1)

        #Valor Crítico
        valor_critico = chi2.ppf(1 - alfa, gl)

        #Mostrar resultados
        st.subheader("3. Resultados del Análisis Estadístico")

        c1, c2, c3 = st.columns(3)
        c1.metric("$\chi^2$ Calculado", f"{chi2_calculado:.2f}")
        c2.metric("Valor Crítico (Tabla)", f"{valor_critico:.2f}")
        c3.metric("Grados de Libertad ($gl$)", f"{gl}")

        #Conclusión de la hipótesis
        st.subheader("4. Conclusión de la Hipótesis")
        if chi2_calculado > valor_critico:
            st.error(f"Se rechaza la Hipótesis Nula ($H_0$). El valor calculado ({chi2_calculado:.2f}) es MAYOR que el valor crítico de la tabla ({valor_critico:.2f}). Las variables NO son independientes.")
        else:
            st.success(f"No se rechaza la Hipótesis Nula ($H_0$). El valor calculado ({chi2_calculado:.2f}) es MENOR o IGUAL que el valor crítico de la tabla ({valor_critico:.2f}). Las variables son independientes.")

        #Grafica de la distribución
        st.markdown('<div class="subtitulo-centrado">Visualización Gráfica</div>', unsafe_allow_html=True)
        limite_x = float(max(valor_critico + 5, chi2_calculado + 5, 15))
        x = np.linspace(0, limite_x, 1000)
        y = chi2.pdf(x, gl)

        # Diseño de la gráfica
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#ffffff')
        ax.set_facecolor('#ffffff')
        
        #Curva
        ax.plot(x, y, color='#6c1d45', lw=2.5, label=f'Curva de Distribución $\chi^2$ (gl = {gl})')

        #Región de rechazo
        x_rechazo = np.linspace(valor_critico, limite_x, 100)
        ax.fill_between(x_rechazo, chi2.pdf(x_rechazo, gl), color='#ebd5dd', alpha=0.8, label=f'Región de Rechazo ($\\alpha$ = {alfa})')

        #Chi calculado
        ax.axvline(chi2_calculado, color='#555555', linestyle='--', lw=2, label=f'Tu $\chi^2$ Calculado = {chi2_calculado:.2f}')

        ax.set_xlabel("Valor de $\chi^2$")
        ax.set_ylabel("Densidad de Probabilidad")
        ax.legend(facecolor='white', frameon=True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')

        st.pyplot(fig)

        # (Aquí está el código de tu gráfica que ya funciona perfectamente...)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')

        st.pyplot(fig)

#pie de página 
st.markdown("""
    <style>
    .footer-premium {
        text-align: center;
        font-family: 'Playfair Display', 'Didot', 'Georgia', serif;
        font-size: 1.0rem;
        color: #6c1d45;
        font-style: italic;
        margin-top: 50px;
        border-top: 1px solid #f2ebef;
        padding-top: 20px;
        padding-bottom: 10px;
    }
    </style>
    <div class="footer-premium">
    Rita Shantal de León Sánchez &copy; 2026
    </div>
    """, unsafe_allow_html=True)

