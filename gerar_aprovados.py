"""Gera plugins/fundos-cetipados/skills/fundos-cetipados/config/aprovados.csv a partir do historico do secundario e do Guia de Fundos.

Base: fundos com ao menos uma compra no historico e presentes nas abas Cetipados ou PR+ do Guia.
Criterio de pre-aprovacao: compras de pelo menos `min_contas_aprovacao` contas distintas (config/parametros.csv).
sobrescritas.csv (chave CNPJ) prevalece sobre o criterio (aprovacao incluir/excluir) e sobre o fator inferido.
O fator inferido vem do 'Objetivo de Retorno'; sem ele, do nome do fundo; sem nenhum dos dois, fica em branco
com revisar=sim.

Tambem grava sync/base_fundos.json, a lista base que vai para o artefato de configuracao (SINCRONIZACAO.md).
"""
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
CONFIG = BASE / "plugins" / "fundos-cetipados" / "skills" / "fundos-cetipados" / "config"
SAIDA = CONFIG / "aprovados.csv"
SAIDA_SYNC = BASE / "sync" / "base_fundos.json"
ABAS = ["Fundos Cetipados", "Fundos PR+"]

parametros = pd.read_csv(CONFIG / "parametros.csv", sep=";", dtype=str).set_index("chave")["valor"]
MIN_CONTAS = int(parametros["min_contas_aprovacao"])
sobrescritas = pd.read_csv(BASE / "sobrescritas.csv", sep=";", dtype=str).fillna("").set_index("cnpj")


def norm(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())


def fator(texto):
    t = norm(texto)
    if re.search(r"ipca|imab|ima-b", t):
        return "Inflação"
    if re.search(r"cdi|\bdi\b", t):
        return "Pós"
    if re.search(r"\bpr[eé]\b|prefixad", t):
        return "Pré"
    return ""


def fator_objetivo(obj):
    if pd.isna(obj):
        return ""
    f = fator(obj)
    # Objetivo so com taxa (ex.: "15,14%", "11% a 12% a.a.", 0.15) indica prefixado
    if not f and re.fullmatch(r"[\d.,%\saa\.-]+", norm(obj)):
        return "Pré"
    return f


def prazo(v):
    # Excel converte "5" em data 05/01/1900; desfaz para o numero de anos
    if isinstance(v, datetime):
        return str((v - datetime(1899, 12, 30)).days)
    return "" if pd.isna(v) else str(v)


def texto(v):
    return "" if pd.isna(v) else str(v).strip()


hist = pd.read_csv(BASE / "prateleira" / "mercado_secundario_fundos.csv", sep=";", encoding="utf-8-sig", decimal=",")
compras = hist[hist.Side == "C"].groupby("Fundo").agg(compras=("Conta", "size"), contas=("Conta", "nunique"))
compras.index = compras.index.map(norm)

guia = pd.concat(
    pd.read_excel(BASE / "prateleira" / "Guia-de-Fundos.xlsx", aba, header=5).dropna(subset=["Fundo"]).assign(aba=aba)
    for aba in ABAS
)
guia["chave"] = guia["Fundo"].map(norm)
df = guia.merge(compras, left_on="chave", right_index=True)

df["cnpj"] = df["CNPJ"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(14)
df["fator_inferido"] = [fator_objetivo(o) or fator(n) for o, n in zip(df["Objetivo de Retorno"], df["Fundo"])]
sob = sobrescritas.reindex(df["cnpj"]).fillna("")
df["fator"] = [s or f for s, f in zip(sob["fator"], df["fator_inferido"])]
df["criterio"] = df["contas"] >= MIN_CONTAS
df["aprovado"] = [(c and a != "excluir") or a == "incluir" for c, a in zip(df["criterio"], sob["aprovacao"])]

out = pd.DataFrame({
    "fundo": df["Fundo"].str.strip(),
    "cnpj": df["cnpj"],
    "aba_guia": df["aba"].str.replace("Fundos ", ""),
    "gestora": df["Gestora"],
    "tipo": df["Tipo"],
    "classe_cvm": df["Classificação CVM"],
    "publico_alvo": df["Público-Alvo"],
    "objetivo_retorno": df["Objetivo de Retorno"],
    "prazo_encerramento_anos": df["Prazo Encerramento (Anos)"].map(prazo),
    "fator": df["fator"],
    "revisar": ["sim" if not f else "" for f in df["fator"]],
    "compras_historico": df["compras"],
    "contas_historico": df["contas"],
})
# Público-alvo fica fora da skill: a prateleira informa a exigência de cada oferta.
aprovados = out[df["aprovado"].values].drop(columns="publico_alvo").sort_values(["fator", "contas_historico"], ascending=[True, False])

SAIDA.parent.mkdir(parents=True, exist_ok=True)
aprovados.to_csv(SAIDA, sep=";", index=False, encoding="utf-8-sig")
print(f"{len(aprovados)} fundos gravados em {SAIDA}")
print(aprovados[["fundo", "objetivo_retorno", "fator"]].to_string())

base = [
    {
        "cnpj": r.cnpj,
        "fundo": r.fundo,
        "aba_guia": r.aba_guia,
        "gestora": texto(r.gestora),
        "tipo": texto(r.tipo),
        "classe_cvm": texto(r.classe_cvm),
        "publico_alvo": texto(r.publico_alvo),
        "objetivo_retorno": texto(r.objetivo_retorno),
        "prazo_encerramento_anos": r.prazo_encerramento_anos,
        "fator_inferido": fi,
        "compras_historico": int(r.compras_historico),
        "contas_historico": int(r.contas_historico),
    }
    for r, fi in zip(out.itertuples(), df["fator_inferido"])
]
SAIDA_SYNC.parent.mkdir(parents=True, exist_ok=True)
SAIDA_SYNC.write_text(json.dumps({
    "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
    "historico_de": pd.to_datetime(hist["Data"]).min().strftime("%d/%m/%Y"),
    "historico_ate": pd.to_datetime(hist["Data"]).max().strftime("%d/%m/%Y"),
    "fundos": sorted(base, key=lambda f: -f["contas_historico"]),
}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(base)} fundos na base do artefato: {SAIDA_SYNC}")
