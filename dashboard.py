import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
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
        .green-cell {
            background-color: #C8E6C9;
        }
        .blue-cell {
            background-color: #BBDEFB;
        }
        .grey-cell {
            background-color: #E0E0E0;
        }
        .delete-cell {
            color: red;
            font-weight: bold;
            cursor: pointer;
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

    # Calcular totales generales por punto de venta
    st.title("Dashboard de Ventas")
    st.subheader("Totales Generales por Punto de Venta")
    col1, col2, col3 = st.columns(3)

    for i, punto in enumerate(puntos_venta):
        vendido_col = f"{punto} vendido"
        if vendido_col in datos.columns:
            total_venta = datos[vendido_col].sum()
            total_costo = datos[vendido_col].sum() * (datos["costo"].sum() / datos["total neto"].sum())
            ganancia = total_venta - total_costo
            margen = (ganancia / total_venta) * 100 if total_venta > 0 else 0

            with [col1, col2, col3][i]:
                st.markdown(f"""
                <div class="custom-box">
                    <h3>{punto.title()}</h3>
                    <p>Total Ventas: ${total_venta:,.2f}</p>
                    <p>Total Costo: ${total_costo:,.2f}</p>
                    <p>Ganancia: ${ganancia:,.2f}</p>
                    <p>Margen: {margen:.2f}%</p>
                </div>
                """, unsafe_allow_html=True)

    # Gráficas de pastel
    st.subheader("Gráficas de Productos Más Vendidos")
    col1, col2 = st.columns(2)
    productos_mas_vendidos = datos.groupby("nombre")["total neto"].sum().nlargest(5)

    with col1:
        st.markdown("### Top 5 Productos Más Vendidos (Totales)")
        fig, ax = plt.subplots()
        productos_mas_vendidos.plot(kind="pie", autopct='%1.1f%%', ax=ax, startangle=90, legend=False)
        ax.set_ylabel("")
        st.pyplot(fig)

    with col2:
        for punto in puntos_venta:
            top_punto = datos.groupby("nombre")[f"{punto} vendido"].sum().nlargest(5)
            st.markdown(f"### Top 5 en {punto.title()}")
            fig, ax = plt.subplots()
            top_punto.plot(kind="pie", autopct='%1.1f%%', ax=ax, startangle=90, legend=False)
            ax.set_ylabel("")
            st.pyplot(fig)

    # Generador de Órdenes
    st.subheader("Generador de Órdenes")
    punto_seleccionado = st.selectbox("Seleccione un Punto de Venta", puntos_venta)
    dias = st.number_input("Ingrese el número de días de ventas", min_value=1, max_value=30, value=7)

    if punto_seleccionado:
        vendido_col = f"{punto_seleccionado} vendido"
        inventario_col = f"{punto_seleccionado} inventario"
        datos["orden"] = (datos[vendido_col] - datos[inventario_col]).clip(lower=0)

        # Crear tabla editable
        datos["Inventario"] = datos[inventario_col]
        tabla = datos[["nombre", inventario_col, vendido_col, "orden"]]
        tabla.rename(columns={inventario_col: "Inventario", vendido_col: "Vendido", "orden": "Orden"}, inplace=True)

        st.markdown("### Tabla de Órdenes (Editable)")
        edited_table = st.experimental_data_editor(tabla, use_container_width=True)

        # Botón para exportar a PDF
        if st.button("Exportar a PDF"):
            pdf_buffer = BytesIO()
            with PdfPages(pdf_buffer) as pdf:
                for index, row in edited_table.iterrows():
                    fig, ax = plt.subplots()
                    ax.text(0.5, 0.5, f"{row['nombre']}: {row['Orden']}", fontsize=12, ha='center')
                    pdf.savefig(fig)
                    plt.close(fig)
            st.download_button(
                "Descargar PDF",
                data=pdf_buffer.getvalue(),
                file_name=f"Ordenes_{punto_seleccionado}_{datetime.date.today()}.pdf",
                mime="application/pdf"
            )

except Exception as e:
    st.error(f"Error al procesar el archivo: {e}")
