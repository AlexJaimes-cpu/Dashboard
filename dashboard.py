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

    # Convertir columnas relevantes a formato numérico
    columnas_numericas = [
        "total neto", "costo", "ganancia", "%", 
        "market samaria vendido", "market playa dormida vendido", "market two towers vendido",
        "market samaria inventario", "market playa dormida inventario", "market two towers inventario"
    ]
    for col in columnas_numericas:
        if col in datos.columns:
            datos[col] = pd.to_numeric(datos[col], errors="coerce")

    # Asignar nombres clave a las columnas
    puntos_venta = ["market samaria", "market playa dormida", "market two towers"]

    # Calcular totales generales
    total_ventas = datos["total neto"].sum()
    total_costo = datos["costo"].sum()
    total_ganancia = total_ventas - total_costo
    porcentaje_ganancia = (total_ganancia / total_ventas) * 100 if total_ventas != 0 else 0

    # Mostrar resultados generales
    st.title("Dashboard de Ventas")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
            <div class="custom-box">
                <h3>Total Ventas</h3>
                <p>${total_ventas:,.2f}</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="custom-box">
                <h3>Totales de Ganancia</h3>
                <p>Total Costo: ${total_costo:,.2f}</p>
                <p>Total Ganancia: ${total_ganancia:,.2f}</p>
                <p>Porcentaje Ganancia: {porcentaje_ganancia:.2f}%</p>
            </div>
        """, unsafe_allow_html=True)

    # Totales por punto de venta (cálculo corregido)
    st.subheader("Totales por Punto de Venta")
    cols = st.columns(len(puntos_venta))  # Crear columnas para mostrar los totales de cada punto de venta

    suma_puntos_venta = 0
    for i, punto in enumerate(puntos_venta):
        vendido_col = f"{punto} vendido"
        if vendido_col in datos.columns:
            total_venta_punto = datos[vendido_col].sum()  # Sumar correctamente las ventas por punto de venta
            suma_puntos_venta += total_venta_punto

            total_costo_punto = total_venta_punto * (total_costo / total_ventas) if total_ventas > 0 else 0
            ganancia_punto = total_venta_punto - total_costo_punto
            margen_punto = (ganancia_punto / total_venta_punto) * 100 if total_venta_punto > 0 else 0

            with cols[i]:
                st.markdown(f"""
                    <div class="custom-box">
                        <h3>{punto.title()}</h3>
                        <p>Total Ventas: ${total_venta_punto:,.2f}</p>
                        <p>Total Costo: ${total_costo_punto:,.2f}</p>
                        <p>Ganancia: ${ganancia_punto:,.2f}</p>
                        <p>Margen: {margen_punto:.2f}%</p>
                    </div>
                """, unsafe_allow_html=True)

    # Verificar si las ventas totales por punto de venta coinciden con el total neto
    if abs(suma_puntos_venta - total_ventas) > 1e-2:  # Permitir un margen mínimo de error
        st.error(f"ERROR: Las ventas totales por punto de venta (${suma_puntos_venta:,.2f}) no coinciden con el total neto (${total_ventas:,.2f}).")

except Exception as e:
    # Manejo de errores
    st.error(f"Error al procesar el archivo: {e}")
