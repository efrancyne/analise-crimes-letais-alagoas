"""Gera os 5 gráficos usados nos slides da apresentação do artigo.

Usa o mesmo recorte do artigo (2013 a 2025) e o mesmo visual escuro do painel
(fundo vinho escuro, vermelho #e11d2e).

Como rodar, da raiz do projeto:

    pip install -r requirements.txt
    python apresentacao/graficos_slides.py

Entradas (mesmas dos notebooks):
    dados_brutos/cvli_dados.csv               microdados de CVLI da SSP-AL (Alagoas em Dados)
    dados_brutos/populacao_municipios_AL.csv  população do IBGE, gerada pelo notebook 03

Saída: apresentacao/graficos/*.png. Os números principais também saem no terminal,
para conferir com o texto do artigo.
"""
import argparse
import re
import unicodedata
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")  # gera arquivos sem abrir janela
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent.parent

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("--base", default=RAIZ / "dados_brutos" / "cvli_dados.csv", type=Path)
parser.add_argument("--pop", default=RAIZ / "dados_brutos" / "populacao_municipios_AL.csv", type=Path)
parser.add_argument("--saida", default=RAIZ / "apresentacao" / "graficos", type=Path)
args = parser.parse_args()
args.saida.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- visual
BG = "#1a0c10"; FG = "#f3e9eb"; MUTED = "#b7a3a8"; GRID = "#3a2329"
RED = "#e11d2e"; RED2 = "#ff6b78"; DIM = "#6b3a44"
plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "text.color": FG, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": GRID, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.alpha": 0.8, "axes.axisbelow": True,
    "font.size": 15, "font.family": "DejaVu Sans",
})


def br(valor, casas=1, sufixo=""):
    """Formata número com vírgula decimal (padrão brasileiro)."""
    return f"{valor:.{casas}f}{sufixo}".replace(".", ",")


