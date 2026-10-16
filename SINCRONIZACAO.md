# Sincronização: painel ↔ skill

O painel ([artefato](https://claude.ai/artifact/Yb5HjC5wDChzxN6rcjXyPq), fonte em `artefato.html`) edita uma cópia da configuração da skill no banco do artefato. A skill roda só com os arquivos do pacote; a sincronização é feita sob demanda, no Claude Code.

## Quem é dono de cada dado

| Documento no banco | Arquivo | Dono |
|---|---|---|
| `base/fundos` | `sync/base_fundos.json` (gerado) | `gerar_aprovados.py`, a partir do Guia e do histórico. O painel só lê. |
| `sobrescritas/<cnpj>` | `sobrescritas.csv` | painel: fator, fonte, confiança, aprovação (incluir/excluir), nota |
| `config/alocacao` | `plugins/fundos-cetipados/skills/fundos-cetipados/config/alocacao-alvo.csv` | painel |
| `config/parametros` | `plugins/fundos-cetipados/skills/fundos-cetipados/config/parametros.csv` | painel |
| `config/sync` | — | marca `ultima_sync_em` (ISO, UTC); o painel compara com o `atualizado_em` de cada documento para mostrar edições pendentes |

## Painel → arquivos

1. `ArtifactData list` das coleções `config` e `sobrescritas` com `out_dir` num diretório vazio do scratchpad.
2. `python -I sincronizar.py importar <out_dir>`: grava os três arquivos. Para se a alocação de algum perfil não somar 100%.
3. `python gerar_aprovados.py`: regera `aprovados.csv` e `sync/base_fundos.json`.
4. Grave `base/fundos` (passo seguinte) e `config/sync` com `ultima_sync_em` atual.
5. Commit e push na `master`. O repositório é o marketplace do plugin (`.claude-plugin/marketplace.json`); quem instalou pelo [roteiro de instalação](https://claude.ai/artifact/7VZTF13nUB7vvg2a1MTjnx) recebe a versão nova pela sincronização do marketplace. O plugin não declara `version`, então cada commit conta como atualização.

## Arquivos → painel

Quando o Guia de Fundos ou o histórico em `prateleira/` mudar, ou um arquivo de config for editado à mão:

1. `python gerar_aprovados.py` e `python sincronizar.py exportar`: grava os corpos em `sync/docs/<colecao>/<doc>.json`.
2. `ArtifactData batch` com `set` de cada arquivo (`file_path`), passando o `if_version` lido antes. Só `base/fundos` quando apenas a base mudou, para não sobrescrever edições do painel ainda não importadas.
3. `config/sync` com `ultima_sync_em` atual.
