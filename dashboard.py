import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Configuración básica de Streamlit
st.set_page_config(
    page_title="Dashboard de Ventas",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos personalizados
st.markdown("""
    <style>
        .main {
            background-color: #f9f9f9;
        }
        .block-container {
            padding: 2rem 1rem;
        }
        h1, h2, h3 {
            color: #0056a6;
            font-size: 18pt;
        }
        .custom-box {
            border: 1.5px solid #0056a6;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            background-color: #ffffff;
            text-align: center;
        }
        .custom-box h3 {
            font-size: 16pt;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .custom-box p {
            font-size: 18pt;
            color: #0056a6;
            margin: 0;
        }
    </style>
""", unsafe_allow_html=True)

# Ruta relativa al archivo Excel en la misma carpeta del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'Reporte_Corregido.xlsx')

try:
    # Leer el archivo y procesar los datos
    datos = pd.read_excel(file_path, sheet_name="Sheet1")

    # Normalizar los nombres de las columnas
    datos.columns = datos.columns.str.strip().str.lower()

    # Variables globales
    total_ventas_generales = 249316096  # Total en dinero
    total_unidades_vendidas = datos["total vendido"].sum() if "total vendido" in datos.columns else 0
    costo_total = datos["costo"].sum() if "costo" in datos.columns else 0
    ganancia_total = total_ventas_generales - costo_total

    # Cálculo por unidad
    valor_por_unidad = total_ventas_generales / total_unidades_vendidas if total_unidades_vendidas > 0 else 0
    costo_por_unidad = costo_total / total_unidades_vendidas if total_unidades_vendidas > 0 else 0
    ganancia_por_unidad = ganancia_total / total_unidades_vendidas if total_unidades_vendidas > 0 else 0

    # Cálculos por punto de venta
    puntos_venta = ["market samaria", "market playa dormida", "market two towers"]
    for punto in puntos_venta:
        vendido_col = f"{punto} vendido"
        if vendido_col in datos.columns:
            datos[f"{punto}_ventas_calculadas"] = datos[vendido_col] * valor_por_unidad
            datos[f"{punto}_costo_calculado"] = datos[vendido_col] * costo_por_unidad
            datos[f"{punto}_ganancia_calculada"] = datos[vendido_col] * ganancia_por_unidad

    # Resumen por punto de venta
    totales_recalculados = {
        punto: {
            'Ventas Recalculadas': datos[f"{punto}_ventas_calculadas"].sum(),
            'Costo Recalculado': datos[f"{punto}_costo_calculado"].sum(),
            'Ganancia Recalculada': datos[f"{punto}_ganancia_calculada"].sum()
        }
        for punto in puntos_venta
        if f"{punto}_ventas_calculadas" in datos.columns
    }

    # Mostrar resultados generales
    st.title("Dashboard de Ventas")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
            <div class="custom-box">
                <h3>Total Ventas</h3>
                <p>${total_ventas_generales:,.2f}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="custom-box">
                <h3>Totales de Ganancia</h3>
                <p>Total Costo: ${costo_total:,.2f}</p>
                <p>Total Ganancia: ${ganancia_total:,.2f}</p>
                <p>Porcentaje Ganancia: {(ganancia_total / total_ventas_generales) * 100:.2f}%</p>
            </div>
        """, unsafe_allow_html=True)

    # Mostrar totales por punto de venta
    st.subheader("Totales por Punto de Venta")
    cols = st.columns(len(puntos_venta))
    for i, punto in enumerate(puntos_venta):
        with cols[i]:
            ventas = totales_recalculados[punto]['Ventas Recalculadas']
            costo = totales_recalculados[punto]['Costo Recalculado']
            ganancia = totales_recalculados[punto]['Ganancia Recalculada']
            st.markdown(f"""
                <div class="custom-box">
                    <h3>{punto.title()}</h3>
                    <p>Ventas: ${ventas:,.2f}</p>
                    <p>Costo: ${costo:,.2f}</p>
                    <p>Ganancia: ${ganancia:,.2f}</p>
                </div>
            """, unsafe_allow_html=True)

    # Gráficos
    st.subheader("Gráficos de Productos Más Vendidos")
    productos_mas_vendidos = datos.groupby("nombre")["total vendido"].sum().nlargest(5)

    st.markdown("#### Top 5 Productos Más Vendidos")
    fig, ax = plt.subplots()
    productos_mas_vendidos.plot(kind="bar", ax=ax)
    ax.set_ylabel("Unidades Vendidas")
    ax.set_title("Top 5 Productos Más Vendidos")
    st.pyplot(fig)

except Exception as e:
    st.error(f"Error al procesar el archivo: {e}")
