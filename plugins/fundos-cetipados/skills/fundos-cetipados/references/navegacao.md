# Navegação: prateleira do secundário XP

> **Rascunho.** Os campos e a estrutura da página ainda não foram conferidos com o Hub logado. Na primeira execução, registre aqui o que a página realmente mostra.

## Acesso

- URL: `https://hub.xpi.com.br/new/fundos-de-investimento#/secundario/prateleira`. A URL pode mudar: se não abrir, entre pelo Hub em Fundos de Investimento › Secundário › Prateleira.
- Use o Chrome em que o assessor já está logado no Hub. Tela de login aparecendo: pare e peça ao assessor que entre. Nunca digite a senha.
- Somente leitura: extraia texto com `get_page_text` ou `read_page`. Clique só em filtros, abas, paginação ou para expandir detalhes.

## O que coletar por fundo

Para cada fundo de `config/aprovados.csv` elegível pelo público-alvo:

- se há oferta disponível na prateleira;
- dados da oferta que a página mostrar: preço/cota, deságio ou ágio, quantidade ou valor disponível, aplicação mínima, data da oferta.

Identificar o fundo pelo nome ou pelo ticker (prefixo `XXXX11`, quando houver). Nome divergente do `aprovados.csv`: case pelo CNPJ, se a página mostrar, ou marque como lacuna.

Fundo da prateleira que não está em `aprovados.csv` fica fora da sugestão. Liste à parte só se for relevante para a lacuna de alocação.
