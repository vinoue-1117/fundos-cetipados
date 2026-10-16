# Regras de alocação

Regras do assessor que a skill aplica. Os valores numéricos e listas ficam em `parametros.csv`; este arquivo explica como aplicá-los.

## Limite por ativo

- Máximo por fundo: `limite_por_ativo_pct` de `parametros.csv`, em % do patrimônio total do cliente.
- A conta soma a posição que o cliente já tem no fundo com o valor sugerido.
- O patrimônio usado é o "Este é o seu patrimônio" do relatório, acrescido do valor de entrada quando ele for aporte novo.

## Público-alvo

- A qualificação assumida é `qualificacao_padrao` de `parametros.csv`. Cliente qualificado: são elegíveis os fundos "Investidor em Geral" e "Investidor Qualificado".
- Para cliente profissional, todos os fundos são elegíveis. Para cliente não qualificado, só os "Investidor em Geral".

## Reclassificações

A XP classifica alguns fundos como Multimercado quando a classificação correta é **Pós-fixado - Demais**. Identificar pelo nome contendo algum dos termos de `reclassificar_pos_demais` em `parametros.csv`.

## Seções do relatório de posição → classe

| Seção no relatório XP | Classe em `alocacao-alvo.csv` |
|---|---|
| Renda Fixa › Prefixada | Prefixado |
| Renda Fixa › Pós-Fixada | Pós-fixado |
| Renda Fixa › Inflação | Inflação |
| Fundos de Renda Fixa Pós-Fixado | Pós-fixado |
| Fundos de Renda Fixa Pré-Fixado | Prefixado |
| Fundos de Inflação | Inflação |
| Fundos Multimercado | Multimercados (salvo reclassificação acima) |

Seção que não está na tabela: classificar pelo nome e indexador do ativo e marcar a linha como inferida na saída.

## Caixa

- Conta como **Caixa** o que é Pós-fixado com resgate até D+1: saldo em conta, fundos de liquidez/DI, Tesouro Selic.
- O resto do Pós-fixado é **Demais**.
- Fundo cetipado nunca conta como Caixa e nunca é sugerido para cobrir déficit de Caixa.
