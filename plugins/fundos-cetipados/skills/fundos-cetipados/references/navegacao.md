# Navegação: prateleira do secundário XP

## Acesso

- URL: `https://hub.xpi.com.br/new/fundos-de-investimento#/secundario/prateleira`. Se não abrir, entre pelo Hub em Fundos de Investimento › Mercado Secundário › Prateleira.
- Use o Chrome em que o assessor já está logado no Hub. Tela de login aparecendo: pare e peça ao assessor que entre. Nunca digite a senha.
- Somente leitura. Clique só em abas, filtros e no botão **Atualizar**. Nunca em **Comprar**, **Avise-me** ou **Exportar** (gera download).

## O que a página mostra

- **Destaques**: carrossel de fundos em cards (preço unitário, deságio, DY 12M, rentabilidade bruta 12M). Não usar: é um subconjunto da tabela.
- **Todos os fundos**: tabela com abas **Cetipados**, **Portfólio Renda+**, **Alternativos**, **Revolvência** e **Todos**. As abas correspondem ao `aba_guia` de `aprovados.csv` (Cetipados, PR+).
- Filtros acima da tabela: **Estoque** (`XP`, `Cliente`), **Classificação**, **Tributação** e busca por nome.
- Colunas nas abas de família: Nome do Fundo, Qtd. mínima, Preço unitário, Qtd. estoque XP, Deságio/Ágio estoque XP, Qtd. estoque cliente, Deságio/Ágio estoque cliente, Rentab. bruta (12M), Dividend Yield (12M), Risco, Ações. Na aba **Todos** as duas fontes de estoque viram uma só coluna (Qtd. disponível, Deságio compra).
- Expandir a linha mostra objetivo, política, último dividendo, DY, preço e **data da cota**.
- O fundo tem duas fontes de oferta: **estoque XP** (tesouraria) e **estoque cliente** (cotas que outros clientes puseram à venda). Cada uma tem quantidade e deságio próprios.
- Botão **Comprar**: há estoque, mesmo que abaixo do mínimo de aplicação (ver Disponibilidade). Botão **Avise-me**: estoque zerado.

## Coleta

O texto da página (`get_page_text`) passa de 180 mil caracteres e não traz CNPJ. A coleta é pela resposta da API que preenche a tabela, capturada dentro da página:

1. Na aba de prateleira, rode via `javascript_tool`:

   ```js
   window.__cap = {};
   window.__origFetch ??= window.fetch;
   window.fetch = async function (...a) {
     const r = await window.__origFetch.apply(this, a);
     const u = typeof a[0] === 'string' ? a[0] : a[0].url;
     if (/investment-funds-secondary\?/.test(u)) r.clone().text().then(t => { window.__cap.lista = t; });
     return r;
   };
   ```

2. Clique em **Atualizar**. A página chama `GET api-advisor.xpi.com.br/investment-funds/yield-rede/v3/investment-funds-secondary?fundFamily=` e devolve todas as famílias de uma vez (cerca de 150 fundos). Chamar a URL direto dá 401: a página envia chave e token próprios. A resposta chega alguns segundos depois do clique: aguarde 2 a 3 s e confira se `window.__cap.lista` existe antes de concluir que a captura falhou.
3. O retorno do `javascript_tool` é truncado em 1 a 2 mil caracteres. Monte uma linha compacta por fundo aprovado, com os CNPJs de `aprovados.csv`:

   ```js
   const cnpjs = [/* CNPJs de aprovados.csv, 14 dígitos, como texto */];
   const d = JSON.parse(window.__cap.lista).data;
   const cnpj = f => (String(f.documentRegulation || '').match(/(?<!\d)(\d{14})(?!\d)[^/]*\.pdf/i) || [])[1] || '';
   const linha = f => [cnpj(f), f.fundName, f.fundFamily, f.unityPrice, f.quotaDate,
     f.stockOfTreasuryQuotas, f.secondaryPurchaseDiscount, f.stockOfPeerToPeerQuotas, f.peerToPeerBuyDiscount,
     f.minimumQuotaQuantity, f.minimalInitialInvestment, f.isQualifiedInvestor, f.isProfessionalInvestor,
     (f.tags || []).map(x => x.title).join('/')].join('|');
   window.__cap.d = d; window.__cap.linha = linha;
   window.__cap.rows = d.filter(f => cnpjs.includes(cnpj(f))).map(linha);
   window.__cap.rows.length;
   ```

   Leia em blocos de 8: `window.__cap.rows.slice(0, 8).join('\n')`, depois `slice(8, 16)` e assim por diante. Aprovado que não apareceu (sem CNPJ na URL): `window.__cap.d.filter(f => /trecho do nome/i.test(f.fundName)).map(window.__cap.linha).join('\n')`.
