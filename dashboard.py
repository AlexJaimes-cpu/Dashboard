import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime

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
        .edit-cell {
            background-color: #F0F8FF;
            border: 1px solid #d3d3d3;
            border-radius: 4px;
        }
        .green-cell {
            background-color: #C8E6C9;
        }
        .blue-cell {
            background-color: #BBDEFB;
        }
        .grey-cell {
            background-color: #E0E0E0;
        }
    </style>
""", unsafe_allow_html=True)

# Ruta relativa al archivo Excel en la misma carpeta del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'Reporte_Corregido.xlsx')

# Leer el archivo y procesar los datos
try:
    # Cargar datos desde la hoja "Sheet1"
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

    # **Inicio del generador de órdenes**
    st.subheader("Generador de Órdenes")
    punto_seleccionado = st.selectbox("Seleccione un Punto de Venta", puntos_venta)
    dias = st.number_input("Ingrese el número de días de ventas que desea calcular", min_value=1, max_value=30, value=7)

    if punto_seleccionado:
        vendido_col = f"{punto_seleccionado} vendido"
        inventario_col = f"{punto_seleccionado} inventario"

        if vendido_col in datos.columns and inventario_col in datos.columns:
            datos["unidades_diarias"] = datos[vendido_col] / 30  # Unidades promedio por día
            datos["proyeccion_unidades"] = datos["unidades_diarias"] * dias
            datos["orden"] = (datos[vendido_col] - datos[inventario_col]).clip(lower=0)
            
            # Aplicar formato de colores a la columna "orden"
            def color_celda(valor):
                if valor > 0:
                    return "green-cell"
                elif valor == 0:
                    return "blue-cell"
                else:
                    return "grey-cell"

            # Mostrar tabla interactiva con filtros acumulativos
            categorias = datos["categoria"].dropna().unique().tolist()
            marcas = datos["marca"].dropna().unique().tolist()

            filtro_categoria = st.sidebar.multiselect("Filtrar por Categoría", categorias, key="filtro_categoria")
            filtro_marca = st.sidebar.multiselect("Filtrar por Marca", marcas, key="filtro_marca")

            datos_filtrados = datos.copy()
            if filtro_categoria:
                datos_filtrados = datos_filtrados[datos_filtrados["categoria"].isin(filtro_categoria)]
            if filtro_marca:
                datos_filtrados = datos_filtrados[datos_filtrados["marca"].isin(filtro_marca)]

            # Mostrar tabla editable
            st.markdown("### Tabla de Generador de Órdenes")
            edited_table = datos_filtrados[["nombre", inventario_col, "orden"]]
            edited_table = edited_table.rename(columns={inventario_col: "Inventario"})
            edited_table["Orden"] = edited_table["orden"]

            st.dataframe(edited_table)

            # Exportar a PDF
            if st.button("Exportar a PDF"):
                pdf_name = f"{punto_seleccionado}_ordenes_{datetime.date.today()}.pdf"
                with PdfPages(pdf_name) as pdf:
                    for index, row in edited_table.iterrows():
                        pdf.savefig(row.to_dict())
                st.success(f"PDF Exportado como: {pdf_name}")

except Exception as e:
    st.error(f"Error al procesar el archivo: {e}")
