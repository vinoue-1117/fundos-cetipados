# Regras de alocação

Regras do assessor que a skill aplica. Os valores numéricos e listas ficam em `parametros.csv`; este arquivo explica como aplicá-los.

## Limite por ativo

- Máximo por fundo: `limite_por_ativo_pct` de `parametros.csv`, em % do patrimônio total do cliente.
- A conta soma a posição que o cliente já tem no fundo com o valor sugerido.
- O patrimônio usado é o "Este é o seu patrimônio" do relatório, acrescido do valor de entrada quando ele for aporte novo.
- O relatório não traz CNPJ: case a posição com o fundo de `aprovados.csv` pelo nome, ignorando maiúsculas e sufixos como FII, FIAgro, Feeder e RL. Se o nome puder ser de mais de um fundo, pergunte ao assessor.
- Fundo em que a posição existente já atinge ou passa do limite não recebe sugestão.

## Público-alvo

- A qualificação do cliente é `qualificacao_padrao` de `parametros.csv`, salvo se o assessor informar outra.
- O público-alvo de cada fundo vem da prateleira (`references/navegacao.md`): `isProfessionalInvestor` exige cliente profissional; `isQualifiedInvestor` exige qualificado ou profissional; sem nenhum dos dois, o fundo serve a qualquer cliente.

## Reclassificações

A XP classifica alguns fundos como Multimercado quando a classificação correta é **Pós-fixado**. Identificar pelo nome contendo algum dos termos de `reclassificar_pos_demais` em `parametros.csv`.

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
