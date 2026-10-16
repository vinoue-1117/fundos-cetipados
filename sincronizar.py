"""Converte a configuracao entre os arquivos da skill e os documentos do banco do artefato.

  exportar          arquivos -> sync/docs/<colecao>/<doc>.json (corpo pronto para ArtifactData set)
  importar <dir>    dump do ArtifactData (out_dir) -> alocacao-alvo.csv, parametros.csv, sobrescritas.csv

Passo a passo completo em SINCRONIZACAO.md.
"""
import csv
import json
import sys
from pathlib import Path

BASE = Path(__file__).parent
CONFIG = BASE / "plugins" / "fundos-cetipados" / "skills" / "fundos-cetipados" / "config"
DOCS = BASE / "sync" / "docs"
PERFIS = ["conservadora", "moderada", "sofisticada"]
CAMPOS_SOB = ["fundo", "fator", "fonte", "confianca", "aprovacao", "nota"]


def ler_csv(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def gravar_csv(p, campos, linhas):
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, campos, delimiter=";", lineterminator="\n")
        w.writeheader()
        w.writerows(linhas)


def num(s):
    return float(s.replace("%", "").replace(",", "."))


def pct(v):
    return f"{v:.2f}".replace(".", ",") + "%"


def exportar():
    classes = [
        {"classe": r["classe"], **{p: num(r[p]) for p in PERFIS}, "comentario": r["comentario"]}
        for r in ler_csv(CONFIG / "alocacao-alvo.csv")
    ]
    par = {r["chave"]: r["valor"] for r in ler_csv(CONFIG / "parametros.csv")}
    docs = {
        "config/alocacao": {"classes": classes},
        "config/parametros": {
            "limite_por_ativo_pct": num(par["limite_por_ativo_pct"]),
            "qualificacao_padrao": par["qualificacao_padrao"],
            "min_contas_aprovacao": int(par["min_contas_aprovacao"]),
            "reclassificar_pos_demais": [t.strip() for t in par["reclassificar_pos_demais"].split(",") if t.strip()],
        },
        "base/fundos": json.loads((BASE / "sync" / "base_fundos.json").read_text(encoding="utf-8")),
    }
    for r in ler_csv(BASE / "sobrescritas.csv"):
        docs[f"sobrescritas/{r['cnpj']}"] = {k: r[k] for k in CAMPOS_SOB}
    for caminho, corpo in docs.items():
        p = DOCS / f"{caminho}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(corpo, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(docs)} documentos em {DOCS}")


def corpo(p):
    d = json.loads(p.read_text(encoding="utf-8"))
    return d["data"] if isinstance(d.get("data"), dict) else d


def importar(dump):
    dump = Path(dump)
    aloc = corpo(dump / "config" / "alocacao.json")["classes"]
    soma = {p: round(sum(c[p] for c in aloc), 2) for p in PERFIS}
    if any(v != 100 for v in soma.values()):
        sys.exit(f"ERRO: alocacao nao soma 100% por perfil: {soma}")
    gravar_csv(CONFIG / "alocacao-alvo.csv", ["classe", *PERFIS, "comentario"],
               [{"classe": c["classe"], **{p: pct(c[p]) for p in PERFIS}, "comentario": c.get("comentario", "")}
                for c in aloc])

    par = corpo(dump / "config" / "parametros.json")
    valores = {
        "limite_por_ativo_pct": f"{par['limite_por_ativo_pct']:g}".replace(".", ","),
        "qualificacao_padrao": par["qualificacao_padrao"],
        "min_contas_aprovacao": str(int(par["min_contas_aprovacao"])),
        "reclassificar_pos_demais": ", ".join(par["reclassificar_pos_demais"]),
    }
    linhas = ler_csv(CONFIG / "parametros.csv")
    for r in linhas:
        r["valor"] = valores[r["chave"]]
    gravar_csv(CONFIG / "parametros.csv", ["chave", "valor", "descricao"], linhas)

    sob = []
    for p in sorted((dump / "sobrescritas").glob("*.json")):
        d = corpo(p)
        if any(d.get(k) for k in ("fator", "aprovacao", "nota")):
            sob.append({"cnpj": p.stem, **{k: d.get(k, "") for k in CAMPOS_SOB}})
    gravar_csv(BASE / "sobrescritas.csv", ["cnpj", *CAMPOS_SOB], sob)
    print(f"alocacao: {len(aloc)} classes | parametros: {valores} | sobrescritas: {len(sob)}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["exportar"]:
        exportar()
    elif sys.argv[1:2] == ["importar"] and len(sys.argv) == 3:
        importar(sys.argv[2])
    else:
        sys.exit(__doc__)
