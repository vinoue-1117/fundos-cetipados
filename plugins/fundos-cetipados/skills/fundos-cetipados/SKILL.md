---
name: fundos-cetipados
description: "Sugere aplicação em fundos cetipados (fundos fechados do mercado secundário XP: FII, FIAgro, FIDC, FIP, FI-Infra) para um cliente, a partir da posição consolidada e de um valor de entrada. Compara a carteira por fator de risco (Pós, Inflação, Prefixado) com a alocação-alvo do perfil e escolhe fundos da lista pré-aprovada disponíveis na prateleira. Trigger: 'aplicar em cetipados', 'sugerir fundo cetipado', 'prateleira do secundário', 'onde aplicar R$ X do cliente', 'mostrar configuração dos cetipados'."
---

# Sugestão de aplicação em fundos cetipados

A saída é uma **sugestão** para o assessor decidir. A skill lê páginas e arquivos; a ordem quem envia é o assessor, na plataforma. Na prateleira, use só leitura: nada de clicar em comprar, aplicar ou confirmar.

Arquivos da skill (leia todos no passo 1):

- `config/alocacao-alvo.csv`: alvo por classe para cada perfil (conservadora, moderada, sofisticada), com comentário por classe.
- `config/parametros.csv`: limite por ativo, qualificação padrão e termos de reclassificação.
- `config/regras.md`: limite por ativo, público-alvo, reclassificações, mapeamento das seções do relatório, definição de Caixa.
- `config/aprovados.csv`: fundos pré-aprovados com fator, público-alvo e prazo. Linhas com `revisar=sim` estão sem fator definido: só entram na sugestão se o assessor informar o fator na conversa.
- `references/navegacao.md`: como ler a prateleira do secundário.

Todo número da saída vem da posição, dos arquivos da skill, da prateleira ou de um ajuste do assessor na conversa. Dado ausente vira **lacuna** explícita na saída, nunca estimativa.

**Ajustes na conversa.** Para o cliente em análise, o assessor pode trocar o alvo de uma classe ou o `limite_por_ativo_pct`. Use o valor dele no lugar do arquivo e registre o ajuste na saída. Se o alvo ajustado tirar a soma do perfil de 100%, pergunte qual classe compensa. O resto segue os arquivos: lista de aprovados, público-alvo e reclassificações não se ajustam.

**Mostrar configuração.** Se o assessor pedir para ver a configuração, responda só com tabelas no chat, lidas dos arquivos: alvo por classe × perfil; parâmetros; fundos aprovados (fundo, gestora, tipo, fator, público-alvo, prazo), marcando os `revisar=sim`. Não rode os passos abaixo.

## 1. Inputs

Reúna:

- **Posição consolidada** do cliente (xlsx ou PDF exportado do Hub XP).
- **Valor de entrada** em R$, e a origem dele: aporte novo (soma ao patrimônio) ou saldo/resgate já na posição (patrimônio não muda). Default: aporte novo.
- **Perfil de alocação**: conservadora, moderada ou sofisticada. O relatório não traz o perfil: pergunte.
- **Qualificação**: default `qualificacao_padrao` de `parametros.csv`. Confirme junto com o perfil.

Pergunte tudo o que faltar numa mensagem só. Pronto quando os quatro itens estiverem confirmados.

## 2. Carteira atual por classe

Leia a posição e atribua cada ativo a uma classe de `alocacao-alvo.csv`, usando o mapeamento de seções e as reclassificações de `regras.md`. Separe Pós-fixado em Caixa e Demais pela regra de Caixa.

Calcule o % de cada classe sobre o patrimônio total. Pronto quando toda linha do relatório estiver numa classe, com as inferidas marcadas, e a soma bater com o patrimônio do relatório.

## 3. Lacunas contra o alvo

Para cada classe: alvo do perfil, % atual, e diferença em R$ sobre o patrimônio pós-aplicação. Os cetipados podem cobrir lacunas em **Pós-fixado - Demais**, **Inflação** e **Prefixado** (pelo `fator` de `aprovados.csv`).

Se as lacunas positivas estiverem só em classes que cetipados não cobrem (Caixa, RV, Internacional, Multimercados), diga isso na saída e indique a classe que pede o recurso. A sugestão de cetipados, nesse caso, é opcional e justificada.

## 4. Prateleira

Siga `references/navegacao.md` e colete, para cada fundo de `aprovados.csv` elegível pelo público-alvo, se há oferta disponível e os dados da oferta. Pronto quando cada fundo elegível estiver como disponível (com os dados) ou indisponível.

## 5. Seleção

Monte a sugestão com um ou mais fundos disponíveis:

- Priorize as classes com maior lacuna em R$.
- Respeite o limite por ativo de `regras.md`, somando a posição existente no mesmo fundo.
- A soma das sugestões fecha o valor de entrada, ou a saída explica o resíduo.

Dentro dessas regras há liberdade de julgamento: diversificação entre gestoras e tipos, prazo de encerramento, condição da oferta. Registre o motivo de cada escolha em uma linha.

## 6. Saída (tabela no chat)

1. **Parâmetros usados**: perfil, qualificação, limite por ativo. Cada ajuste da conversa aparece com o valor do arquivo ao lado, ex.: `Inflação 20% (padrão: 15%)`.
2. **Alocação por classe**: classe | alvo | atual | após sugestão (em %).
3. **Sugestão**: fundo | fator | valor (R$) | % do patrimônio | dados da oferta | motivo.
4. **Lacunas e ressalvas**: dados ausentes, classificações inferidas, fundos `revisar=sim` ignorados, resíduo não alocado.

Formato: moeda `R$ 1.234,56`, percentuais com vírgula, datas `DD/MM/AAAA`.
