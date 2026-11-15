
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import chi2

from painel import dados

VERMELHO, AZUL, AQUA, CINZA = "#e11d2e", "#2a78d6", "#1baf7a", "#8a8a8a"
VERMELHO_ESCURO = "#9b1021"
GRADE = "rgba(128,128,128,0.22)"
PERIODOS_MAPA = {"Últimos 12 meses": 12, "Últimos 3 anos": 36, "Todo o período (desde 2013)": None}
IND_TAXA, IND_CASOS = "Taxa por 100 mil habitantes", "Número de vítimas"
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

st.set_page_config(page_title="CVLI em Alagoas", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

CSS = """
<style>
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none; }
h1 { color: #e11d2e !important; letter-spacing: -0.5px; margin-bottom: 0; }
.kpi-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 14px; margin: 0.5rem 0 1.2rem; }
.kpi {
  background: rgba(225, 29, 46, 0.07); border-left: 4px solid #e11d2e; border-radius: 10px;
  padding: 0.85rem 1rem; min-height: 122px; display: flex; flex-direction: column; justify-content: space-between;
}
.kpi-r { font-size: 0.85rem; opacity: 0.8; }
.kpi-v { font-size: 2.1rem; font-weight: 600; line-height: 1.1; letter-spacing: -0.5px; }
.kpi-s { font-size: 0.82rem; font-weight: 600; }
.kpi-s.bom { color: #12804a; } .kpi-s.ruim { color: #d41f33; } .kpi-s.neutro { opacity: 0.7; font-weight: 400; }
@media (prefers-color-scheme: dark) { .kpi-s.bom { color: #4cd68b; } .kpi-s.ruim { color: #ff6b7a; } }
.resumo { background: rgba(225, 29, 46, 0.05); border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.6rem; }
.resumo-t { font-weight: 600; margin-bottom: 0.25rem; }
.resumo .lin { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; padding: 0.32rem 0; border-top: 1px solid rgba(128,128,128,0.2); font-size: 0.9rem; }
.resumo .lin span { opacity: 0.85; } .resumo .lin b { white-space: nowrap; }
@media (max-width: 1100px) { .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 520px) { .kpi-grid { grid-template-columns: minmax(0, 1fr); } }
[data-testid="stPopover"] button { border: 1.5px solid #e11d2e; color: #e11d2e; font-weight: 600; }
[data-testid="stPopover"] button:hover { background: #e11d2e; color: #fff; border-color: #e11d2e; }
h2, h3 { letter-spacing: -0.2px; }
.st-key-hero {
  position: relative; border-radius: 20px; overflow: hidden; margin: 0.2rem 0 1.4rem; gap: 0 !important; color: #fff;
  background: radial-gradient(1000px 520px at 76% 45%, rgba(225, 29, 46, 0.26), rgba(225, 29, 46, 0) 70%),
              linear-gradient(135deg, #0f0709 0%, #240c11 55%, #170a0d 100%);
  box-shadow: 0 12px 44px rgba(120, 10, 25, 0.28);
}
@media (min-width: 901px) { .st-key-hero { margin-left: -3.4rem; width: calc(100% + 6.8rem); max-width: none; } }
.st-key-hero h1 { color: #fff !important; font-size: 2.55rem; line-height: 1.08; padding: 0; margin: 0 0 0.2rem; }
.st-key-hero_txt { position: absolute; top: 40px; left: 44px; width: min(27%, 390px); z-index: 4; pointer-events: none; gap: 1.1rem !important; }
.st-key-hero_txt button { pointer-events: auto; background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.55); color: #fff; }
.st-key-hero_txt button p { color: #fff; }
.st-key-hero_txt button:hover { background: #e11d2e; border-color: #e11d2e; color: #fff; }
.st-key-hero_menu { position: absolute; top: 34px; right: 36px; width: 160px; z-index: 6; }
.st-key-hero_menu [data-testid="stPopover"] button { border-color: rgba(255, 255, 255, 0.75); color: #fff; background: rgba(0, 0, 0, 0.25); }
.st-key-hero_menu [data-testid="stPopover"] button:hover { background: #e11d2e; border-color: #e11d2e; }
.st-key-hero_kpis { position: absolute; left: 36px; width: calc(100% - 72px); bottom: 32px; z-index: 4; pointer-events: none; }
.st-key-hero_rank { position: absolute; left: 44px; bottom: 190px; width: min(27%, 390px); z-index: 4; pointer-events: none; }
.hero-rank .rk { display: grid; grid-template-columns: 1.2fr 1fr auto; align-items: center; gap: 10px; font-size: 0.9rem; padding: 0.24rem 0; }
.hero-rank .nm { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: rgba(255, 255, 255, 0.9); }
.hero-rank .bar { height: 7px; border-radius: 4px; background: rgba(255, 255, 255, 0.1); overflow: hidden; }
.hero-rank .bar i { display: block; height: 100%; border-radius: 4px; background: linear-gradient(90deg, #9c1a2b, #ff4d5e); }
.hero-rank b { min-width: 36px; text-align: right; }
.hero-cap { font-size: 0.86rem; color: rgba(255, 255, 255, 0.68); line-height: 1.4; }
.hero-frase { font-size: 1.22rem; line-height: 1.5; color: rgba(255, 255, 255, 0.92); }
.hero-frase b { color: #fff; }
.hero-frase .bom { color: #4cd68b; font-weight: 700; } .hero-frase .ruim { color: #ff6b7a; font-weight: 700; }
.hero-sel { background: rgba(255, 255, 255, 0.07); border-left: 3px solid #ff3b4e; border-radius: 10px; padding: 0.7rem 0.95rem; backdrop-filter: blur(6px); }
.hero-sel .nome { font-size: 1.4rem; font-weight: 700; margin-bottom: 0.3rem; }
.hero-sel .lin { display: flex; justify-content: space-between; gap: 10px; font-size: 0.95rem; padding: 0.2rem 0; border-top: 1px solid rgba(255, 255, 255, 0.14); }
.hero-sel .lin span { color: rgba(255, 255, 255, 0.75); }
.kpi-grid.seis { grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; margin: 0; }
.st-key-hero .kpi { background: rgba(255, 255, 255, 0.07); border-left: 3px solid #ff3b4e; backdrop-filter: blur(6px); min-height: 114px; padding: 0.8rem 1rem; color: #fff; }
.st-key-hero .kpi-r { opacity: 0.78; font-size: 0.84rem; }
.st-key-hero .kpi-v { font-size: 2rem; }
.st-key-hero .kpi-s { font-size: 0.82rem; }
.st-key-hero .kpi-s.bom { color: #4cd68b; } .st-key-hero .kpi-s.ruim { color: #ff6b7a; }
.st-key-hero .kpi-s.neutro { color: rgba(255, 255, 255, 0.72); opacity: 1; }
@media (max-width: 1100px) {
  .st-key-hero_txt { width: min(40%, 420px); }
  .kpi-grid.seis { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 900px) {
  .st-key-hero { display: flex; flex-direction: column; }
  .st-key-hero_txt, .st-key-hero_kpis, .st-key-hero_menu, .st-key-hero_rank { position: static; width: auto; padding: 18px 18px 0; pointer-events: auto; }
  .st-key-hero_menu { width: 150px; padding-bottom: 0; }
  .st-key-hero_kpis { padding-bottom: 18px; }
  .st-key-hero_rank { padding-bottom: 14px; }
  .st-key-hero > div:has(.st-key-hero_menu) { order: -3; align-self: flex-end; }
  .st-key-hero > div:has(.st-key-hero_txt) { order: -2; }
  .st-key-hero > div:has(.st-key-hero_rank) { order: 4; }
  .st-key-hero > div:has(.st-key-hero_kpis) { order: 5; }
  .kpi-grid.seis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
"""


def aplicar_css():
    st.markdown(CSS, unsafe_allow_html=True)


aplicar_css()


# ---------------------------------------------------------------- utilidades
def n(x) -> str:
    return f"{x:,.0f}".replace(",", ".")


def dec(x, casas=1) -> str:
    return f"{x:.{casas}f}".replace(".", ",")


def sinal(x, casas=1) -> str:
    return "–" if pd.isna(x) else f"{x:+.{casas}f}%".replace(".", ",")


def pct_var(novo, antigo):
    return (novo / antigo - 1) * 100 if antigo else np.nan


def ic_poisson(k: int) -> tuple[float, float]:
    lo = chi2.ppf(0.025, 2 * k) / 2 if k > 0 else 0.0
    hi = chi2.ppf(0.975, 2 * (k + 1)) / 2
    return lo, hi


def var_txt(pct):
    if pd.isna(pct):
        return "–", "neutro"
    seta = "▲" if pct > 0 else "▼" if pct < 0 else "■"
    return f"{seta} {dec(abs(pct))}%", ("ruim" if pct > 0 else "bom" if pct < 0 else "neutro")


def cartao(rotulo, valor, sub, tom="neutro", dica=""):
    return (f'<div class="kpi" title="{dica}"><div class="kpi-r">{rotulo}</div><div class="kpi-v">{valor}</div>'
            f'<div class="kpi-s {tom}">{sub}</div></div>')


def resumo(titulo, linhas):
    corpo = "".join(f'<div class="lin"><span>{a}</span><b>{b}</b></div>' for a, b in linhas)
    return f'<div class="resumo"><div class="resumo-t">{titulo}</div>{corpo}</div>'


def data_pt(ts) -> str:
    ts = pd.Timestamp(ts)
    return f"{ts.day:02d}/{ts.month:02d}/{ts.year}"


def estilo(fig, altura=380, legenda=False, hover="x unified"):
    fig.update_layout(
        height=altura, margin=dict(l=4, r=4, t=30, b=4), showlegend=legenda, hovermode=hover,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.1, x=0), bargap=0.25,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor=GRADE, zeroline=False)
    return fig


