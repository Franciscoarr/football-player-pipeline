# src/dashboard/app.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import altair as alt
import os
from dotenv import load_dotenv

st.set_page_config(page_title="Football Player Dashboard", layout="wide")
st.title("Football Player Data Dashboard")

@st.cache_data
def load_data():
    load_dotenv()
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB")
    
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    engine = create_engine(db_url)
    
    query = """
        SELECT p.name, p.age, p.nationality, p.height, p.weight,
               t.name as team_name, 
               s.season, s.competition, s.appearances, s.minutes, 
               s.goals, s.assists, s.key_passes, s.tackles, s.yellow_cards, s.red_cards
        FROM players p
        JOIN player_statistics s ON p.player_id = s.player_id
        JOIN teams t ON s.team_id = t.team_id;
    """
    return pd.read_sql(query, engine)

# Función auxiliar para pintar gráficos forzando el orden descendente
def plot_bar_chart(data, x_col, y_col, color="#0068c9"):
    chart = alt.Chart(data).mark_bar(color=color).encode(
        x=alt.X(f'{x_col}:N', sort='-y', title=None),
        y=alt.Y(f'{y_col}:Q', title=None),
        tooltip=[x_col, y_col]
    )
    st.altair_chart(chart, use_container_width=True)

try:
    df = load_data()
    
    # --- 1. BARRA LATERAL (Filtros en cascada) ---
    st.sidebar.header("Parámetros de Búsqueda")
    
    equipos = df['team_name'].unique().tolist()
    equipo_seleccionado = st.sidebar.selectbox("Seleccionar Equipo:", equipos)
    df_filtrado = df[df['team_name'] == equipo_seleccionado]
    
    temporadas = sorted(df_filtrado['season'].unique().tolist(), reverse=True)
    temporada_seleccionada = st.sidebar.selectbox("Seleccionar Temporada:", temporadas)
    df_filtrado = df_filtrado[df_filtrado['season'] == temporada_seleccionada]
    
    competiciones = df_filtrado['competition'].unique().tolist()
    competicion_seleccionada = st.sidebar.selectbox("Seleccionar Competición:", competiciones)
    df_filtrado = df_filtrado[df_filtrado['competition'] == competicion_seleccionada]

    # --- 2. KPIs PRINCIPALES ---
    st.markdown(f"### Resumen Analítico » {equipo_seleccionado} | {temporada_seleccionada} | {competicion_seleccionada}")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Jugadores", len(df_filtrado))
    col2.metric("Goles Totales", df_filtrado['goals'].sum())
    col3.metric("Asistencias", df_filtrado['assists'].sum())
    col4.metric("Tarjetas Amarillas", df_filtrado['yellow_cards'].sum())
    col5.metric("Tarjetas Rojas", df_filtrado['red_cards'].sum())

    st.markdown("---")

    # --- 3. GRÁFICOS VISUALES CON ALTAIR ---
    tab_ataque, tab_disciplina, tab_minutos = st.tabs(["Rendimiento Ofensivo", "Disciplina", "Participación"])

    with tab_ataque:
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("Top 5 Goleadores")
            top_goleadores = df_filtrado.nlargest(5, 'goals')
            plot_bar_chart(top_goleadores, 'name', 'goals')
        with col_chart2:
            st.subheader("Top 5 Asistentes")
            top_asistentes = df_filtrado.nlargest(5, 'assists')
            plot_bar_chart(top_asistentes, 'name', 'assists')

    with tab_disciplina:
        col_chart3, col_chart4 = st.columns(2)
        with col_chart3:
            st.subheader("Mayor Acumulación de Tarjetas Amarillas")
            top_amarillas = df_filtrado.nlargest(5, 'yellow_cards')
            plot_bar_chart(top_amarillas, 'name', 'yellow_cards', color="#ffc107") 
        with col_chart4:
            st.subheader("Mayor Acumulación de Tarjetas Rojas")
            top_rojas = df_filtrado.nlargest(5, 'red_cards')
            plot_bar_chart(top_rojas, 'name', 'red_cards', color="#dc3545") 

    with tab_minutos:
        col_chart5, col_chart6 = st.columns(2)
        with col_chart5:
            st.subheader("Minutos Disputados")
            top_minutos = df_filtrado.nlargest(5, 'minutes')
            plot_bar_chart(top_minutos, 'name', 'minutes', color="#17a2b8")
        with col_chart6:
            st.subheader("Partidos Jugados")
            top_partidos = df_filtrado.nlargest(5, 'appearances')
            plot_bar_chart(top_partidos, 'name', 'appearances', color="#28a745")

    # --- 4. TABLA DETALLADA ---
    st.markdown("---")
    st.subheader("Explorador de Datos Detallado")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error de conexión o lectura de datos: {e}")