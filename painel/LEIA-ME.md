# Painel de CVLI em Alagoas

Painel interativo alimentado pelo portal Alagoas em Dados.

## Como rodar

Na raiz do projeto:

```bash
pip install -r requirements-painel.txt
streamlit run painel/app.py
```

O navegador abre em http://localhost:8501.

## Como os dados chegam

- A API CKAN do portal (`package_show`) informa qual é o arquivo CSV mais recente do dataset de CVLI e quando ele foi atualizado.
- Os dados só são baixados de novo quando essa data muda. A página confere a API a cada 5 minutos e se recarrega sozinha se houver novidade. Há também o botão "Verificar atualização agora".
- O portal publica em lotes, então "ao vivo" significa a versão mais recente publicada, não eventos em tempo real.

## Por que as datas vêm do CSV e não do `datastore_search`

O datastore do portal lê `DATA DO FATO` com mês e dia trocados quando o dia é 12 ou menos (03/01/2012 vira 2012-03-01). Isso atinge cerca de 39% dos registros e estraga análises mensais e diárias; os anos não mudam. As datas são lidas do texto original do CSV (99,986% iguais às do CSV usado nos notebooks).

## População

O mapa e as taxas por 100 mil habitantes usam `dados_brutos/populacao_municipios_AL.csv` (IBGE), gerado pelo notebook 03. Sem esse arquivo, o painel mostra um aviso no lugar do mapa.

## Visual

- **Abertura em tela cheia.** O topo é um bloco escuro com o mapa de calor de Alagoas à direita e, à esquerda, o título com a palavra "letais" em destaque, um cartão "Perfil dos crimes" com 5 mensagens calculadas sobre o período do mapa e os filtros (parcela de mortes por arma de fogo, à noite, em vias públicas, de homens e de vítimas de 18 a 34 anos; sempre sobre os casos com a informação preenchida), e um mini-ranking. Os totais e variações ficam só na faixa de indicadores de baixo, para não repetir. Uma faixa de 6 indicadores de mesmo tamanho fica na base do bloco. Ao clicar em um município, a manchete dá lugar aos dados dele. Resumo do período, ranking de taxas e vítimas por ano vêm logo abaixo. No celular o bloco vira uma coluna de ponta a ponta (filtros, título, manchete, mapa, seletor de município com o cartão de detalhe, ranking, indicadores). Como municípios pequenos são difíceis de acertar com o dedo, há uma lista "Ver um município" logo abaixo do mapa: tocar no mapa preenche a lista, e escolher na lista destaca o município no mapa. O tooltip é curto (2 linhas) e o arrasto do mapa fica desligado para não atrapalhar a rolagem da página. O formato depende só da **largura da tela** (900 px ou menos = celular): a página gera os dois mapas e o CSS mostra o certo, então também funciona em janela estreita de computador ou ao girar o aparelho. A lista de municípios é a fonte única da seleção nos dois formatos.
- **Mapa de calor de Alagoas como elemento principal.** Cada um dos 102 municípios é pintado de um vermelho mais intenso quanto maior o valor. Por padrão a cor é a **taxa de vítimas por 100 mil habitantes por ano** (permite comparar cidades de tamanhos diferentes); dá para trocar para o número de vítimas. O período do mapa é escolhido no menu: últimos 12 meses (padrão), últimos 3 anos ou todo o período.
- A escala de cor é limitada ao percentil 95 dos municípios, para que uma capital muito acima dos demais não apague a diferença entre os outros. Municípios com menos de 5 casos mostram o aviso "taxa instável" ao passar o mouse.
- No topo, cinco cartões de tamanho igual (vítimas e feminicídios nos últimos 12 meses, último mês, taxa do estado e comparação com 2013). Ao lado do mapa, um resumo do período e o ranking.
- Ao passar o mouse em um município aparecem as vítimas, a taxa, o **intervalo de confiança de 95%** da taxa e avisos quando ela é instável (poucos casos ou município pequeno): em cidades de menos de 10 mil habitantes, uma única vítima pode mudar a taxa em mais de 10 por 100 mil.
- Clique em um município para ver as vítimas e a taxa dele e o histórico por ano. Os demais gráficos (evolução, horário e local, perfil, tabela de municípios) ficam abaixo, em abas.
- Todos os filtros ficam num único menu suspenso, no botão "Filtros" do topo.
- Vermelho vivo (`#e11d2e`) como cor principal; azul e verde-água só quando um gráfico precisa de 2 ou 3 séries. Temas claro e escuro seguem o sistema.
- O tema do Streamlit está em `.streamlit/config.toml`, na raiz do projeto, por isso o painel deve ser iniciado da raiz.

## Arquivos

- `app.py`: interface (Streamlit + Plotly)
- `dados.py`: consulta à API, download, limpeza e agrupamentos
- `assets/alagoas_municipios.geojson`: contorno dos municípios (malha do IBGE; baixada automaticamente se faltar)
- `assets/favicon.png`: ícone da aba do navegador (silhueta de Alagoas em vermelho)