def tema_escuro() -> bool:
    try:
        return st.context.theme.type == "dark"
    except Exception:
        return False


ESCALA_CALOR = ([[0, "#2b1a1d"], [1, "#ff4d5e"]] if tema_escuro() else [[0, "#fdeaec"], [1, "#a50f1e"]])


def grafico(fig, **kw):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, **kw)


@st.cache_data(ttl=240, show_spinner=False)
def metadados() -> dict:
    return dados.buscar_metadados()


@st.cache_data(show_spinner="Baixando os dados do portal…")
def carregar(url_csv: str, versao: str):
   
    return dados.preparar(dados.baixar_csv(url_csv))


@st.cache_data(show_spinner=False)
def malha():
    return dados.carregar_malha()


@st.cache_data(show_spinner=False)
def referencia():
    return dados.municipios_referencia(dados.carregar_populacao())


@st.cache_data(show_spinner=False)
def populacao():
    return dados.populacao_recente(dados.carregar_populacao())


try:
    meta = metadados()
    df, diag = carregar(meta["url_csv"], meta["atualizado_em"])
except Exception as e:  
    st.error(f"Não foi possível carregar os dados do portal Alagoas em Dados agora. Detalhe: {e}")
    st.stop()

st.session_state["versao_carregada"] = meta["atualizado_em"]


