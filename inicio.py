import streamlit as st
import pandas as pd
import plotly.express as px

def main():
    st.set_page_config(page_title="Análisis de Ventas Northwind", page_icon="📊")
    
    st.title("Proyecto de Análisis de Ventas Northwind")
    st.subheader("Jessica Arguedas Venegas")
    
    st.markdown("""
    ## Introducción
    
    El siguiente dashboard muestra un análisis de la base de datos Northwind la cual 
    muestra ventas por países y años. Es el proyecto final del curso de Taller de 
    Programación del Profesor Nayib Vargas.
    
    ### Objetivo del Proyecto
    Realizar un análisis detallado de las tendencias de ventas de la empresa Northwind 
    utilizando técnicas de visualización de datos y análisis estadístico.
    
    ### Agradecimiento
    Quiero realizarle un pequeño agradecimiento profesor Nayib por haberme apoyado en este momento tan dificil de mi
    vida y darme todo el tiempo y la paciencia para no abandonar este curso.Por que aunque falle muchas tareas siempre
    me dio la oportunidad de entregarlas. Gracias por su vocación a pesar de todas las quejas que hemos realizado.
    Le deseo los mejores éxitos en su vida laboral y personal.
                
    """
                )
    
    # Aquí puedes agregar más secciones o visualizaciones según tu proyecto
    st.sidebar.header("Jessica Arguedas Venegas")
    st.sidebar.info("Creado el 2024 , Profesor a cargo:Nayib Vargas")

if __name__ == "__main__":
    main()