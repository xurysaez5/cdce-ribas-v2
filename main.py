import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="CDCE RIBAS V2",
    layout="wide", # Usamos todo el ancho de la pantalla
    initial_sidebar_state="collapsed"
)

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
<style>
    /* Fondo principal claro */
    [data-testid="stAppViewContainer"] { background-color: #F8F9FA; }
    
    /* Tarjeta KPI elegante */
    .kpi-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #002D57;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.08);
        text-align: center;
    }
    .kpi-value { font-size: 2rem; font-weight: bold; color: #002D57; margin: 0; }
    .kpi-label { font-size: 0.9rem; color: #666; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# --- ESTRUCTURA DEL MENÚ PRINCIPAL ---
st.title("Panel de Control CDCE - Municipio Ribas")
st.write("---")

# ZONA 1: INDICADORES SUPERIORES (KPIs)
# Creamos 4 columnas iguales para dar aire al diseño
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown('<div class="kpi-card"><p class="kpi-label">Matrícula Total</p><p class="kpi-value">24,500</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="kpi-card"><p class="kpi-label">Personal Activo</p><p class="kpi-value">1,200</p></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="kpi-card"><p class="kpi-label">Escuelas Reportadas</p><p class="kpi-value">54/84</p></div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="kpi-card"><p class="kpi-label" style="color:#D32F2F;">Pendientes</p><p class="kpi-value" style="color:#D32F2F;">30</p></div>', unsafe_allow_html=True)

st.write("##") # Un pequeño espacio de separación

# ZONA 2: CUERPO CENTRAL (Gráfico y Listas)
col_grafico, col_lista = st.columns([2, 1]) # La columna del gráfico es el doble de ancha

with col_grafico:
    st.subheader("📍 Distribución por Niveles")
    st.info("Aquí colocaremos el gráfico de barras o torta más adelante.")

with col_lista:
    st.subheader("🔔 Alertas de Directores")
    st.warning("Lista de directores que aún no han actualizado datos.")