@st.fragment(run_every=300)
def vigia():
    try:
        atual = metadados()["atualizado_em"]
    except Exception:
        return
    if atual != st.session_state.get("versao_carregada"):
        st.rerun(scope="app")


vigia()


hero = st.container(key="hero")
with hero:
    with st.container(key="hero_menu"):
        with st.popover("Filtros", icon=":material/tune:", width="stretch"):
            st.markdown("**Mapa**")
            per_mapa = st.radio("Período do mapa", list(PERIODOS_MAPA), horizontal=True)
            ind_mapa = st.radio("Cor dos municípios", [IND_TAXA, IND_CASOS], horizontal=True,
                                help="A taxa divide as vítimas pela população, o que permite comparar cidades de tamanhos diferentes.")
            st.markdown("**Gráficos abaixo do mapa**")
            ano_min, ano_max = int(df["ano"].min()), int(df["ano"].max())
            ini, fim = st.slider("Anos", ano_min, ano_max, (2013, ano_max))
            rank_mun = df["municipio"].value_counts().index.tolist()
            sel_mun = st.multiselect("Municípios", rank_mun, placeholder="Todos")
            sel_sexo = st.multiselect("Sexo da vítima", sorted(df["sexo"].unique()), default=sorted(df["sexo"].unique()))
            sel_instr = st.multiselect("Instrumento", df["instrumento"].value_counts().index.tolist(),
                                       default=df["instrumento"].value_counts().index.tolist())
            sel_per = st.multiselect("Período do dia", dados.PERIODOS, default=dados.PERIODOS,
                                     help="Só considera registros com hora informada.")
            st.divider()
            if st.button("Verificar atualização dos dados", width="stretch"):
                metadados.clear()
                st.rerun()

mapbase = df[df["sexo"].isin(sel_sexo) & df["instrumento"].isin(sel_instr)]
if set(sel_per) != set(dados.PERIODOS):
    mapbase = mapbase[mapbase["periodo"].isin(sel_per)]
base = mapbase[mapbase["municipio"].isin(sel_mun)] if sel_mun else mapbase
f = base[base["ano"].between(ini, fim)]

ultima = df["data"].max()
mes_fim = ultima.to_period("M")
parcial = ultima.day < ultima.days_in_month - 2 
mes_ref = mes_fim - 1 if parcial else mes_fim           
j12 = (mes_ref - 11, mes_ref)
j12_ant = (mes_ref - 23, mes_ref - 12)
mes_p = base["data"].dt.to_period("M")
c12 = base[mes_p.between(*j12)]
c12_ant = base[mes_p.between(*j12_ant)]
rotulo_j12 = f"{MESES[j12[0].month - 1]}/{j12[0].year} a {MESES[j12[1].month - 1]}/{j12[1].year}"

if f.empty:
    st.warning("Nenhum registro com esses filtros.")
    st.stop()


# ---------------------------------------------------------------- números do topo
ref = referencia()
usa_taxa = ind_mapa == IND_TAXA
v12, v12a = len(c12), len(c12_ant)
mes_atual = base[mes_p == mes_ref]
mes_ant = base[mes_p == mes_ref - 12]
base13 = int((base["ano"] == 2013).sum())
fem12, fem12a = int(c12["feminicidio"].sum()), int(c12_ant["feminicidio"].sum())
mp = mapbase["data"].dt.to_period("M")
if ref is not None:
    chaves_escolhidas = set(df.loc[df["municipio"].isin(sel_mun), "chave"]) if sel_mun else set(ref["chave"])
    pop_escolhida = ref.loc[ref["chave"].isin(chaves_escolhidas), "populacao"].sum()
    taxa12 = v12 / pop_escolhida * 1e5 if pop_escolhida else np.nan
    r12 = ref.copy()                              # maior taxa em 12 meses (municípios de 20 mil hab. ou mais)
    r12["casos"] = r12["chave"].map(mapbase[(mp >= j12[0]) & (mp <= j12[1])].groupby("chave").size()).fillna(0)
    r12["taxa"] = r12["casos"] / r12["populacao"] * 1e5
    topo_taxa = r12[r12["populacao"] >= 20000].sort_values("taxa", ascending=False).iloc[0]
else:
    taxa12, topo_taxa = np.nan, None

