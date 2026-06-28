import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

SUPABASE_URL = "https://zidtwltdfdwcixqmiksj.supabase.co"
SUPABASE_KEY = "sb_publishable_BPsbWExEt-F4MKfOILr_LA_zIl6P8yd"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}


def obtener_datos():
    url = f"{SUPABASE_URL}/rest/v1/Cajas_Cja?select=*&order=id_pedido.desc"
    resp = requests.get(url, headers=HEADERS)
    return resp.json()


st.set_page_config(
    page_title="Cartonera — Panel de Control",
    page_icon="📦",
    layout="wide"
)

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-card h1 { font-size: 3rem; margin: 0; }
    .metric-card p  { font-size: 1rem; margin: 0; opacity: 0.8; }
    .estado-en-proceso {
        background: linear-gradient(135deg, #1a6b3a, #27ae60);
        border-radius: 12px;
        padding: 12px 24px;
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        display: inline-block;
    }
    .estado-detenido {
        background: linear-gradient(135deg, #7b1a1a, #e74c3c);
        border-radius: 12px;
        padding: 12px 24px;
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        display: inline-block;
    }
    .estado-finalizado {
        background: linear-gradient(135deg, #1a3a7b, #2980b9);
        border-radius: 12px;
        padding: 12px 24px;
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


def badge_estado(estado):
    clase = {
        "En proceso": "estado-en-proceso",
        "Detenido":   "estado-detenido",
        "Finalizado": "estado-finalizado",
    }.get(estado, "estado-finalizado")
    icono = "🟢" if estado == "En proceso" else "🔴" if estado == "Detenido" else "✅"
    return f'<span class="{clase}">{icono} {estado}</span>'


st.title("📦 Panel de Control — Producción")
st.divider()

datos = obtener_datos()

if not datos:
    st.info("No hay pedidos registrados aún.")
    time.sleep(3)
    st.rerun()
    st.stop()

df = pd.DataFrame(datos)
ultimo = datos[0]
estado = ultimo.get("estado_pedido", "—")

col_titulo, col_estado = st.columns([3, 1])
with col_titulo:
    st.subheader(f"Pedido N° {ultimo['id_pedido']} — En curso")
with col_estado:
    st.markdown(badge_estado(estado), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <p>Cajas Chicas</p>
        <h1>{ultimo['cajas_chicas']}</h1>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <p>Cajas Grandes</p>
        <h1>{ultimo['cajas_grandes']}</h1>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <p>Total Cajas</p>
        <h1>{ultimo['total_cajas']}</h1>
    </div>""", unsafe_allow_html=True)

st.divider()

st.subheader("📊 Producción por Pedido")
df_grafico = df.copy()
df_grafico["id_pedido"] = df_grafico["id_pedido"].astype(str)

col_g1, col_g2 = st.columns(2)
with col_g1:
    fig1 = px.bar(
        df_grafico,
        x="id_pedido",
        y=["cajas_chicas", "cajas_grandes"],
        barmode="group",
        labels={"id_pedido": "N° Pedido", "value": "Cajas", "variable": "Tipo"},
        color_discrete_map={"cajas_chicas": "#2980b9", "cajas_grandes": "#27ae60"},
        title="Cajas Chicas vs Grandes por Pedido"
    )
    fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig1, use_container_width=True)

with col_g2:
    fig2 = px.line(
        df_grafico.sort_values("id_pedido"),
        x="id_pedido",
        y="total_cajas",
        markers=True,
        labels={"id_pedido": "N° Pedido", "total_cajas": "Total Cajas"},
        title="Total de Cajas por Pedido",
        color_discrete_sequence=["#e67e22"]
    )
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.subheader("📋 Historial de Pedidos")
df_tabla = df[["id_pedido", "cajas_chicas", "cajas_grandes", "total_cajas", "estado_pedido"]].copy()
df_tabla.columns = ["N° Pedido", "Cajas Chicas", "Cajas Grandes", "Total Cajas", "Estado"]
st.dataframe(df_tabla, use_container_width=True, hide_index=True)

time.sleep(3)
st.rerun()
