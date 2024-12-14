import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

def load_data():
    """Load data from SQLite database"""
    conn = sqlite3.connect("data/Northwind_small.sqlite")
    
    # Load tables using exact names from the previous code
    categoryName = pd.read_sql_query("SELECT * FROM Category", conn)
    Order = pd.read_sql_query("SELECT * FROM [Order]", conn) 
    OrderDetail = pd.read_sql_query("SELECT * FROM OrderDetail", conn)
    Product = pd.read_sql_query("SELECT * FROM Product", conn)
    Customer = pd.read_sql_query("SELECT * FROM Customer", conn)
    
    conn.close()
    
    return categoryName, Order, OrderDetail, Product, Customer

def prepare_data(Order, OrderDetail, Product, Customer, categoryName):
    """Prepare data for analysis"""
    # Preparar datos de ventas por año y país
    ordenes = Order[['Id', 'OrderDate', 'CustomerId']].copy()
    detalles_orden = OrderDetail[['OrderId', 'Quantity', 'UnitPrice']].copy()
    detalles_orden['TotalSales'] = detalles_orden['Quantity'] * detalles_orden['UnitPrice']
    
    # Merge con datos de cliente para obtener país
    clientes = Customer[['Id', 'Country']]
    ventas_por_orden = pd.merge(ordenes, detalles_orden, left_on='Id', right_on='OrderId')
    ventas_por_orden = pd.merge(ventas_por_orden, clientes, left_on='CustomerId', right_on='Id')
    
    # Procesar fechas
    ventas_por_orden['OrderDate'] = pd.to_datetime(ventas_por_orden['OrderDate'])
    ventas_por_orden['Year'] = ventas_por_orden['OrderDate'].dt.year
    
    # Ventas por año
    ventas_por_anio = ventas_por_orden.groupby('Year')['TotalSales'].sum().reset_index()
    
    # Preparar datos de productos por categoría
    product_counts = Product.groupby('CategoryId').size().reset_index(name='ProductCount')
    category_product_counts = pd.merge(product_counts, categoryName, left_on='CategoryId', right_on='Id')
    category_product_counts.loc[category_product_counts['ProductCount'] < 5, 'CategoryName'] = 'Otras categorías'
    
    # Preparar datos de productos activos vs descontinuados
    product_status = Product.groupby('Discontinued').size().reset_index(name='Count')
    product_status['Discontinued'] = product_status['Discontinued'].replace({0: 'Activos', 1: 'Descontinuados'})
    
    # Ventas por país
    ventas_por_pais = ventas_por_orden.groupby('Country')['TotalSales'].sum().reset_index().sort_values(by='TotalSales', ascending=False)
    
    return {
        'ventas_por_anio': ventas_por_anio,
        'category_product_counts': category_product_counts,
        'product_status': product_status,
        'ventas_por_pais': ventas_por_pais,
        'ventas_por_orden': ventas_por_orden
    }

def main():
    st.set_page_config(page_title="Análisis de Northwind", layout="wide")
    
    # Cargar datos
    try:
        categoryName, Order, OrderDetail, Product, Customer = load_data()
        data = prepare_data(Order, OrderDetail, Product, Customer, categoryName)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    # Título principal
    st.title("📊 Análisis de Datos de Northwind")
    
    # Filtros en la parte superior
    st.header("Filtros de Análisis")
    
    # Preparar columnas para filtros
    col1, col2 = st.columns(2)
    
    # Selector de países en la primera columna
    paises_disponibles = sorted(data['ventas_por_orden']['Country'].unique())
    with col1:
        paises_seleccionados = st.multiselect(
            "Seleccionar Países", 
            options=paises_disponibles,
            default=paises_disponibles,
            key="paises_filter"
        )
    
    # Selector de años en la segunda columna
    years = data['ventas_por_anio']['Year'].unique()
    with col2:
        selected_years = st.multiselect(
            "Seleccionar Años", 
            options=years.tolist(), 
            default=years.tolist(),
            key="years_filter"
        )
    
    # Filtrar datos
    datos_filtrados = data['ventas_por_orden'][
        (data['ventas_por_orden']['Country'].isin(paises_seleccionados)) & 
        (data['ventas_por_orden']['Year'].isin(selected_years))
    ]
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total de Categorías",
            value=len(categoryName),
            delta="Variedad de productos"
        )
    
    with col2:
        st.metric(
            label="Total de Productos",
            value=len(Product),
            delta=f"{len(Product[Product['Discontinued'] == 0])} Activos"
        )
    
    with col3:
        st.metric(
            label="Países Seleccionados",
            value=len(paises_seleccionados),
            delta="Alcance geográfico"
        )
    
    # Dividir la página en 2 columnas
    col1, col2 = st.columns(2)
    
    # Gráfico de Productos por Categoría
    with col1:
        st.subheader("Productos por Categoría")
        fig_categoria = px.pie(
            data['category_product_counts'],
            values='ProductCount',
            names='CategoryName',
            title='Distribución de Productos',
            hole=0.4
        )
        st.plotly_chart(fig_categoria, use_container_width=True)
    
    # Gráfico de Estado de Productos
    with col2:
        st.subheader("Estado de Productos")
        fig_estado = px.pie(
            data['product_status'],
            values='Count',
            names='Discontinued',
            title='Productos Activos vs Descontinuados',
            hole=0.4
        )
        st.plotly_chart(fig_estado, use_container_width=True)
    
    # Gráfico de Ventas por Año
    st.subheader("Evolución de Ventas Anuales")
    ventas_filtradas_anio = data['ventas_por_anio'][data['ventas_por_anio']['Year'].isin(selected_years)]
    fig_ventas = px.line(
        ventas_filtradas_anio,
        x='Year',
        y='TotalSales',
        title='Ventas Totales por Año',
        labels={'Year': 'Año', 'TotalSales': 'Ventas Totales'}
    )
    st.plotly_chart(fig_ventas, use_container_width=True)
    
    # Gráfico de Ventas por País
    st.subheader("Ventas Totales por País")
    # Filtrar ventas por países seleccionados
    ventas_pais_filtradas = data['ventas_por_pais'][data['ventas_por_pais']['Country'].isin(paises_seleccionados)]
    fig_pais = px.bar(
        ventas_pais_filtradas,
        x='Country', 
        y='TotalSales', 
        title='Ventas por País Seleccionados', 
        labels={'Country': 'País', 'TotalSales': 'Total de Ventas'}
    )
    st.plotly_chart(fig_pais, use_container_width=True)
    
    # Tabla de Ventas Detallada
    st.subheader("Detalle de Ventas")
    st.dataframe(datos_filtrados[['Country', 'Year', 'TotalSales']].groupby(['Country', 'Year']).sum().reset_index())
    
    # Recomendaciones
    st.header("🚀 Recomendaciones")
    st.markdown("""
    - **Diversificación de Productos**: Considerar añadir más variedad en categorías con pocos productos.
    - **Gestión de Inventario**: Revisar y potencialmente reactivar productos descontinuados.
    - **Estrategia de Mercado**: Explorar oportunidades en países con menor volumen de ventas.
    - **Análisis de Tendencias**: Investigar los factores que impulsan las fluctuaciones anuales de ventas.
    """)

if __name__ == "__main__":
    main()