p1, p13 = pct_var(v12, v12a), pct_var(v12, base13)
t1, c1 = var_txt(p1)
t2, c2 = var_txt(pct_var(len(mes_atual), len(mes_ant)))
dfem = fem12 - fem12a
mes_rot = f"{MESES[mes_ref.month - 1].capitalize()}/{mes_ref.year}"
cartoes = [
    cartao("Vítimas · 12 meses", n(v12), f"{t1} vs 12 meses antes", c1, f"Período: {rotulo_j12}. Os filtros do menu valem, exceto o de anos."),
    cartao(mes_rot, n(len(mes_atual)), f"{t2} vs {MESES[mes_ref.month - 1]}/{mes_ref.year - 1}", c2, "Último mês completo da base."),
    cartao("Taxa em Alagoas" if not sel_mun else "Taxa escolhida", "–" if pd.isna(taxa12) else dec(taxa12),
           "por 100 mil hab. · 12 meses", "neutro", "Vítimas dos últimos 12 meses divididas pela população (IBGE, 2025)."),
    cartao("Em relação a 2013", sinal(p13), f"{n(base13)} em 2013 → {n(v12)}", "neutro",
           "Últimos 12 meses contra o total de 2013, primeiro ano da série comparável."),
    cartao("Feminicídios · 12 meses", n(fem12), f"{'▲' if dfem > 0 else '▼' if dfem < 0 else '■'} {abs(dfem)} vs 12 meses antes",
           "ruim" if dfem > 0 else "bom" if dfem < 0 else "neutro", "Casos classificados como feminicídio."),
    cartao("Maior taxa · 12 meses", "–" if topo_taxa is None else dec(topo_taxa["taxa"]),
           "–" if topo_taxa is None else topo_taxa["municipio"], "neutro", "Entre os municípios com 20 mil habitantes ou mais."),
]

sujeito = "Alagoas registrou" if not sel_mun else "os municípios escolhidos registraram"


def frase_var(pc, quando):
    if pd.isna(pc):
        return ""
    return f'<span class="{"bom" if pc < 0 else "ruim"}">{dec(abs(pc))}% {"menos" if pc < 0 else "mais"}</span> {quando}'


frase = (f"Em <b>12 meses</b> ({rotulo_j12}), {sujeito} <b>{n(v12)} vítimas</b> de crimes violentos letais: "
         f"{frase_var(p1, 'que nos 12 meses anteriores')} e {frase_var(p13, 'que em 2013')}.")

# ---------------------------------------------------------------- dados do mapa
m = None
if ref is not None:
    meses_mapa = PERIODOS_MAPA[per_mapa]
    ini_mapa = mes_ref - (meses_mapa - 1) if meses_mapa else pd.Period("2013-01", "M")
    no_periodo = mapbase[(mp >= ini_mapa) & (mp <= mes_ref)]
    anos_periodo = ((mes_ref - ini_mapa).n + 1) / 12

    m = ref.copy()
    m["casos"] = m["chave"].map(no_periodo.groupby("chave").size()).fillna(0).astype(int)
    m["taxa"] = m["casos"] / anos_periodo / m["populacao"] * 1e5
    m["valor"] = m["taxa"] if usa_taxa else m["casos"]
    ics = [ic_poisson(k) for k in m["casos"]]
    m["ic_lo"] = [lo / anos_periodo / pop * 1e5 for (lo, _), pop in zip(ics, m["populacao"])]
    m["ic_hi"] = [hi / anos_periodo / pop * 1e5 for (_, hi), pop in zip(ics, m["populacao"])]
    # taxa instável: a metade do intervalo de confiança passa de 50% da própria contagem (≈ menos de 16 casos)
    m["instavel"] = [(hi - lo) / 2 > 0.5 * k for k, (lo, hi) in zip(m["casos"], ics)]
    positivos = m.loc[m["valor"] > 0, "valor"]
    zmax = float(np.percentile(positivos, 95)) if len(positivos) else 1.0
    un = "por 100 mil hab./ano" if usa_taxa else "vítimas"

    def texto(r):
        t = f"<b>{r.municipio}</b><br>{n(r.casos)} vítimas no período<br>{dec(r.taxa)} por 100 mil hab./ano"
        if r.casos > 0:
            t += f"<br>IC 95%: {dec(r.ic_lo)} a {dec(r.ic_hi)}"
        t += f"<br>{n(r.populacao)} habitantes"
        if r.casos > 0 and r.instavel:
            t += "<br><i>poucos casos: a taxa é instável</i>"
        if r.populacao < 20000:
            t += f"<br><i>município pequeno: 1 vítima a mais soma {dec(1 / anos_periodo / r.populacao * 1e5)}</i>"
        return t

    m["texto"] = [texto(r) for r in m.itertuples()]

# ================================================================ BLOCO DE ABERTURA: mapa em tela cheia
st.session_state.setdefault("mapa_k", 0)
escolhido = None
try:
    ua = st.context.headers.get("User-Agent", "").lower()
except Exception:
    ua = ""
