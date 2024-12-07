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
if filtro_nombre:
    datos_filtrados = datos_filtrados[datos_filtrados["nombre"].isin(filtro_nombre)]
if filtro_marca:
    datos_filtrados = datos_filtrados[datos_filtrados["marca"].isin(filtro_marca)]
if filtro_categoria:
    datos_filtrados = datos_filtrados[datos_filtrados["categoria"].isin(filtro_categoria)]

# Calcular las ventas y generar la tabla
if punto_seleccionado:
    vendido_col = f"{punto_seleccionado} vendido"
    inventario_col = f"{punto_seleccionado} inventario"
    if vendido_col in datos_filtrados.columns and inventario_col in datos_filtrados.columns:
        # Calcular ventas en el rango de días y agregar columnas necesarias
        datos_filtrados["Unidades Vendidas en Días"] = (datos_filtrados[vendido_col] / 30) * dias_ventas
        datos_filtrados["Inventario"] = datos_filtrados[inventario_col]

        # Editar inventario manualmente
        inventario_modificado = st.experimental_data_editor(
            datos_filtrados[["nombre", "Inventario"]],
            key="editor_inventario",
            num_rows="dynamic",
        )

        # Calcular las unidades a ordenar
        datos_filtrados["Unidades a Comprar"] = (
            datos_filtrados["Unidades Vendidas en Días"] - inventario_modificado["Inventario"]
        ).clip(lower=0)

        # Mostrar la tabla final
        st.subheader("Resumen de Orden de Compra")
        st.dataframe(
            datos_filtrados[["nombre", "Unidades Vendidas en Días", "Inventario", "Unidades a Comprar"]]
        )
