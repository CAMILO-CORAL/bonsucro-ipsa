import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import streamlit.components.v1 as components

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Bonsucro · Análisis de Áreas Afectadas",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Root tokens · Paleta institucional Providencia ── */
:root {
    --bg:          #F6F8F2;
    --surface:     #FFFFFF;
    --surface2:    #D8EBCB;
    --surface3:    #EEF5E8;
    --border:      #9AC864;
    --accent:      #72B328;
    --accent2:     #5F8A6E;
    --accent3:     #004024;
    --text:        #08321F;
    --text-muted:  #516E62;
    --danger:      #004024;
    --warning:     #72B328;
    --highlight:   #9AC864;
    --font-head:   'Syne', sans-serif;
    --font-body:   'DM Sans', sans-serif;
    --font-mono:   'DM Mono', monospace;
    --radius:      8px;
    --radius-lg:   14px;
}

/* ── Base overrides ── */
html, body, [class*="css"] {
    font-family: var(--font-body);
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background-color: var(--bg) !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #004024 0%, #08321F 100%) !important;
    border-right: 1px solid #5F8A6E !important;
}
[data-testid="stSidebar"] * { color: #FFFFFF !important; }
[data-testid="stSidebar"] .stCheckbox label {
    font-family: var(--font-mono) !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.04em !important;
    color: #D8EBCB !important;
    transition: color .2s;
}
[data-testid="stSidebar"] .stCheckbox label:hover { color: #9AC864 !important; }

/* Sidebar header text */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-family: var(--font-head) !important;
    color: #9AC864 !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid #5F8A6E;
    padding-bottom: 6px;
    margin-bottom: 12px;
}

/* ── Main headings ── */
h1, h2, h3, h4 {
    font-family: var(--font-head) !important;
    color: var(--text) !important;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] select,
.stSelectbox > div > div {
    background: #FFFFFF !important;
    border: 1px solid #9AC864 !important;
    color: #08321F !important;
    border-radius: var(--radius) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
}

/* ── DataFrames ── */
.dataframe, [data-testid="stDataFrame"] {
    background: #FFFFFF !important;
    border: 1px solid #9AC864 !important;
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] th {
    background: #D8EBCB !important;
    color: #004024 !important;
    font-family: var(--font-mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid #9AC864 !important;
}
[data-testid="stDataFrame"] td {
    font-family: var(--font-mono) !important;
    font-size: 0.8rem !important;
    color: #516E62 !important;
    border-color: #D8EBCB !important;
}

/* ── Streamlit divider ── */
hr { border-color: #9AC864 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #EEF5E8; }
::-webkit-scrollbar-thumb { background: #9AC864; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #72B328; }

/* ── Warning/info box ── */
[data-testid="stAlert"] {
    background: #EEF5E8 !important;
    border-left: 3px solid #72B328 !important;
    border-radius: var(--radius) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.8rem !important;
    color: #08321F !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HELPER: reusable card components
# ─────────────────────────────────────────────
def metric_card(label, value, unit="", accent="#72B328", delta=None):
    delta_html = ""
    if delta is not None:
        color = "#72B328" if delta >= 0 else "#004024"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f'<div style="font-family:\'DM Mono\',monospace;font-size:0.72rem;color:{color};margin-top:4px;">{arrow} {abs(delta):.1f}%</div>'
    return f"""
    <div style="
        background: linear-gradient(135deg, #FFFFFF 0%, #EEF5E8 100%);
        border: 1px solid #9AC864;
        border-top: 3px solid {accent};
        border-radius: 12px;
        padding: 20px 22px 16px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 64, 36, 0.08);
    ">
      <div style="
        position:absolute;top:-20px;right:-20px;
        width:80px;height:80px;border-radius:50%;
        background:{accent}18;
      "></div>
      <div style="font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:0.18em;
                  text-transform:uppercase;color:#516E62;margin-bottom:10px;">{label}</div>
      <div style="font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:700;
                  color:#08321F;line-height:1;">{value}
        <span style="font-size:0.9rem;font-weight:400;color:{accent};margin-left:4px;">{unit}</span>
      </div>
      {delta_html}
    </div>
    """

def section_header(title, subtitle="", icon=""):
    return f"""
    <div style="margin: 38px 0 18px; display:flex; align-items:flex-end; gap:14px;">
      <div>
        <div style="font-family:'DM Mono',monospace;font-size:0.62rem;letter-spacing:0.22em;
                    text-transform:uppercase;color:#72B328;margin-bottom:4px;">{icon} {subtitle}</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.35rem;font-weight:700;
                    color:#08321F;border-bottom:1px solid #9AC864;padding-bottom:10px;">{title}</div>
      </div>
    </div>
    """

def tag(text, color="#72B328"):
    return f'<span style="background:{color}18;color:{color};border:1px solid {color}40;border-radius:4px;padding:2px 8px;font-family:\'DM Mono\',monospace;font-size:0.68rem;letter-spacing:0.06em;">{text}</span>'

# ─────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_excel('Streamlit.xlsx')

data = load_data()

# ─────────────────────────────────────────────
#  HEADER BANNER
# ─────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #FFFFFF 0%, #EEF5E8 58%, #D8EBCB 100%);
    border: 1px solid #9AC864;
    border-left: 6px solid #004024;
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 14px 40px rgba(0, 64, 36, 0.08);
">
  <div style="font-size:2.2rem;">🌿</div>
  <div>
    <div style="font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:0.25em;
                text-transform:uppercase;color:#72B328;margin-bottom:4px;">
        Sistema de Monitoreo · Bonsucro
    </div>
    <div style="font-family:'Syne',sans-serif;font-size:1.7rem;font-weight:800;color:#004024;line-height:1.1;">
        Análisis de Áreas Afectadas en Haciendas
    </div>
    <div style="font-family:'DM Sans',sans-serif;font-size:0.82rem;color:#516E62;margin-top:6px;">
        Monitoreo de afectación hídrica y multitemporal por tenencia · Caña de azúcar
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 16px 0 8px;">
        <div style="font-family:'DM Mono',monospace;font-size:0.6rem;letter-spacing:0.25em;
                    text-transform:uppercase;color:#9AC864;margin-bottom:2px;"></div>
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:#FFFFFF;">
            Panel de Control
        </div>
    </div>
    <hr style="border-color:#5F8A6E;margin:8px 0 16px;">
    """, unsafe_allow_html=True)

    st.markdown("**TENENCIAS**", help="Selecciona una o más tenencias para filtrar el análisis")

    # Diccionario de equivalencias de tenencia
    tenencia_labels = {
        11: "11 - Propias",
        28: "28 - Arrendadas",
        31: "31 - Participación",
        51: "51 - Proveedores Caña",
        81: "81 - Compras Ocasionales"
    }

    # Obtener solo las tenencias existentes en el xlsx
    tenencias_disponibles = []
    for t in data['Tenencia'].dropna().unique():
        try:
            t_int = int(float(t))
            if t_int in tenencia_labels:
                tenencias_disponibles.append(t_int)
        except:
            pass

    tenencias_disponibles = sorted(set(tenencias_disponibles))

    tenencia_seleccionada = []
    for tenencia in tenencias_disponibles:
        if st.checkbox(tenencia_labels[tenencia], key=f"tenencia_{tenencia}"):
            tenencia_seleccionada.append(tenencia)

    st.markdown("<hr style='border-color:#5F8A6E;margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown("**UMBRAL DE AFECTACIÓN**")

    limite_input = st.text_input("Límite (%):", value="4", label_visibility="collapsed")
    try:
        limite_afectacion = float(limite_input)
    except ValueError:
        st.warning("Ingresa un valor numérico válido.")
        limite_afectacion = 4

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.08);border:1px solid #5F8A6E;border-radius:8px;
                padding:10px 14px;margin-top:8px;backdrop-filter: blur(6px);">
        <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#D8EBCB;
                    letter-spacing:0.1em;text-transform:uppercase;">Umbral activo</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;
                    color:#9AC864;">{limite_afectacion:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#5F8A6E;margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#D8EBCB;line-height:1.8;">
        <div>REGISTROS TOTALES &nbsp;<span style="color:#FFFFFF;">{len(data):,}</span></div>
        <div>TENENCIAS &nbsp;<span style="color:#FFFFFF;">{data['Tenencia'].nunique()}</span></div>
        <div>HACIENDAS &nbsp;<span style="color:#FFFFFF;">{data['Nombre'].nunique()}</span></div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FILTER DATA
# ─────────────────────────────────────────────
filtered_data = data[data['Tenencia'].apply(lambda x: int(float(x)) if pd.notna(x) else x).isin(tenencia_seleccionada)]

# ─────────────────────────────────────────────
#  ESTADO VACÍO
# ─────────────────────────────────────────────
if filtered_data.empty:
    st.markdown("""
    <div style="text-align:center;padding:70px 40px;border:1px dashed #9AC864;
                border-radius:14px;margin:30px 0;background:#FFFFFF;">
        <div style="font-size:2.5rem;margin-bottom:12px;">⬡</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:600;
                    color:#004024;margin-bottom:6px;">Sin datos seleccionados</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.75rem;color:#516E62;">
            Activa una o más tenencias en el panel lateral para iniciar el análisis
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
#  SECCIÓN 1 · KPI CARDS
# ─────────────────────────────────────────────
total_hectareas       = filtered_data['Area caña (Ha)'].sum()
promedio_afectacion   = filtered_data['Total porcentaje Afectación'].mean()
promedio_buff         = filtered_data['Porcentaje Afectación por buff hidríco'].mean()
promedio_multi        = filtered_data['Porcentaje Afectación por Multitemporal'].mean()
num_haciendas         = filtered_data['Nombre'].nunique()
haciendas_criticas    = filtered_data[filtered_data['Total porcentaje Afectación'] > limite_afectacion]
pct_criticas          = (haciendas_criticas['Nombre'].nunique() / num_haciendas * 100) if num_haciendas else 0

st.markdown(section_header(
    "Resumen Ejecutivo", "Indicadores Clave de Desempeño", "◈"
), unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(metric_card("Total de Hectáreas en caña", f"{total_hectareas:,.1f}", "Ha", "#72B328"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("Número de Haciendas", f"{num_haciendas}", "", "#004024"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("Porcentaje Promedio de Afectación total", f"{promedio_afectacion:.1f}", "%", "#5F8A6E"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("Porcentaje Promedio de Afectación por Buff hídrico", f"{promedio_buff:.1f}", "%", "#9AC864"), unsafe_allow_html=True)
with c5:
    st.markdown(metric_card("Porcentaje Promedio de Afectación Multitemporal", f"{promedio_multi:.1f}", "%", "#08321F"), unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SECCIÓN 2 · HACIENDAS SOBRE EL UMBRAL
# ─────────────────────────────────────────────
st.markdown(section_header(
    f"Haciendas con Afectación > {limite_afectacion:.0f}%",
    "Alerta de Umbral", "⚠"
), unsafe_allow_html=True)

col_a, col_b = st.columns([1, 2])

with col_a:
    ha_criticas_sum = haciendas_criticas['Area caña (Ha)'].sum()
    n_criticas      = haciendas_criticas.shape[0]
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#FFFFFF,#EEF5E8);
                border:1px solid #9AC864;border-radius:12px;padding:24px;
                box-shadow: 0 10px 28px rgba(0, 64, 36, 0.06);">
        <div style="font-family:'DM Mono',monospace;font-size:0.62rem;letter-spacing:0.2em;
                    text-transform:uppercase;color:#004024;margin-bottom:14px;">
            ● REGISTROS EN ALERTA
        </div>
        <div style="display:flex;gap:24px;flex-wrap:wrap;">
            <div>
                <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:#004024;">
                    {n_criticas}
                </div>
                <div style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#516E62;">
                    Número de haciendas con afectación mayor al umbral definido
                </div>
            </div>
            <div>
                <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:#72B328;">
                    {ha_criticas_sum:,.1f}
                </div>
                <div style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#516E62;">
                    Número de Hectáreas con afectación mayor al umbral definido
                </div>
            </div>
        </div>
        <div style="margin-top:16px;background:#D8EBCB;border-radius:6px;padding:8px 12px;">
            <div style="font-family:'DM Mono',monospace;font-size:0.7rem;color:#08321F;">
                {pct_criticas:.1f}% del total de haciendas supera el umbral definido
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    if not haciendas_criticas.empty:
        # Mini bar chart
        top_criticas = (haciendas_criticas
                        .groupby('Nombre')['Total porcentaje Afectación']
                        .mean()
                        .sort_values(ascending=True)
                        .tail(8))

        fig, ax = plt.subplots(figsize=(6, 3.2))
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')

        colors = ['#004024' if v > 75 else '#72B328' if v > 60 else '#9AC864'
                  for v in top_criticas.values]

        bars = ax.barh(
            top_criticas.index,
            top_criticas.values,
            color=colors,
            height=0.55,
            zorder=3
        )

        ax.axvline(
            limite_afectacion,
            color='#516E62',
            linewidth=1,
            linestyle='--',
            alpha=0.5,
            zorder=4
        )

        ax.text(
            limite_afectacion + 0.03,
            -0.45,
            f'{limite_afectacion:.0f}%',
            color='#516E62',
            fontsize=7,
            fontfamily='monospace'
        )

        # Etiquetas de porcentaje al final de cada barra
        for bar, value in zip(bars, top_criticas.values):
            ax.text(
                bar.get_width() + 0.05,
                bar.get_y() + bar.get_height() / 2,
                f'{value:.2f}%',
                va='center',
                ha='left',
                fontsize=8,
                color='#516E62',
                fontfamily='monospace'
            )

        ax.set_xlabel('Afectación (%)', color='#516E62', fontsize=8, fontfamily='monospace')
        ax.tick_params(colors='#516E62', labelsize=7.5)
        ax.xaxis.label.set_fontfamily('monospace')

        for spine in ax.spines.values():
            spine.set_edgecolor('#9AC864')

        ax.grid(axis='x', color='#D8EBCB', linewidth=0.7, zorder=0)

        # Ajuste del límite del eje X para que quepan las etiquetas
        max_val = top_criticas.max()
        ax.set_xlim(0, max_val + 0.5)

        plt.tight_layout(pad=0.5)
        st.pyplot(fig, use_container_width=True)
        plt.close()
    else:
        st.markdown("""
        <div style="border:1px dashed #9AC864;border-radius:10px;padding:30px;text-align:center;background:#FFFFFF;">
            <div style="font-family:'DM Mono',monospace;font-size:0.75rem;color:#516E62;">
                Ninguna hacienda supera el umbral definido
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SECCIÓN 3 · RANKING TENENCIAS
#  (ESTÁTICO: NO DEPENDE DE LOS FILTROS LATERALES)
# ─────────────────────────────────────────────
st.markdown(section_header(
    "Ranking de Tenencias por Afectación",
    "Clasificación Comparativa Global", "◎"
), unsafe_allow_html=True)

# Ranking global con TODAS las tenencias del archivo
ranking_tenencias = (
    data.groupby('Tenencia', dropna=False)
    .agg(
        Afectación_promedio=('Total porcentaje Afectación', 'mean'),
        Hectáreas=('Area caña (Ha)', 'sum'),
        Haciendas=('Nombre', 'nunique')
    )
    .reset_index()
)

# Eliminar tenencias vacías
ranking_tenencias = ranking_tenencias[ranking_tenencias['Tenencia'].notna()].copy()

# Orden descendente: mayor a menor afectación promedio
ranking_tenencias = ranking_tenencias.sort_values(
    by='Afectación_promedio',
    ascending=False
).reset_index(drop=True)

# Ranking 1, 2, 3...
ranking_tenencias.index += 1

rows_html = ""

max_pct = ranking_tenencias['Afectación_promedio'].max()
if pd.isna(max_pct) or max_pct == 0:
    max_pct = 1

for rank, row in ranking_tenencias.iterrows():
    pct = float(row['Afectación_promedio'])
    hectareas = float(row['Hectáreas'])
    haciendas = int(row['Haciendas'])

    tenencia_val = row['Tenencia']
    if pd.notna(tenencia_val):
        if isinstance(tenencia_val, (int, np.integer)):
            tenencia_txt = str(tenencia_val)
        elif isinstance(tenencia_val, float) and tenencia_val.is_integer():
            tenencia_txt = str(int(tenencia_val))
        else:
            tenencia_txt = str(tenencia_val)
    else:
        tenencia_txt = "Sin dato"

    # Escala de color adaptada a porcentajes bajos
    if pct >= 1.0:
        bar_color = '#004024'
    elif pct >= 0.30:
        bar_color = '#72B328'
    else:
        bar_color = '#9AC864'

    # Barra visual normalizada respecto al máximo
    bar_w = max((pct / max_pct) * 100, 4)

    rows_html += f"""
    <tr style="border-bottom:1px solid #D8EBCB;">
      <td style="padding:10px 8px;font-family:'DM Mono',monospace;font-size:0.72rem;
                 color:#516E62;text-align:center;">{rank:02d}</td>
      <td style="padding:10px 12px;font-family:'DM Sans',sans-serif;font-size:0.82rem;
                 font-weight:500;color:#08321F;">{tenencia_txt}</td>
      <td style="padding:10px 8px;text-align:right;font-family:'DM Mono',monospace;
                 font-size:0.78rem;color:{bar_color};font-weight:500;">
          {pct:.2f}%
      </td>
      <td style="padding:10px 16px;width:140px;">
          <div style="background:#D8EBCB;border-radius:4px;height:7px;width:120px;">
            <div style="background:{bar_color};width:{bar_w:.1f}%;height:7px;border-radius:4px;"></div>
          </div>
      </td>
      <td style="padding:10px 8px;font-family:'DM Mono',monospace;font-size:0.72rem;
                 color:#516E62;text-align:right;">{hectareas:,.1f} Ha</td>
      <td style="padding:10px 8px;font-family:'DM Mono',monospace;font-size:0.72rem;
                 color:#516E62;text-align:right;">{haciendas} haciendas</td>
    </tr>
    """

tabla_html = f"""
<div style="background:#FFFFFF;border:1px solid #9AC864;border-radius:12px;overflow:hidden;
            box-shadow: 0 10px 30px rgba(0, 64, 36, 0.06);">
  <table style="width:100%;border-collapse:collapse;background:#FFFFFF;">
    <thead>
      <tr style="background:#D8EBCB;border-bottom:2px solid #9AC864;">
        <th style="padding:10px 8px;font-family:'DM Mono',monospace;font-size:0.62rem;
                   letter-spacing:0.15em;text-transform:uppercase;color:#004024;text-align:center;">#</th>
        <th style="padding:10px 12px;font-family:'DM Mono',monospace;font-size:0.62rem;
                   letter-spacing:0.15em;text-transform:uppercase;color:#004024;text-align:left;">Tenencia</th>
        <th style="padding:10px 8px;font-family:'DM Mono',monospace;font-size:0.62rem;
                   letter-spacing:0.15em;text-transform:uppercase;color:#004024;text-align:right;">Afectación</th>
        <th style="padding:10px 16px;font-family:'DM Mono',monospace;font-size:0.62rem;
                   letter-spacing:0.15em;text-transform:uppercase;color:#004024;text-align:left;">Promedio</th>
        <th style="padding:10px 8px;font-family:'DM Mono',monospace;font-size:0.62rem;
                   letter-spacing:0.15em;text-transform:uppercase;color:#004024;text-align:right;">Hectáreas</th>
        <th style="padding:10px 8px;font-family:'DM Mono',monospace;font-size:0.62rem;
                   letter-spacing:0.15em;text-transform:uppercase;color:#004024;text-align:right;">Haciendas</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</div>
"""

altura_tabla = min(520, 70 + len(ranking_tenencias) * 44)
components.html(tabla_html, height=altura_tabla, scrolling=True)

# ─────────────────────────────────────────────
#  SECCIÓN 4 · HACIENDAS CON MAYOR AFECTACIÓN
# ─────────────────────────────────────────────
st.markdown(section_header(
    "Haciendas con Mayor Afectación",
    "Detalle por Unidad Productiva", "▣"
), unsafe_allow_html=True)

ranking_haciendas = (
    filtered_data[[
        'Hac_Ste',
        'Nombre',
        'Tenencia',
        'Area caña (Ha)',
        'Total porcentaje Afectación',
        'Porcentaje Afectación por buff hidríco',
        'Porcentaje Afectación por Multitemporal'
    ]]
    .sort_values('Total porcentaje Afectación', ascending=False)
    .head(10)
    .reset_index(drop=True)
)
ranking_haciendas.index += 1

col_h1, col_h2 = st.columns([1.25, 1.15])

with col_h1:
    n_rows = len(ranking_haciendas)
    fig_t, ax_t = plt.subplots(figsize=(7.4, 0.46 * n_rows + 0.9))
    fig_t.patch.set_facecolor('#FFFFFF')
    ax_t.set_facecolor('#FFFFFF')
    ax_t.axis('off')

    medals = {1: '#72B328', 2: '#5F8A6E', 3: '#9AC864'}

    col_labels = ['#', 'CÓDIGO', 'HACIENDA', 'TENENCIA', '% AFECTACIÓN', 'HECTÁREAS']
    col_x      = [0.03, 0.12, 0.23, 0.56, 0.80, 0.96]
    col_align  = ['center', 'center', 'left', 'center', 'right', 'right']

    # Header
    for cx, lbl, align in zip(col_x, col_labels, col_align):
        ha_val = 'center' if align == 'center' else align
        ax_t.text(
            cx, 1.0, lbl,
            transform=ax_t.transAxes,
            color='#004024',
            fontsize=6.4,
            fontweight='bold',
            fontfamily='monospace',
            ha=ha_val,
            va='bottom'
        )

    # Header separator
    ax_t.plot(
        [0.01, 0.99], [0.97, 0.97],
        color='#9AC864',
        linewidth=1.2,
        transform=ax_t.transAxes,
        clip_on=False
    )

    row_h = 0.93 / n_rows if n_rows > 0 else 0.1

    for i, (rank, row) in enumerate(ranking_haciendas.iterrows()):
        pct = float(row['Total porcentaje Afectación'])
        pct_color = '#004024' if pct > 75 else '#72B328' if pct > 50 else '#5F8A6E'
        y_pos = 0.95 - (i + 0.5) * row_h

        # Fondo alternado
        if i % 2 == 0:
            rect = plt.Rectangle(
                (0.01, y_pos - row_h * 0.5),
                0.98,
                row_h,
                transform=ax_t.transAxes,
                color='#EEF5E8',
                zorder=0,
                clip_on=False
            )
            ax_t.add_patch(rect)

        # Ranking
        rank_color = medals.get(rank, '#516E62')
        rank_label = {1: '★1', 2: '★2', 3: '★3'}.get(rank, f'{rank:02d}')
        ax_t.text(
            col_x[0], y_pos, rank_label,
            transform=ax_t.transAxes,
            color=rank_color,
            fontsize=7.4,
            fontfamily='monospace',
            ha='center',
            va='center',
            fontweight='bold'
        )

        # Código
        codigo = row['Hac_Ste']
        if pd.notna(codigo):
            if isinstance(codigo, float) and codigo.is_integer():
                codigo_txt = str(int(codigo))
            else:
                codigo_txt = str(codigo)
        else:
            codigo_txt = '—'

        ax_t.text(
            col_x[1], y_pos, "0" + codigo_txt,
            transform=ax_t.transAxes,
            color='#516E62',
            fontsize=6.7,
            fontfamily='monospace',
            ha='center',
            va='center'
        )

        # Nombre
        nombre = str(row['Nombre'])[:24]
        ax_t.text(
            col_x[2], y_pos, nombre,
            transform=ax_t.transAxes,
            color='#08321F',
            fontsize=6.9,
            fontfamily='monospace',
            ha='left',
            va='center'
        )

        # Tenencia
        tenencia = row['Tenencia']
        if pd.notna(tenencia):
            if isinstance(tenencia, float) and tenencia.is_integer():
                tenencia_txt = str(int(tenencia))
            else:
                tenencia_txt = str(tenencia)
        else:
            tenencia_txt = '—'

        ax_t.text(
            col_x[3], y_pos, tenencia_txt,
            transform=ax_t.transAxes,
            color='#72B328',
            fontsize=6.8,
            fontfamily='monospace',
            ha='center',
            va='center'
        )

        # % Afectación SIN barra de fondo
        ax_t.text(
            col_x[4], y_pos, f'{pct:.1f}%',
            transform=ax_t.transAxes,
            color=pct_color,
            fontsize=7.3,
            fontfamily='monospace',
            ha='right',
            va='center',
            fontweight='bold'
        )

        # Hectáreas
        ax_t.text(
            col_x[5], y_pos, f"{row['Area caña (Ha)']:,.1f}",
            transform=ax_t.transAxes,
            color='#516E62',
            fontsize=6.7,
            fontfamily='monospace',
            ha='right',
            va='center'
        )

        # Separador de fila
        ax_t.plot(
            [0.01, 0.99], [y_pos - row_h * 0.5, y_pos - row_h * 0.5],
            color='#D8EBCB',
            linewidth=0.6,
            transform=ax_t.transAxes,
            clip_on=False
        )

    for spine in ['top', 'bottom', 'left', 'right']:
        ax_t.spines[spine].set_visible(False)

    plt.tight_layout(pad=0.25)
    st.pyplot(fig_t, use_container_width=True)
    plt.close()

with col_h2:
    fig3, ax3 = plt.subplots(figsize=(5.8, 3.9))
    fig3.patch.set_facecolor('#FFFFFF')
    ax3.set_facecolor('#FFFFFF')

    names  = [str(n)[:18] for n in ranking_haciendas['Nombre'].values]
    af_tot = ranking_haciendas['Total porcentaje Afectación'].values
    af_buf = ranking_haciendas['Porcentaje Afectación por buff hidríco'].values
    af_mul = ranking_haciendas['Porcentaje Afectación por Multitemporal'].values

    x = np.arange(len(names))
    bw = 0.26

    ax3.bar(x - bw, af_tot, bw, label='Total', color='#004024', alpha=0.92, zorder=3)
    ax3.bar(x,      af_buf, bw, label='Buff hídrico', color='#72B328', alpha=0.92, zorder=3)
    ax3.bar(x + bw, af_mul, bw, label='Multitemporal', color='#516E62', alpha=0.75, zorder=3)

    ax3.set_xticks(x)
    ax3.set_xticklabels(
        names,
        rotation=35,
        ha='right',
        fontsize=6.5,
        color='#516E62',
        fontfamily='monospace'
    )

    ax3.tick_params(axis='y', colors='#516E62', labelsize=7.5)
    ax3.yaxis.set_major_formatter(mticker.FormatStrFormatter('%g%%'))

    for spine in ax3.spines.values():
        spine.set_edgecolor('#9AC864')

    ax3.grid(axis='y', color='#D8EBCB', linewidth=0.7, zorder=0)

    ax3.legend(
        fontsize=7.5,
        frameon=False,
        loc='upper right',
        labelcolor='#08321F'
    )

    ax3.set_title(
        'Comparación de Afectación por Hacienda',
        color='#08321F',
        fontsize=8.5,
        fontfamily='monospace',
        pad=10
    )

    plt.tight_layout(pad=0.5)
    st.pyplot(fig3, use_container_width=True)
    plt.close()

# ─────────────────────────────────────────────
#  SECCIÓN 5 · DETALLE HACIENDA
# ─────────────────────────────────────────────
st.markdown(section_header(
    "Ficha Técnica de Hacienda",
    "Consulta Individual", "⊕"
), unsafe_allow_html=True)

hacienda_filtrada = st.selectbox(
    "Selecciona una hacienda:",
    data['Nombre'].dropna().unique(),
    label_visibility="collapsed"
)

hacienda_data = data[data['Nombre'] == hacienda_filtrada].copy()

if not hacienda_data.empty:
    row0 = hacienda_data.iloc[0]
    af = float(row0['Total porcentaje Afectación'])
    af_color = '#004024' if af > 75 else '#72B328' if af > 50 else '#5F8A6E'

    # ── Formateo de código principal ──
    codigo_hacienda = row0.get('Hac_Ste', '—')
    if pd.notna(codigo_hacienda) and codigo_hacienda != '—':
        try:
            codigo_hacienda = f"{int(float(codigo_hacienda)):06d}"
        except:
            codigo_hacienda = str(codigo_hacienda)
    else:
        codigo_hacienda = '—'

    # ── Formateo de tenencia principal ──
    tenencia_hacienda = row0.get('Tenencia', '—')
    if pd.notna(tenencia_hacienda) and tenencia_hacienda != '—':
        try:
            tenencia_hacienda = str(int(float(tenencia_hacienda)))
        except:
            tenencia_hacienda = str(tenencia_hacienda)
    else:
        tenencia_hacienda = '—'

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#FFFFFF,#EEF5E8);
                border:1px solid #9AC864;border-radius:12px;
                padding:18px 24px;margin-bottom:12px;
                display:flex;gap:32px;flex-wrap:wrap;align-items:center;
                box-shadow: 0 12px 28px rgba(0, 64, 36, 0.06);">
        <div>
            <div style="font-family:'DM Mono',monospace;font-size:0.6rem;letter-spacing:0.18em;
                        text-transform:uppercase;color:#516E62;">Hacienda</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
                        color:#004024;">{hacienda_filtrada}</div>
        </div>
        <div>
            <div style="font-family:'DM Mono',monospace;font-size:0.6rem;letter-spacing:0.18em;
                        text-transform:uppercase;color:#516E62;">Código</div>
            <div style="font-family:'DM Mono',monospace;font-size:0.95rem;color:#08321F;">
                {codigo_hacienda}
            </div>
        </div>
        <div>
            <div style="font-family:'DM Mono',monospace;font-size:0.6rem;letter-spacing:0.18em;
                        text-transform:uppercase;color:#516E62;">Tenencia</div>
            <div style="font-family:'DM Mono',monospace;font-size:0.85rem;color:#72B328;">
                {tenencia_hacienda}
            </div>
        </div>
        <div>
            <div style="font-family:'DM Mono',monospace;font-size:0.6rem;letter-spacing:0.18em;
                        text-transform:uppercase;color:#516E62;">Área caña</div>
            <div style="font-family:'Syne',sans-serif;font-size:0.95rem;font-weight:600;
                        color:#08321F;">{row0.get('Area caña (Ha)', 0):,.1f} Ha</div>
        </div>
        <div>
            <div style="font-family:'DM Mono',monospace;font-size:0.6rem;letter-spacing:0.18em;
                        text-transform:uppercase;color:#516E62;">Afectación total</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;
                        color:{af_color};">{af:.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Copia para mostrar abajo con formato legible ──
    detalle_df = hacienda_data.copy()

    # Renombrar columnas para visualización
    detalle_df = detalle_df.rename(columns={
        'Hac_Ste': 'Hacienda'
    })

    # Formatear Hacienda a 6 dígitos con cero inicial
    if 'Hacienda' in detalle_df.columns:
        def format_hacienda(v):
            if pd.isna(v):
                return '—'
            try:
                return f"{int(float(v)):06d}"
            except:
                return str(v)
        detalle_df['Hacienda'] = detalle_df['Hacienda'].apply(format_hacienda)

    # Formatear Tenencia sin decimal
    if 'Tenencia' in detalle_df.columns:
        def format_tenencia(v):
            if pd.isna(v):
                return '—'
            try:
                return str(int(float(v)))
            except:
                return str(v)
        detalle_df['Tenencia'] = detalle_df['Tenencia'].apply(format_tenencia)

    # Columnas numéricas a 2 decimales
    columnas_2_decimales = [
        'Area caña (Ha)',
        'Total area afec buff hídríco (Ha)',
        'Porcentaje Afectación por buff hídríco',
        'Total area afec Multitemporal (Ha)',
        'Porcentaje Afectación por Multitemporal',
        'Total area afec (Ha)',
        'Total porcentaje Afectación'
    ]

    for col in columnas_2_decimales:
        if col in detalle_df.columns:
            detalle_df[col] = detalle_df[col].apply(
                lambda x: f"{float(x):,.2f}" if pd.notna(x) else '—'
            )

    html_table = detalle_df.to_html(index=False, escape=False, classes="bonsucro-table")

    tabla_detalle_html = f"""
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: #F6F8F2;
            font-family: 'DM Mono', monospace;
        }}

        .bonsucro-table-wrap {{
            width: 100%;
            overflow-x: auto;
            overflow-y: hidden;
            border: 1px solid #9AC864;
            border-radius: 12px;
            background: #FFFFFF;
            box-sizing: border-box;
        }}

        table.bonsucro-table {{
            width: max-content;
            min-width: 100%;
            border-collapse: collapse;
            table-layout: auto;
            background: #FFFFFF;
            color: #08321F;
            font-family: 'DM Mono', monospace;
            font-size: 12px;
            white-space: nowrap;
        }}

        table.bonsucro-table thead tr {{
            background: #D8EBCB;
            border-bottom: 1px solid #9AC864;
        }}

        table.bonsucro-table th {{
            padding: 10px 12px;
            text-align: left;
            color: #004024;
            font-size: 11px;
            letter-spacing: 0.04em;
            font-weight: 600;
            border-right: 1px solid #9AC864;
        }}

        table.bonsucro-table td {{
            padding: 10px 12px;
            color: #08321F;
            border-top: 1px solid #D8EBCB;
            border-right: 1px solid #D8EBCB;
        }}

        table.bonsucro-table th:last-child,
        table.bonsucro-table td:last-child {{
            border-right: none;
        }}

        table.bonsucro-table tbody tr:nth-child(even) {{
            background: #EEF5E8;
        }}

        table.bonsucro-table tbody tr:hover {{
            background: #D8EBCB;
        }}
    </style>
    </head>
    <body>
        <div class="bonsucro-table-wrap">
            {html_table}
        </div>
    </body>
    </html>
    """

    altura_tabla = 120 + len(detalle_df) * 42
    components.html(tabla_detalle_html, height=altura_tabla, scrolling=True)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style="margin-top:48px;border-top:1px solid #9AC864;padding:16px 0;
            display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
    <div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#516E62;letter-spacing:0.1em;">
        🌿 BONSUCRO · SISTEMA DE MONITOREO DE ÁREAS AFECTADAS
    </div>
    <div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#5F8A6E;">
        Ingenio Providenica - 2026
    </div>
</div>
""", unsafe_allow_html=True)