movel = any(k in ua for k in ("mobi", "android", "iphone"))
with hero:
    if m is None:
        st.info("O mapa precisa do arquivo de população (dados_brutos/populacao_municipios_AL.csv). Rode o notebook 03 para gerá-lo.")
    else:
        # o bloco de abertura é escuro nos dois temas: escala própria, legível sobre fundo escuro
        escala = [[0, "#3d2428"], [0.35, "#9c1a2b"], [0.7, "#e11d2e"], [1, "#ff6272"]]
        mapa_fig = go.Figure(go.Choropleth(
            geojson=malha(), locations=m["cod_ibge"], featureidkey="properties.codarea", z=m["valor"],
            zmin=0, zmax=zmax, colorscale=escala, text=m["texto"], hovertemplate="%{text}<extra></extra>",
            marker_line_color="rgba(15,7,9,0.95)", marker_line_width=0.8,
            selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=0.5)),
            colorbar=dict(orientation="h", x=0.865, xanchor="center", y=0.27, yanchor="middle", len=0.24, thickness=11,
                          title=dict(text=f"{'Taxa' if usa_taxa else 'Vítimas'} ({un})<br>cor máxima a partir de {dec(zmax, 0)}",
                                     side="top", font=dict(color="#f1e7e8", size=11)),
                          tickfont=dict(color="#f1e7e8", size=10), outlinewidth=0),
        ))
        if sel_mun:                                   # contorno forte nos municípios escolhidos no menu
            marcados = m[m["chave"].isin(base["chave"].unique())]
            mapa_fig.add_trace(go.Choropleth(
                geojson=malha(), locations=marcados["cod_ibge"], featureidkey="properties.codarea", z=[1] * len(marcados),
                colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], showscale=False, hoverinfo="skip",
                marker_line_color="#ffffff", marker_line_width=3))
        if movel:      # celular: o estado ocupa a largura toda e a legenda vai para baixo
            lon_r, lat_r, altura = [-38.45, -35.0], [-10.75, -8.6], 300
            mapa_fig.update_traces(colorbar=dict(x=0.5, xanchor="center", y=0.02, yanchor="bottom", len=0.7))
        else:          # janela fixa: o estado ocupa a parte direita e deixa o lado esquerdo livre para o texto
            lon_r, lat_r, altura = [-39.75, -34.95], [-11.30, -8.40], 840
        mapa_fig.update_geos(projection_type="mercator", lonaxis_range=lon_r, lataxis_range=lat_r,
                             visible=False, bgcolor="rgba(0,0,0,0)")
        mapa_fig.update_layout(height=altura, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)",
                               geo_bgcolor="rgba(0,0,0,0)", dragmode="turntable",
                               hoverlabel=dict(bgcolor="#1c0d10", bordercolor="#ff4d5e", font=dict(color="#ffffff", size=12)))
        evento = st.plotly_chart(mapa_fig, width="stretch", key=f"mapa_{st.session_state['mapa_k']}",
                                 config={"displayModeBar": False, "scrollZoom": False},
                                 on_select="rerun", selection_mode="points")
        pts = [pt for pt in (evento.selection.points if evento else []) if pt.get("curve_number", 0) == 0]
        if pts:
            escolhido = m.iloc[pts[0]["point_index"]]

    with st.container(key="hero_txt"):
        st.title("Crimes violentos letais em Alagoas")
        st.markdown(f'<div class="hero-cap">Secretaria de Segurança Pública de Alagoas, via portal Alagoas em Dados · '
                    f'dados até <b>{data_pt(ultima)}</b> · publicado em <b>{data_pt(meta["atualizado_em"][:10])}</b></div>',
                    unsafe_allow_html=True)
        if escolhido is not None:
            ic = f"{dec(escolhido['ic_lo'])} a {dec(escolhido['ic_hi'])}" if escolhido["casos"] else "–"
            st.markdown(
                f'<div class="hero-sel"><div class="nome">{escolhido["municipio"]}</div>'
                f'<div class="lin"><span>Vítimas no período</span><b>{n(escolhido["casos"])}</b></div>'
                f'<div class="lin"><span>Taxa por 100 mil hab./ano</span><b>{dec(escolhido["taxa"])}</b></div>'
                f'<div class="lin"><span>Intervalo de confiança de 95%</span><b>{ic}</b></div>'
                f'<div class="lin"><span>População (IBGE)</span><b>{n(escolhido["populacao"])}</b></div></div>',
                unsafe_allow_html=True)
            if st.button("Limpar seleção", width="stretch"):
                st.session_state["mapa_k"] += 1
                st.rerun()
        else:
            st.markdown(f'<div class="hero-frase">{frase}</div>', unsafe_allow_html=True)
            st.markdown('<div class="hero-cap">Clique em um município do mapa para ver os detalhes.</div>', unsafe_allow_html=True)

    if m is not None:
        with st.container(key="hero_rank"):
            if usa_taxa:                              # mostra a medida contrária à da cor do mapa
                alt, col, tit, fmt = m.sort_values("casos", ascending=False).head(5), "casos", "Mais vítimas", n
            else:
                alt = m[m["populacao"] >= 20000].sort_values("taxa", ascending=False).head(5)
                col, tit, fmt = "taxa", "Maiores taxas (20 mil hab. ou mais)", dec
            vmax = float(alt[col].max()) or 1.0
            linhas = "".join(
                f'<div class="rk"><span class="nm">{r.municipio}</span><div class="bar"><i style="width:{getattr(r, col) / vmax * 100:.0f}%"></i></div>'
                f'<b>{fmt(getattr(r, col))}</b></div>' for r in alt.itertuples())
            st.markdown(f'<div class="hero-rank"><div class="hero-cap" style="margin-bottom:0.35rem">{tit} · {per_mapa.lower()}</div>{linhas}</div>',
                        unsafe_allow_html=True)

    with st.container(key="hero_kpis"):
        st.markdown('<div class="kpi-grid seis">' + "".join(cartoes) + "</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------- faixa logo abaixo do mapa
if m is not None:
    cA, cB, cC = st.columns([1, 1.15, 1.25], gap="large")
    with cA:
        taxa_al = m["casos"].sum() / anos_periodo / m["populacao"].sum() * 1e5
        top5 = m["casos"].nlargest(5).sum() / max(m["casos"].sum(), 1) * 100
        st.markdown(resumo(f"Resumo do mapa · {per_mapa.lower()}", [
            ("Taxa de Alagoas (por 100 mil hab./ano)", dec(taxa_al)),
            ("Taxa mediana dos municípios", dec(m["taxa"].median())),
            ("Municípios sem nenhuma vítima", f"{int((m['casos'] == 0).sum())} de {len(m)}"),
            ("Os 5 municípios com mais vítimas somam", f"{dec(top5, 0)}%"),
        ]), unsafe_allow_html=True)
        st.caption(f"Período: {MESES[ini_mapa.month - 1]}/{ini_mapa.year} a {MESES[mes_ref.month - 1]}/{mes_ref.year}. "
                   "Quanto mais vermelho, maior o valor. A escala de cor é limitada ao percentil 95 dos municípios. "
                   "Populações do IBGE (2025).")
    with cB:
        st.markdown("**Maiores taxas**" if usa_taxa else "**Mais vítimas**")
        rk = m[m["populacao"] >= 20000] if usa_taxa else m
        rk = rk.sort_values("valor", ascending=False).head(8).iloc[::-1]
        fig = go.Figure(go.Bar(x=rk["valor"], y=rk["municipio"], orientation="h", marker_color=VERMELHO,
                               customdata=rk["casos"], hovertemplate="%{y}: %{x:.1f} (" + un + ")<br>%{customdata} vítimas<extra></extra>"))
        grafico(estilo(fig, 290, hover="closest"))
        st.caption("Ranking só com municípios de 20 mil habitantes ou mais, onde a taxa é mais estável." if usa_taxa else "Ranking em número de vítimas.")
    with cC:
        alvo = mapbase if escolhido is None else mapbase[mapbase["chave"] == escolhido["chave"]]
        nome_alvo = "Alagoas" if escolhido is None else escolhido["municipio"]
        st.markdown(f"**Vítimas por ano · {nome_alvo}**")
        serie = alvo.groupby("ano").size().reindex(range(2013, ano_max + 1), fill_value=0)
        parcial_ano = ultima < pd.Timestamp(year=ultima.year, month=12, day=31)
        cores = [VERMELHO if not (parcial_ano and a == ultima.year) else "rgba(225,29,46,0.45)" for a in serie.index]
        figm = go.Figure(go.Bar(x=serie.index, y=serie.values, marker_color=cores,
                                hovertemplate="%{x}: %{y} vítimas<extra></extra>"))
        figm.update_xaxes(dtick=1)
        grafico(estilo(figm, 290, hover="closest"))
        st.caption(f"{ultima.year} é parcial (dados até {data_pt(ultima)}), por isso a última barra é mais clara."
                   if parcial_ano else "Total de vítimas em cada ano.")

st.subheader("Mais análises")

aba1, aba2, aba3, aba4, aba5 = st.tabs(["Evolução", "Municípios", "Quando e onde", "Perfil das vítimas", "Dados e método"])


with aba1:
    st.subheader("Vítimas por mês")
    mensal = base.groupby("mes").size().rename("n")
    meses = pd.date_range(base["mes"].min(), base["mes"].max(), freq="MS")
    mensal = mensal.reindex(meses, fill_value=0)
    if parcial:
        mensal = mensal.iloc[:-1]                              
    media12 = mensal.rolling(12).mean()
    corte = mensal.index >= pd.Timestamp(year=ini, month=1, day=1)
    corte &= mensal.index <= pd.Timestamp(year=fim, month=12, day=31)
    fig = go.Figure()
    fig.add_scatter(x=mensal.index[corte], y=mensal[corte], name="Mês", mode="lines",
                    line=dict(color=CINZA, width=1.2), hovertemplate="%{y} vítimas")
    fig.add_scatter(x=media12.index[corte], y=media12[corte], name="Média móvel de 12 meses", mode="lines",
                    line=dict(color=VERMELHO, width=2.5), hovertemplate="%{y:.0f} por mês")
    grafico(estilo(fig, legenda=True))
    if parcial:
        st.caption(f"O mês de {MESES[mes_fim.month - 1]}/{mes_fim.year} ainda está incompleto (dados até {data_pt(ultima)}) e não aparece.")

    st.subheader("Vítimas por ano")
    anual = f.groupby("ano").size()
    ano_parcial = ultima.year if ultima < pd.Timestamp(year=ultima.year, month=12, day=31) else None
    cores = [VERMELHO if a != ano_parcial else "rgba(225,29,46,0.45)" for a in anual.index]
    fig = go.Figure(go.Bar(x=anual.index, y=anual.values, marker_color=cores, hovertemplate="%{x}: %{y} vítimas<extra></extra>"))
    fig.update_xaxes(dtick=1)
    grafico(estilo(fig, 320, hover="closest"))
    if ano_parcial in anual.index:
        st.caption(f"{ano_parcial} é um ano parcial (dados até {data_pt(ultima)}), por isso a barra é mais clara.")


with aba2:
    pop = populacao()
    tab = pd.DataFrame({"casos_periodo": f.groupby("municipio").size(),
                        "casos_12m": c12.groupby("municipio").size(),
                        "casos_12m_ant": c12_ant.groupby("municipio").size()}).fillna(0).astype(int)
    tab["variacao_%"] = [pct_var(a, b) if b >= 5 else np.nan for a, b in zip(tab["casos_12m"], tab["casos_12m_ant"])]
    chave = base.drop_duplicates("municipio").set_index("municipio")["chave"]
    tab["chave"] = chave.reindex(tab.index)
    if pop is not None:
        tab = tab.merge(pop, on="chave", how="left").set_index(tab.index)
        tab["taxa_12m"] = tab["casos_12m"] / tab["pop"] * 1e5

    cA, cB = st.columns(2)
    with cA:
        st.subheader(f"Maiores números, {ini}–{fim}")
        top = tab.sort_values("casos_periodo", ascending=False).head(15).iloc[::-1]
        fig = go.Figure(go.Bar(x=top["casos_periodo"], y=top.index, orientation="h", marker_color=VERMELHO,
                               hovertemplate="%{y}: %{x} vítimas<extra></extra>"))
        grafico(estilo(fig, 460, hover="closest"))
    with cB:
        if pop is not None:
            st.subheader("Maiores taxas, últimos 12 meses")
            ok = tab[tab["pop"] >= 20000].sort_values("taxa_12m", ascending=False).head(15).iloc[::-1]
            fig = go.Figure(go.Bar(x=ok["taxa_12m"], y=ok.index, orientation="h", marker_color=VERMELHO_ESCURO,
                                   customdata=np.c_[ok["casos_12m"], ok["pop"]],
                                   hovertemplate="%{y}: %{x:.1f} por 100 mil<br>%{customdata[0]} vítimas, %{customdata[1]:,.0f} hab.<extra></extra>"))
            grafico(estilo(fig, 460, hover="closest"))
            st.caption("Só municípios com 20 mil habitantes ou mais, porque em cidade pequena poucos casos mudam muito a taxa. "
                       "População: última estimativa do IBGE disponível (2025, base do Censo 2022).")
        else:
            st.info("Arquivo de população não encontrado (dados_brutos/populacao_municipios_AL.csv). Rode o notebook 03 para gerá-lo.")

    st.subheader("Todos os municípios")
    mostra = tab.drop(columns=["chave", "ano_pop"], errors="ignore").rename(columns={
        "casos_periodo": f"Vítimas {ini}–{fim}", "casos_12m": "Últimos 12 meses", "casos_12m_ant": "12 meses anteriores",
        "variacao_%": "Variação %", "pop": "População", "taxa_12m": "Taxa por 100 mil (12 meses)"})
    st.dataframe(mostra.sort_values(mostra.columns[0], ascending=False).round(1), width="stretch", height=360,
                 column_config={"População": st.column_config.NumberColumn(format="%d")})
    st.caption("Variação só é calculada quando havia pelo menos 5 casos nos 12 meses anteriores.")


with aba3:
    cA, cB = st.columns(2)
    com_hora = f.dropna(subset=["hora"])
    with cA:
        st.subheader("Por hora do dia")
        horas = com_hora.groupby("hora").size().reindex(range(24), fill_value=0)
        noite = horas.loc[18:23].sum() / horas.sum() * 100
        fig = go.Figure(go.Bar(x=horas.index, y=horas.values, marker_color=VERMELHO,
                               hovertemplate="%{x}h: %{y} vítimas<extra></extra>"))
        fig.update_xaxes(dtick=2, ticksuffix="h")
        grafico(estilo(fig, 340, hover="closest"))
        st.caption(f"Entre 18h e 23h ocorrem **{dec(noite)}%** dos casos com hora informada (25% se o horário fosse indiferente).")
    with cB:
        st.subheader("Dia da semana e hora")
        mapa = pd.crosstab(com_hora["dia_semana"], com_hora["hora"]).reindex(index=dados.DIAS, columns=range(24), fill_value=0)
        fig = go.Figure(go.Heatmap(z=mapa.values, x=[f"{h}h" for h in mapa.columns], y=dados.DIAS,
                                   colorscale=ESCALA_CALOR, showscale=False,
                                   hovertemplate="%{y}, %{x}: %{z} vítimas<extra></extra>"))
        fig.update_yaxes(autorange="reversed")
        fig.update_xaxes(dtick=3)
        grafico(estilo(fig, 340, hover="closest"))

    st.subheader("Local do fato")
    loc = f["local"].value_counts(normalize=True).mul(100).iloc[::-1]
    fig = go.Figure(go.Bar(x=loc.values, y=loc.index, orientation="h", marker_color=VERMELHO,
                           hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
    fig.update_xaxes(ticksuffix="%")
    grafico(estilo(fig, 320, hover="closest"))
    st.caption("O campo original é texto livre; as grafias foram agrupadas em categorias (regra do notebook 02).")

with aba4:
    cA, cB = st.columns(2)
    with cA:
        st.subheader("Faixa etária ao longo dos anos")
        conhecida = base[base["faixa"].notna()]
        part = (pd.crosstab(conhecida["ano"], conhecida["faixa"], normalize="index") * 100)
        part = part.loc[(part.index >= ini) & (part.index <= fim)]
        fig = go.Figure()
        for faixa, cor in zip(["12–17", "18–24", "25–34"], [VERMELHO, AZUL, AQUA]):
            fig.add_scatter(x=part.index, y=part[faixa], name=faixa, mode="lines+markers", line=dict(color=cor, width=2),
                            marker=dict(size=7), hovertemplate="%{y:.1f}%")
        fig.update_xaxes(dtick=1)
        fig.update_yaxes(ticksuffix="%")
        grafico(estilo(fig, 340, legenda=True))
        st.caption("Participação entre as vítimas com idade informada.")
    with cB:
        st.subheader("Mulheres e feminicídios por ano")
        fem = f.groupby("ano").agg(mulheres=("sexo", lambda s: (s == "Feminino").sum()), feminicidios=("feminicidio", "sum"))
        fig = go.Figure()
        fig.add_bar(x=fem.index, y=fem["mulheres"], name="Mulheres vítimas", marker_color=AZUL)
        fig.add_bar(x=fem.index, y=fem["feminicidios"], name="Feminicídios classificados", marker_color=VERMELHO)
        fig.update_layout(barmode="group")
        fig.update_xaxes(dtick=1)
        grafico(estilo(fig, 340, legenda=True))
        st.caption("A classificação de feminicídio só existe a partir de 2015 (Lei 13.104/2015); antes, entra como homicídio.")

    cC, cD = st.columns(2)
    with cC:
        st.subheader("Instrumento")
        ins = f["instrumento"].value_counts(normalize=True).mul(100).iloc[::-1]
        fig = go.Figure(go.Bar(x=ins.values, y=ins.index, orientation="h", marker_color=VERMELHO,
                               hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
        fig.update_xaxes(ticksuffix="%")
        grafico(estilo(fig, 300, hover="closest"))
    with cD:
        st.subheader("Idade das vítimas")
        idade = f["idade"].dropna()
        fig = go.Figure(go.Histogram(x=idade, xbins=dict(start=0, end=105, size=2), marker_color=VERMELHO,
                                     hovertemplate="%{x} anos: %{y}<extra></extra>"))
        fig.update_xaxes(title_text="idade (anos)")
        grafico(estilo(fig, 300, hover="closest"))
        st.caption(f"Mediana {dec(idade.median(), 0)} anos; metade das vítimas tem entre {dec(idade.quantile(.25), 0)} e {dec(idade.quantile(.75), 0)} anos.")

with aba5:
    st.subheader("Fonte")
    st.markdown(
        f"- **Dataset:** [{meta['titulo']}]({meta['pagina']}) (portal Alagoas em Dados, CKAN)\n"
        f"- **Arquivo:** {meta['recurso']}\n"
        f"- **Atualizado pelo portal em:** {data_pt(meta['atualizado_em'][:10])} · **dados até:** {data_pt(ultima)}\n"
        f"- **Registros:** {n(diag['linhas_usadas'])} de {n(diag['linhas_arquivo'])} no arquivo "
        f"({diag['sem_data_valida']} sem data válida, {diag['ids_duplicados']} IDs duplicados, {diag['datas_futuras']} datas futuras)"
    )
    st.subheader("Como os dados chegam aqui")
    st.markdown(
        "A página consulta a **API CKAN** do portal (`package_show`) para descobrir o arquivo mais recente e a data da última "
        "publicação. Quando essa data muda, os dados são baixados de novo; a cada 5 minutos a página confere se houve novidade. "
        "O portal publica em lotes (não em tempo real), então \"ao vivo\" aqui significa *sempre a versão mais recente publicada*.\n\n"
        "**Atenção às datas.** O `datastore_search` do portal lê `DATA DO FATO` com **mês e dia trocados** quando o dia é 12 ou "
        "menos (03/01/2012 vira 2012-03-01). Por isso as datas são lidas do texto original do CSV do mesmo recurso. "
        "Os anos não são afetados, mas análises mensais ou diárias feitas direto no datastore saem erradas."
    )
    st.subheader("Limitações")
    st.markdown(
        "- A base é um registro de ocorrências de CVLI, sem população; as taxas usam estimativas do IBGE (2023 interpolado; "
        "as estimativas até 2021 partem do Censo 2010 e há uma quebra de série em 2022).\n"
        "- Escolaridade e ocupação têm mais de 65% de ausência e não são usadas.\n"
        "- Mortes ainda em apuração podem ser reclassificadas pelo órgão, então números recentes podem mudar."
    )
    st.download_button("Baixar os dados filtrados (CSV)", f.drop(columns=["chave"]).to_csv(index=False).encode("utf-8-sig"),
                       file_name="cvli_filtrado.csv", mime="text/csv")