4. Restaure: `window.fetch = window.__origFetch`.

A captura falhou (sem `__cap.lista` depois do Atualizar): caia para `get_page_text` na aba **Cetipados** e depois na **Portfólio Renda+**, casando pelo nome.

### Casar com `aprovados.csv`

- CNPJ: 14 dígitos no nome do arquivo de `documentRegulation`, com ou sem sufixo de versão (`.../Regulamento_61238364000107.pdf`, `.../Regulamento_60513922000124_v1.pdf`).
- Alguns fundos não têm o CNPJ na URL (regulamento em `institucional.xpi.com.br` ou campo vazio). Para esses, case pelo nome. Nome divergente: lacuna.
- Fundo da prateleira que não está em `aprovados.csv` fica fora da sugestão.

### Campos

| Campo da API | Na página | Uso |
|---|---|---|
| `fundName` | Nome do Fundo | identificação |
| `documentRegulation` | — | CNPJ (ver acima) |
| `fundFamily` | aba | 5 = Cetipados, 7 = Portfólio Renda+ (conferidos com `aba_guia`); 6 = Alternativos, 8 = Revolvência (pelo conteúdo) |
| `unityPrice` | Preço unitário | R$ por cota |
| `quotaDate` | Data da cota | data do preço |
| `stockOfTreasuryQuotas` | Qtd. estoque XP | cotas disponíveis no estoque XP |
| `secondaryPurchaseDiscount` | Deságio/Ágio estoque XP | % sobre o preço; negativo = ágio |
| `stockOfPeerToPeerQuotas` | Qtd. estoque cliente | cotas à venda por clientes |
| `peerToPeerBuyDiscount` | Deságio/Ágio estoque cliente | % sobre o preço; negativo = ágio |
| `minimalInitialInvestment` | Qtd. mínima | aplicação mínima. A página rotula como quantidade, mas o valor bate com R$ (25.000 cotas × R$ 100,55 ≈ 2.500.000) |
| `minimumQuotaQuantity` | — | mínimo em cotas |
| `isQualifiedInvestor`, `isProfessionalInvestor` | — | público-alvo exigido pela oferta |
| `tags` | selo na linha | restrições como "Dinheiro novo" e "Unique"; registre o `title` como ressalva |
| `profitability12Gross`, `dividendYield12` | Rentab. bruta, DY (12M) | contexto da oferta |

Números vêm como texto no formato brasileiro (`"1.234,56"`), exceto `profitability*Gross`, que usa ponto.

`isInvestmentBlocked` vem `true` mesmo para fundos com **Comprar** ativo: refere-se à aplicação primária. Não usar para disponibilidade.

## Disponibilidade

Cada fonte de oferta (`stockOfTreasuryQuotas`, `stockOfPeerToPeerQuotas`) tem estoque quando a quantidade é maior ou igual a `minimumQuotaQuantity` (sem mínimo informado: maior que zero). Quantidade acima de zero e abaixo do mínimo é **estoque residual**: não atende a aplicação mínima e conta como sem estoque. Um fundo está **disponível** quando ao menos uma fonte tem estoque. Para cada fonte com estoque, registre quantidade, deságio/ágio e valor disponível (quantidade × preço unitário). Não aplique o deságio ao preço: o preço efetivo da ordem sai na plataforma. Sem estoque nas duas fontes, o fundo está **indisponível**; cite o estoque residual nas ressalvas.
