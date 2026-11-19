# Análise de Crimes Violentos Letais Intencionais (CVLI) em Alagoas

Este projeto tem como objetivo analisar o cenário de Crimes Violentos Letais Intencionais (CVLI) no estado de Alagoas, utilizando a base de microdados disponibilizada pela Secretaria de Segurança Pública de Alagoas, acessível no portal Alagoas em Dados.

A proposta da pesquisa é transformar dados públicos em informação acessível para a população, permitindo identificar padrões, tendências e desigualdades no fenômeno de violência letal no estado.

## Objetivo geral

Analisar a evolução dos crimes violentos letais intencionais em Alagoas e identificar padrões relacionados a:

- variação temporal dos casos;
- diferenças entre municípios;
- concentração territorial;
- perfil das vítimas e dos agressores;
- ocorrência por período do dia;
- natureza dos locais (público ou privado);
- evolução dos feminicídeos em relação ao total de homicídios.

## Perguntas de pesquisa

A análise busca responder as seguintes questões:

1. A diminuição dos crimes letais intencionais foi homogênea entre as cidades de Alagoas?
2. O número de feminicídios acompanhou essa diminuição nos últimos 13 anos?
3. Os crimes ocorreram mais em determinados horários do dia, como durante a noite?
4. Os casos foram mais frequentes em áreas públicas ou em locais privados?
5. Há diferenças relevantes entre municípios com maior e menor incidência de CVLI?
6. Existe alguma tendência temporal ou regional que indique concentração espacial da violência letal?

## Fonte de dados

- Base: CVLI AL - Base de Microdados
- Órgão responsável: Secretaria de Segurança Pública de Alagoas
- Plataforma: Alagoas em Dados

A base será utilizada como fonte principal para a coleta, limpeza, tratamento e análise dos dados.

## Escopo do projeto

O projeto será desenvolvido com foco em:

- organização e limpeza dos microdados;
- análise exploratória dos indicadores;
- comparação temporal entre anos;
- comparação intermunicipal;
- identificação de padrões por horário, local e tipo de crime;
- criação de visualizações simples e compreensíveis para a população;
- apresentação dos resultados em linguagem acessível e informativa.

## Metodologia

A metodologia do projeto incluirá as seguintes etapas:

1. Coleta dos dados públicos da base de microdados da Segurança Pública de Alagoas.
2. Revisão e compreensão da estrutura das variáveis disponíveis.
3. Limpeza dos dados, incluindo padronização, exclusão de inconsistências e tratamento de valores ausentes.
4. Seleção das variáveis relevantes para a análise de CVLI.
5. Exploração dos dados por município, ano, faixa etária, sexo, horário, local e tipo de crime.
6. Identificação de tendências e padrões estatísticos.
7. Construção de gráficos e dashboards com foco em comunicação clara.
8. Interpretação dos resultados e elaboração de conclusões.



## Produtos esperados

O resultado final da pesquisa deve incluir:

- análise descritiva dos dados;
- gráficos e visualizações de tendências;
- comparação entre municípios e anos;
- painel ou relatório visual acessível;
- síntese dos principais achados para a população e para gestores públicos.

## Objetivo de comunicação

A pesquisa busca oferecer uma leitura mais simples e visual dos dados, permitindo que a população compreenda melhor o comportamento dos crimes violentos letais intencionais no estado e entenda se as tendências estão se alterando de forma desigual entre as cidades e grupos sociais.

## Como reproduzir

1. Baixe o CSV de microdados do dataset "CVLI AL - Base de Microdados" no portal Alagoas em Dados e salve como `dados_brutos/cvli_dados.csv` (o arquivo não é versionado).
2. Instale as dependências dos notebooks:

   ```bash
   pip install -r requirements.txt
   ```

3. Rode os notebooks em ordem, de dentro da pasta `notebooks/`:
   - `01_pre_processamento.ipynb`: leitura e limpeza da base;
   - `02_analise_exploratoria.ipynb`: recorte de 2013 a 2025, análise descritiva e testes de hipóteses; gera `dados_tratados/`;
   - `03_analise_populacional.ipynb`: taxas por 100 mil habitantes; gera `dados_brutos/populacao_municipios_AL.csv`.
4. Gráficos da apresentação (opcional), a partir da raiz do projeto:

   ```bash
   python apresentacao/graficos_slides.py
   ```

   Os PNGs saem em `apresentacao/graficos/` e os números principais são impressos no terminal.
5. Painel interativo: ver `painel/LEIA-ME.md`.

## Principais resultados (2013 a 2025)

Base de 18.741 vítimas, com população municipal do IBGE.

- O número de vítimas caiu de 2.247 (2013) para 950 (2025), queda de 57,7%. A taxa passou de 68,1 para 29,5 por 100 mil habitantes.
- A queda não foi homogênea: entre os 24 municípios com pelo menos 150 vítimas, a taxa caiu de 72,6% (Pilar) a 5,6% (Campo Alegre), comparando 2013-15 com 2023-25. No estado, a queda foi de 46,3%.
- Entre os municípios com 20 mil habitantes ou mais, a taxa média de 2023-25 vai de 7,2 (Feira Grande) a 61,2 (Rio Largo) por 100 mil.
- A taxa de vítimas mulheres caiu menos que a dos homens (31,7% contra 47,2%).
- 42,1% das vítimas foram mortas entre 18h e 23h.

## Equipe

Trabalho da disciplina Ciência dos Dados e Inteligência Empresarial (Sistemas de Informação, UFAL).

- Elysa Francyne dos Santos
- Joao Gaudencio Soares Costa
- José Gabriel Fideles Silva
- Sophia Sacramento dos Santos

## Conclusão

A análise de CVLI em Alagoas pode contribuir para a produção de conhecimento sobre a violência letal no estado, auxiliando na tomada de decisão, na formulação de políticas públicas e na compreensão de padrões que impactam diretamente a sociedade alagoana.