def chave(nome):
    """Nome de município sem acento, espaço ou caixa, para juntar CVLI e IBGE."""
    s = unicodedata.normalize("NFKD", str(nome)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def salvar(nome):
    plt.tight_layout()
    plt.savefig(args.saida / nome, dpi=150)
    plt.close()
    print("  salvo:", nome)


# ---------------------------------------------------------------- dados
df = pd.read_csv(args.base)
df["DATA DO FATO"] = pd.to_datetime(df["DATA DO FATO"], dayfirst=True)
df["ANO"] = df["DATA DO FATO"].dt.year
df = df[df["ANO"].between(2013, 2025)].copy()
df["chave"] = df["CIDADE DO FATO"].map(chave)
df["HORA"] = pd.to_numeric(df["HORA DO FATO"].str[:2], errors="coerce")

pop = pd.read_csv(args.pop, encoding="utf-8-sig")
pop["chave"] = pop["municipio"].map(chave)
print("Vítimas 2013-2025:", len(df))

# Grade município x ano com população; ano sem vítima entra com zero casos.
casos = df.groupby(["chave", "ANO"]).size().rename("casos")
grade = pop.set_index(["chave", "ano"])[["municipio", "populacao"]]
grade.index.names = ["chave", "ANO"]
mun = grade.join(casos).fillna({"casos": 0}).reset_index()
nome = mun.drop_duplicates("chave").set_index("chave").municipio

# ---------------------------------------------------------------- 1. casos e taxa por ano
est = mun.groupby("ANO").agg(casos=("casos", "sum"), pop=("populacao", "sum"))
est["taxa"] = est.casos / est["pop"] * 1e5
print("\n1. Vítimas e taxa por 100 mil hab.")
print(est[["casos", "taxa"]].round(1).to_string())

fig, ax = plt.subplots(figsize=(12, 5.6))
ax.bar(est.index, est.casos, color=DIM, width=0.7, label="Vítimas (número)")
ax.set_ylabel("Vítimas"); ax.set_xticks(est.index); ax.tick_params(axis="x", labelsize=12)
ax.set_ylim(0, 2600)
ax2 = ax.twinx()  # segundo eixo: a taxa tem outra escala
ax2.plot(est.index, est.taxa, color=RED, lw=3.5, marker="o", ms=8, label="Taxa por 100 mil hab.")
ax2.set_ylim(0, 80); ax2.set_ylabel("Taxa por 100 mil hab.", color=RED)
ax2.tick_params(axis="y", colors=RED); ax2.grid(False)
ax2.spines["right"].set_visible(True); ax2.spines["right"].set_color(GRID)
for ano in (2013, 2025):
    ax2.annotate(br(est.taxa[ano]), (ano, est.taxa[ano]), textcoords="offset points",
                 xytext=(0, 14), ha="center", color=RED2, fontsize=15, fontweight="bold")
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper right", frameon=False, labelcolor=FG)
salvar("g1_casos_taxa.png")

# ---------------------------------------------------------------- 2. variação por município
# Triênios (2013-15 x 2023-25) e só municípios com >= 150 vítimas no período,
# para a taxa não oscilar por acaso em cidades com poucos casos.
def taxa_periodo(inicio, fim):
    s = mun[mun.ANO.between(inicio, fim)].groupby("chave").agg(c=("casos", "sum"), p=("populacao", "sum"))
    return s.c / s.p * 1e5


total = mun.groupby("chave").casos.sum()
grandes = total[total >= 150].index
t1, t2 = taxa_periodo(2013, 2015), taxa_periodo(2023, 2025)
var = ((t2[grandes] / t1[grandes] - 1) * 100).sort_values(ascending=False)
var.index = nome[var.index]
ini =mun[mun.ANO.between(2013, 2015)]; fim = mun[mun.ANO.between(2023, 2025)]
estado = (fim.casos.sum() / fim.populacao.sum()) / (ini.casos.sum() / ini.populacao.sum()) * 100 - 100
print(f"\n2. Municípios com >= 150 vítimas: {len(var)}; variação do estado: {estado:.1f}%")
print(var.round(1).to_string())

fig, ax = plt.subplots(figsize=(10, 9.6))
ax.barh(var.index, var.values, color=[RED2 if v > estado else RED for v in var.values], height=0.72)
ax.axvline(estado, color=FG, ls="--", lw=1.5)
ax.text(estado - 1, -1.1, "Alagoas " + br(estado, sufixo="%"), color=FG, fontsize=12, ha="right")
for i, v in enumerate(var.values):
    ax.text(v + 0.8, i, br(v, sufixo="%"), va="center", ha="left", fontsize=11, color=BG, fontweight="bold")
ax.set_xlim(-80, 0); ax.tick_params(axis="y", labelsize=12.5, colors=FG); ax.grid(axis="y", visible=False)
ax.set_xlabel("Variação da taxa, 2013–15 → 2023–25 (%)")
salvar("g2_variacao_municipios.png")

# ---------------------------------------------------------------- 3. total x mulheres
g = df.groupby("ANO").agg(total=("ID_CONTROLE", "size"),
                          mulheres=("SEXO DA VITIMA", lambda s: (s == "Feminino").sum()))
idx = g / g.iloc[0] * 100  # índice: 2013 = 100
print("\n3. Vítimas por ano (total e mulheres)")
print(g.to_string())

fig, ax = plt.subplots(figsize=(12, 5.6))
ax.plot(idx.index, idx.total, color=MUTED, lw=3, marker="o", label="Todas as vítimas")
ax.plot(idx.index, idx.mulheres, color=RED, lw=3.5, marker="o", label="Mulheres")
for col, cor in (("total", MUTED), ("mulheres", RED2)):
    ax.annotate(f"{idx[col].iloc[-1]:.0f}", (idx.index[-1], idx[col].iloc[-1]), xytext=(10, 0),
                textcoords="offset points", color=cor, fontsize=15, fontweight="bold", va="center")
ax.set_ylim(30, 110); ax.set_xticks(idx.index); ax.tick_params(axis="x", labelsize=12)
ax.set_ylabel("Índice (2013 = 100)"); ax.legend(frameon=False, labelcolor=FG, loc="upper right")
salvar("g3_mulheres.png")

# ---------------------------------------------------------------- 4. hora do dia
h = df.dropna(subset=["HORA"])
por_hora = h.HORA.astype(int).value_counts().sort_index()
noite = h.HORA.between(18, 23).mean() * 100
print(f"\n4. Vítimas entre 18h e 23h: {noite:.1f}% (de {len(h)} com hora preenchida)")

fig, ax = plt.subplots(figsize=(12, 5.4))
ax.bar(por_hora.index, por_hora.values, width=0.8,
       color=[RED if 18 <= x <= 23 else DIM for x in por_hora.index])
ax.set_xticks(range(0, 24, 2)); ax.set_xlabel("Hora do dia"); ax.set_ylabel("Vítimas (2013–2025)")
ax.text(20.5, por_hora.max() * 1.02, "noite: " + br(noite, sufixo="%"), color=RED2, ha="center",
        fontsize=16, fontweight="bold")
ax.set_ylim(0, por_hora.max() * 1.12); ax.grid(axis="x", visible=False)
salvar("g4_hora.png")

# ---------------------------------------------------------------- 5. ranking de taxas
# Taxa média anual de 2023-25, só municípios com >= 20 mil hab. (mesmo critério do artigo).
p = mun[mun.ANO.between(2023, 2025)].groupby("chave").agg(c=("casos", "sum"), p=("populacao", "mean"))
p = p[p.p >= 20000]
p["taxa"] = p.c / (p.p * 3) * 1e5
p = p.sort_values("taxa")
print(f"\n5. Municípios com >= 20 mil hab.: {len(p)}")
print(p.taxa.round(1).rename(index=nome).to_string())

sel = pd.concat([p.head(5), p.tail(5)])  # 5 menores e 5 maiores taxas
sel.index = nome[sel.index]
maceio = p.loc["maceio", "taxa"]
fig, ax = plt.subplots(figsize=(10, 6.6))
ys = list(range(5)) + list(range(6, 11))  # linha vazia separa os dois grupos
ax.barh(ys, sel.taxa, color=[MUTED] * 5 + [RED] * 5, height=0.7)
ax.set_yticks(ys); ax.set_yticklabels(sel.index, fontsize=13, color=FG)
for y, v in zip(ys, sel.taxa):
    ax.text(v + 0.8, y, br(v), va="center", fontsize=12, color=FG)
ax.axvline(maceio, color=FG, ls="--", lw=1.4)
ax.text(maceio + 0.6, 5, "Maceió " + br(maceio), color=FG, fontsize=12, va="center")
ax.set_xlabel("Vítimas por 100 mil hab. por ano (2023–25)"); ax.set_xlim(0, 70)
ax.grid(axis="y", visible=False)
salvar("g5_ranking.png")

print("\nPronto. Gráficos em", args.saida)
