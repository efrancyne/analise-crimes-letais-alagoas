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

## Estrutura sugerida do repositório

```text
analise_CVLI/
├── README.md
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── scripts/
├── reports/
└── visualizations/
```

## Observações

- Este projeto tem caráter analítico e de divulgação de informações públicas.
- Os dados devem ser tratados com atenção à qualidade, consistência e atualização da base.
- O foco principal é a transparência e a compreensão do contexto de violência letal em Alagoas.

## Objetivo de comunicação

A pesquisa busca oferecer uma leitura mais simples e visual dos dados, permitindo que a população compreenda melhor o comportamento dos crimes violentos letais intencionais no estado e entenda se as tendências estão se alterando de forma desigual entre as cidades e grupos sociais.

## Conclusão

A análise de CVLI em Alagoas pode contribuir para a produção de conhecimento sobre a violência letal no estado, auxiliando na tomada de decisão, na formulação de políticas públicas e na compreensão de padrões que impactam diretamente a sociedade alagoana.
