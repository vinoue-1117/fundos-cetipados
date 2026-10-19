---
name: fundos-cetipados
description: "Sugere aplicação em fundos cetipados (fundos fechados do mercado secundário XP: FII, FIAgro, FIDC, FIP, FI-Infra) para um cliente, a partir da posição consolidada e de um valor de entrada. Compara a carteira por fator de risco (Pós, Inflação, Prefixado) com a alocação-alvo do perfil e escolhe fundos da lista pré-aprovada disponíveis na prateleira. Trigger: 'aplicar em cetipados', 'sugerir fundo cetipado', 'prateleira do secundário', 'onde aplicar R$ X do cliente', 'mostrar configuração dos cetipados'."
---

# Sugestão de aplicação em fundos cetipados

A saída é uma **sugestão** para o assessor decidir. A skill lê páginas e arquivos; a ordem quem envia é o assessor, na plataforma. Na prateleira, use só leitura: nada de clicar em comprar, aplicar ou confirmar.

Arquivos da skill (leia todos no passo 1):

- `config/alocacao-alvo.csv`: alvo por classe para cada perfil (conservadora, moderada, sofisticada), com comentário por classe.
- `config/parametros.csv`: limite por ativo, qualificação padrão e termos de reclassificação.
- `config/regras.md`: limite por ativo e casamento da posição com os aprovados, público-alvo, reclassificações, mapeamento das seções do relatório.
- `config/aprovados.csv`: fundos pré-aprovados com fator e prazo. Linhas com `revisar=sim` estão sem fator definido: só entram na sugestão se o assessor informar o fator na conversa.
- `references/navegacao.md`: como ler a prateleira do secundário.

Todo número da saída vem da posição, dos arquivos da skill, da prateleira ou de um ajuste do assessor na conversa. Dado ausente vira **lacuna** explícita na saída, nunca estimativa.

**Ajustes na conversa.** Para o cliente em análise, o assessor pode trocar o alvo de uma classe ou o `limite_por_ativo_pct`. Use o valor dele no lugar do arquivo e registre o ajuste na saída. Se o alvo ajustado tirar a soma do perfil de 100%, pergunte qual classe compensa. O resto segue os arquivos: lista de aprovados, público-alvo e reclassificações não se ajustam.

**Mostrar configuração.** Se o assessor pedir para ver a configuração, responda só com tabelas no chat, lidas dos arquivos: alvo por classe × perfil; parâmetros; fundos aprovados (fundo, gestora, tipo, fator, prazo), marcando os `revisar=sim`. Não rode os passos abaixo.

## 1. Inputs

Reúna:

- **Posição consolidada** do cliente (xlsx ou PDF exportado do Hub XP).
- **Valor de entrada** em R$, e a origem dele: aporte novo (soma ao patrimônio) ou saldo/resgate já na posição (patrimônio não muda). Default: aporte novo.
- **Perfil de alocação**: conservadora, moderada ou sofisticada. O relatório não traz o perfil: pergunte.
- **Qualificação**: default `qualificacao_padrao` de `parametros.csv`. Confirme junto com o perfil.

Pergunte tudo o que faltar numa mensagem só. Item que o assessor não responder assume o default e aparece como "(padrão)" em Parâmetros usados. Pronto quando os quatro itens estiverem definidos.

## 2. Carteira atual por classe

Só as classes que os cetipados cobrem entram na análise: **Pós-fixado**, **Inflação** e **Prefixado**. Leia a posição e atribua cada ativo de renda fixa a uma delas, usando o mapeamento de seções e as reclassificações de `regras.md`. O resto da carteira conta só no patrimônio total.

Calcule o % de cada uma sobre o patrimônio total. Pronto quando todo ativo de renda fixa estiver numa classe, com os inferidos marcados.

## 3. Lacunas contra o alvo

Para cada uma das três classes: alvo do perfil, % atual e lacuna em R$ (alvo × patrimônio pós-aplicação − posição atual). O `fator` de `aprovados.csv` dá a classe do fundo: Pós → Pós-fixado, Pré → Prefixado, Inflação → Inflação.

## 4. Prateleira

Siga `references/navegacao.md` e colete, para cada fundo de `aprovados.csv`, se há oferta disponível, os dados da oferta e o público-alvo exigido. Fundo cujo público-alvo o cliente não atende (`regras.md`) fica fora da sugestão. Pronto quando cada fundo estiver como disponível (com os dados), indisponível ou fora do público-alvo.

## 5. Seleção

Monte a sugestão com um ou mais fundos disponíveis:

- Priorize as classes com maior lacuna em R$.
- Respeite o limite por ativo de `regras.md`, somando a posição existente no mesmo fundo. Fundo já no limite ou acima não recebe sugestão.
- O valor sugerido fica entre a aplicação mínima da oferta e o valor disponível somado das fontes com estoque (`references/navegacao.md`, Disponibilidade).
- Valores em R$. A conversão em cotas fica com a plataforma.
- A soma das sugestões fecha o valor de entrada, ou a saída explica o resíduo.

Dentro dessas regras há liberdade de julgamento: diversificação entre gestoras e tipos, prazo de encerramento, condição da oferta. Registre o motivo de cada escolha em uma linha.

## 6. Saída (tabela no chat)

1. **Parâmetros usados**: perfil, qualificação, limite por ativo (em % e em R$), valor de entrada e origem, patrimônio-base com a data da posição. Cada ajuste da conversa aparece com o valor do arquivo ao lado, ex.: `Inflação 20% (padrão: 15%)`.
2. **Alocação por classe** (só as três): classe | alvo | atual | após sugestão (em %) | lacuna antes da sugestão (R$).
3. **Sugestão**: fundo | fator | valor (R$) | % do patrimônio | dados da oferta | motivo.
4. **Lacunas e ressalvas**: dados ausentes, classificações inferidas, fundos indisponíveis ou fora do público-alvo, fundos `revisar=sim` ignorados, resíduo não alocado.

Formato: moeda `R$ 1.234,56`, percentuais com vírgula, datas `DD/MM/AAAA`.
