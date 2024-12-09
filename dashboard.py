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

    # Filtros acumulativos
    st.sidebar.header("Filtros")
    categorias = datos["categoria"].dropna().unique().tolist() if "categoria" in datos.columns else []
    marcas = datos["marca"].dropna().unique().tolist() if "marca" in datos.columns else []
    nombres = datos["nombre"].dropna().unique().tolist() if "nombre" in datos.columns else []

    filtro_categoria = st.sidebar.multiselect("Filtrar por Categoría", categorias, key="filtro_categoria")
    filtro_marca = st.sidebar.multiselect("Filtrar por Marca", marcas, key="filtro_marca")
    filtro_nombre = st.sidebar.multiselect("Filtrar por Producto (Nombre)", nombres, key="filtro_nombre")

    datos_filtrados = datos.copy()
    if filtro_categoria:
        datos_filtrados = datos_filtrados[datos_filtrados["categoria"].isin(filtro_categoria)]
    if filtro_marca:
        datos_filtrados = datos_filtrados[datos_filtrados["marca"].isin(filtro_marca)]
    if filtro_nombre:
        datos_filtrados = datos_filtrados[datos_filtrados["nombre"].isin(filtro_nombre)]

    # Tablas interactivas por punto de venta
    st.subheader("Tablas Interactivas por Punto de Venta")
    for punto in puntos_venta:
        st.markdown(f'<div class="custom-box"><h3>{punto.title()}</h3>', unsafe_allow_html=True)
        vendido_col = f"{punto} vendido"
        if vendido_col in datos_filtrados.columns:
            tabla = datos_filtrados.groupby("nombre").agg(
                Unidades_Vendidas=(vendido_col, "sum"),
                Total_Ventas=(f"{punto}_ventas_calculadas", "sum"),
                Ganancia=(f"{punto}_ganancia_calculada", "sum"),
            ).reset_index().sort_values("Unidades_Vendidas", ascending=False)
            st.dataframe(tabla)
        st.markdown('</div>', unsafe_allow_html=True)

    # Gráficas (dos por fila, responsive)
    st.subheader("Gráficos de Productos Más Vendidos")
    productos_mas_vendidos = datos_filtrados.groupby("nombre")["total vendido"].sum().nlargest(5)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Top 5 Productos Más Vendidos (Totales)")
        fig, ax = plt.subplots()
        productos_mas_vendidos.plot(kind="pie", autopct='%1.1f%%', ax=ax, startangle=90, legend=False)
        ax.set_ylabel("")
        st.pyplot(fig)

    with col2:
        for punto in puntos_venta:
            st.markdown(f"#### Top 5 en {punto.title()}")
            fig, ax = plt.subplots()
            top_punto_venta = datos_filtrados.groupby("nombre")[f"{punto} vendido"].sum().nlargest(5)
            top_punto_venta.plot(kind="pie", autopct='%1.1f%%', ax=ax, startangle=90, legend=False)
            ax.set_ylabel("")
            st.pyplot(fig)

except Exception as e:
    st.error(f"Error al procesar el archivo: {e}") 

import math

# Crear sección para "Crear Orden de Compra"
st.subheader("Crear Orden de Compra")

# Filtro de punto de venta
punto_seleccionado = st.selectbox("Seleccione un Punto de Venta", puntos_venta)

# Filtro de días de ventas
dias_ventas = st.number_input("Días de Ventas a Mostrar", min_value=1, max_value=30, value=7)

# Filtros adicionales opcionales
filtro_nombre = st.multiselect("Buscar por Nombre (Acumulativo)", nombres, key="orden_filtro_nombre")
filtro_marca = st.multiselect("Filtrar por Marca (Opcional)", marcas, key="orden_filtro_marca")
filtro_categoria = st.multiselect("Filtrar por Categoría (Opcional)", categorias, key="orden_filtro_categoria")

# Filtrar los datos según los criterios seleccionados
datos_filtrados = datos.copy()

# Aplicar filtros solo si se selecciona algo
if filtro_nombre:
    datos_filtrados = datos_filtrados[datos_filtrados["nombre"].isin(filtro_nombre)]
if filtro_marca:
    datos_filtrados = datos_filtrados[datos_filtrados["marca"].isin(filtro_marca)]
if filtro_categoria:
    datos_filtrados = datos_filtrados[datos_filtrados["categoria"].isin(filtro_categoria)]

# Verificar si hay resultados tras aplicar los filtros
if not datos_filtrados.empty and punto_seleccionado:
    vendido_col = f"{punto_seleccionado} vendido"
    inventario_col = f"{punto_seleccionado} inventario"

    if vendido_col in datos_filtrados.columns and inventario_col in datos_filtrados.columns:
        # Calcular unidades vendidas en el rango de días (redondeo hacia arriba)
        datos_filtrados["Unidades Vendidas en Días"] = datos_filtrados[vendido_col].apply(
            lambda x: math.ceil((x / 30) * dias_ventas)
        )

        # Crear una copia de la columna inventario para edición
        datos_filtrados["Inventario"] = datos_filtrados[inventario_col]

        # Permitir edición manual del inventario directamente en la tabla
        for index, row in datos_filtrados.iterrows():
            datos_filtrados.at[index, "Inventario"] = st.number_input(
                f"Inventario para {row['nombre']}",
                value=row["Inventario"],
                key=f"inv_{row['nombre']}"
            )

        # Calcular unidades a comprar después de la edición
        datos_filtrados["Unidades a Comprar"] = (
            datos_filtrados["Inventario"] - datos_filtrados["Unidades Vendidas en Días"]
        ).clip(lower=0).apply(math.ceil)

        # Mostrar tabla final con diseño ajustado
        st.subheader("Resumen de Orden de Compra")
        st.write(f"**Punto de Venta:** {punto_seleccionado}")
        st.write(f"**Días de Ventas:** {dias_ventas}")
        st.table(
            datos_filtrados[[
                "nombre",
                "Unidades Vendidas en Días",
                "Inventario",
                "Unidades a Comprar"
            ]].rename(columns={
                "nombre": "Nombre",
                "Unidades Vendidas en Días": f"Ventas en {dias_ventas} días",
                "Inventario": "Inventario",
                "Unidades a Comprar": "Und. x Comprar"
            })
        )
else:
    st.warning("Por favor, seleccione filtros para mostrar los resultados.")
