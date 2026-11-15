from __future__ import annotations

import gzip
import io
import json
import re
import unicodedata
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

BASE_API = "https://dados.al.gov.br/catalogo/api/3/action"
DATASET = "cvli-2012-a-2023-base-microdados"
ARQ_POPULACAO = Path(__file__).resolve().parents[1] / "dados_brutos" / "populacao_municipios_AL.csv"
CABECALHOS = {"User-Agent": "painel-cvli/1.0"}
ARQ_MALHA = Path(__file__).resolve().parent / "assets" / "alagoas_municipios.geojson"
URL_MALHA = ("https://servicodados.ibge.gov.br/api/v3/malhas/estados/27"
             "?intrarregiao=municipio&qualidade=minima&formato=application/vnd.geo+json")

FAIXAS = [-1, 11, 17, 24, 34, 44, 59, np.inf]
ROTULOS_FAIXA = ["0–11", "12–17", "18–24", "25–34", "35–44", "45–59", "60+"]
DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
PERIODOS = ["Madrugada", "Manhã", "Tarde", "Noite"]


def _abrir(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=CABECALHOS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def buscar_metadados() -> dict:
    """Pergunta à API CKAN qual é o recurso CSV mais recente do dataset de CVLI."""
    pacote = json.loads(_abrir(f"{BASE_API}/package_show?id={DATASET}", 30))["result"]
    csvs = [r for r in pacote["resources"] if str(r.get("format", "")).upper() == "CSV"]
    if not csvs:
        raise RuntimeError("O dataset não tem recurso em CSV.")
    rec = max(csvs, key=lambda r: r.get("last_modified") or r.get("created") or "")
    return {
        "titulo": pacote["title"],
        "pagina": f"https://dados.al.gov.br/catalogo/dataset/{pacote['id']}",
        "recurso": rec["name"],
        "url_csv": rec["url"],
        "atualizado_em": rec.get("last_modified") or pacote["metadata_modified"],
        "consultado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def baixar_csv(url: str) -> pd.DataFrame:
    bruto = _abrir(url, 120)
    try:
        texto = bruto.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = bruto.decode("latin-1")
    return pd.read_csv(io.StringIO(texto), dtype=str)


def _chave(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def _sem_acento(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()


def classifica_local(x) -> str:
    s = _sem_acento(str(x))
    if s in {"ni", "n/i", "sem informacao", "nao informado", "outro", "outros", "", "nan"} or s.startswith("http"):
        return "Não informado/outros"
    if re.search(r"show|evento|aposta|hotel|motel|hospedagem|comercial|coercial|ciomercial|bar\b|restaurante|mercado|oficina|"
                 r"salao|barbearia|boate|danceteria|igreja|escola|ensino|saude|hospital|hge|consultorio|clinica|"
                 r"trabalho|feira|clube|quadra|campo de futebol|churrasquinho|estabelecimento|shopping|"
                 r"presidio|cela|cadeia|cadeiao|delegacia|detencao|custodia|internacao|prisional|orgao|instituicao|centro social|"
                 r"parque|mirante|bloco|aviacao|apoio|assistencia|neas|rodoviaria", s):
        return "Estabelecimento/instituição"
    if re.search(r"imedia|proxi|porta de|exterior|quintal|arredores|esquina|trás do|tras do", s):
        return "Entorno da residência"
    if re.search(r"casa|resid|resod|privad|quarto|domicilio|telhado", s) and not re.search(r"abandon|sem morador|construcao", s):
        return "Dentro da residência"
    if re.search(r"^v[ií]a|^via|logradouro|local p|loca p|publi|public|praca|pracinha|beco|travessa|rodovia|estrada|ponto de onibus|"
                 r"estacionamento|coletivo|onibus|van\b|alternativo|taxi|veiculo|ferrovia|linha ferrea|calcad|vila$|canal|rua", s):
        return "Via/espaço público"
    if re.search(r"vegeta|vegta|mata|plantac|canavial|zona rural|area rural|rural|sitio|fazenda|chacara|engenho|propriedade|terras|"
                 r"rio\b|riacho|lagoa|acude|barragem|cacimba|corrego|grota|mangue|praia|margem|beira|vala|valeta|fossa|cova|"
                 r"terreno|tereno|baldio|area verde|ribanceira|buraco|lixao|aquatico|campo", s):
        return "Área rural/natural/terreno"
    if re.search(r"abandon|desocupad|sem morador|construcao|obra|galpao|edificacao|predio|alvenaria|imovel", s):
        return "Imóvel abandonado/em obra"
    return "Não informado/outros"


def _grupo_instrumento(x) -> str:
    s = _sem_acento(str(x))
    if s.startswith("paf"):
        return "Arma de fogo"
    if s == "branca":
        return "Arma branca"
    if s == "espancamento":
        return "Espancamento"
    if s in {"ni", "nan", "", "sem informacao", "nao informado"}:
        return "Não informado"
    return "Outros"


def _ler_data(serie: pd.Series) -> pd.Series:
    data = pd.to_datetime(serie, format="%d/%m/%Y", errors="coerce")
    falta = data.isna() & serie.notna()
    if falta.any():
        data[falta] = pd.to_datetime(serie[falta].str[:10], format="%Y-%m-%d", errors="coerce")
    return data


def preparar(bruto: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df = pd.DataFrame({
        "id": pd.to_numeric(bruto["ID_CONTROLE"], errors="coerce"),
        "data": _ler_data(bruto["DATA DO FATO"]),
        "hora": pd.to_numeric(bruto["HORA DO FATO"].str[:2], errors="coerce"),
        "municipio": bruto["CIDADE DO FATO"].str.strip(),
        "bairro": bruto["BAIRRO DO FATO"].str.strip(),
        "sexo": bruto["SEXO DA VITIMA"].str.strip(),
        "cor": bruto["COR/RACA DA VITIMA"].str.strip(),
        "idade": pd.to_numeric(bruto["IDADE DA VITIMA"], errors="coerce"),
        "instrumento": bruto["INSTRUMENTO UTILIZADO"].map(_grupo_instrumento),
        "local": bruto["LOCAL DO FATO"].map(classifica_local),
        "tipo": bruto["SUBJETIVIDADE COMPLEMENTAR"].str.strip(),
    })
    n_bruto = len(df)
    sem_data = int(df["data"].isna().sum())
    df = df.dropna(subset=["data"]).copy()
    df = df[df["hora"].between(0, 23) | df["hora"].isna()]

    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.to_period("M").dt.to_timestamp()
    df["dia_semana"] = pd.Categorical(df["data"].dt.dayofweek.map(dict(enumerate(DIAS))), categories=DIAS, ordered=True)
    df["periodo"] = pd.cut(df["hora"], [-1, 5, 11, 17, 23], labels=PERIODOS)
    df["faixa"] = pd.cut(df["idade"], FAIXAS, labels=ROTULOS_FAIXA)
    df["sexo"] = df["sexo"].where(df["sexo"].isin(["Masculino", "Feminino"]), "Não informado")
    df["cor"] = df["cor"].where(~df["cor"].str.upper().isin(["NI", ""]) & df["cor"].notna(), "Não informado")
    df["feminicidio"] = df["tipo"].eq("Feminicídio")
    df["chave"] = df["municipio"].map(_chave)

    diag = {
        "linhas_arquivo": n_bruto,
        "linhas_usadas": len(df),
        "sem_data_valida": sem_data,
        "data_min": df["data"].min(),
        "data_max": df["data"].max(),
        "ids_duplicados": int(df["id"].duplicated().sum()),
        "datas_futuras": int((df["data"] > pd.Timestamp.now()).sum()),
    }
    return df.reset_index(drop=True), diag


def carregar_populacao() -> pd.DataFrame | None:

    if not ARQ_POPULACAO.exists():
        return None
    pop = pd.read_csv(ARQ_POPULACAO)
    pop["chave"] = pop["municipio"].map(_chave)
    return pop


def populacao_recente(pop: pd.DataFrame | None) -> pd.DataFrame | None:
    if pop is None:
        return None
    ult = pop.sort_values("ano").groupby("chave").tail(1)
    return ult[["chave", "populacao", "ano"]].rename(columns={"populacao": "pop", "ano": "ano_pop"})


def carregar_malha() -> dict:
   
    if not ARQ_MALHA.exists():
        bruto = _abrir(URL_MALHA, 60)
        if bruto[:2] == bytes([0x1F, 0x8B]):          # o IBGE às vezes responde comprimido (gzip)
            bruto = gzip.decompress(bruto)
        ARQ_MALHA.parent.mkdir(exist_ok=True)
        ARQ_MALHA.write_bytes(bruto)
    return _orientar_para_plotly(json.loads(ARQ_MALHA.read_text(encoding="utf-8")))


def _area(anel) -> float:
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(anel, anel[1:] + anel[:1])) / 2


def _orientar_para_plotly(geo: dict) -> dict:
    for f in geo["features"]:
        g = f["geometry"]
        pols = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for pol in pols:
            for i, anel in enumerate(pol):
                horario = _area(anel) < 0
                if horario != (i == 0):
                    anel.reverse()
    return geo


def municipios_referencia(pop: pd.DataFrame | None) -> pd.DataFrame | None:
    if pop is None:
        return None
    ult = pop.sort_values("ano").groupby("cod_ibge").tail(1)
    ref = ult[["cod_ibge", "municipio", "chave", "populacao"]].copy()
    ref["cod_ibge"] = ref["cod_ibge"].astype(str)
    return ref.reset_index(drop=True)
