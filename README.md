# Agente de Análise de SRAG com Múltiplos Agentes

## Visão Geral do Projeto

Este projeto é uma Prova de Conceito (PoC) de um sistema de Inteligência Artificial avançado, projetado para auxiliar profissionais de saúde no monitoramento da **Síndrome Respiratória Aguda Grave (SRAG)**. A solução utiliza uma arquitetura de múltiplos agentes para automatizar a geração de relatórios complexos, combinando dados epidemiológicos, notícias em tempo real e protocolos clínicos.

O agente principal, atuando como um orquestrador, consulta dados, calcula métricas, busca contexto na web, delega tarefas de pesquisa a sub-agentes especialistas e, finalmente, gera um relatório analítico completo, com gráficos e um PDF para download.

---

## Principais Funcionalidades

- **Pipeline de Dados Parametrizado:** Limpeza e preparação automatizada dos dados brutos do OpenDataSUS, com regras de negócio centralizadas em um arquivo de configuração.
- **Análise de Dados Dinâmica:** As métricas e gráficos são gerados dinamicamente para a localidade solicitada (Brasil, Estado ou Cidade).
- **Arquitetura de Múltiplos Agentes (LangGraph):** Um agente Orquestrador gerencia o fluxo de trabalho e delega tarefas para sub-agentes especialistas, como o de pesquisa de protocolos clínicos.
- **Geração Aumentada por Recuperação (RAG):** O agente enriquece sua análise consultando notícias em tempo real com a API da Tavily, fornecendo contexto para os dados numéricos.
- **Sistema de LLM Resiliente com Fallback:** O agente tenta usar APIs rápidas na nuvem (Google Gemini, Groq) e, em caso de falha ou limite de cota, recorre automaticamente a um modelo open-source rodando localmente (Ollama), garantindo que a aplicação nunca pare de funcionar.
- **Geração de Artefatos:** O sistema produz múltiplos outputs: um relatório em texto, gráficos de evolução diária e mensal, e um relatório final consolidado em formato PDF.
- **Interface Conversacional:** Uma aplicação web interativa construída com Streamlit permite que o usuário solicite relatórios e faça perguntas de acompanhamento sobre os resultados.

---

## Diagrama da Arquitetura

---

## Tecnologias Utilizadas

- **Linguagem:** Python 3.9+
- **Orquestração de Agentes:** LangChain & LangGraph
- **Modelos de Linguagem (LLMs):** Google Gemini, Groq (Llama 3.1)
- **Análise de Dados:** Pandas
- **Busca na Web:** Tavily Search API
- **Interface Web:** Streamlit
- **Geração de Gráficos:** Matplotlib
- **Geração de PDF:** fpdf2
- **Gerenciamento de Dependências:** Pip & Venv

---

## Guia de Instalação e Execução

Siga estes passos detalhados para configurar e executar o projeto em sua máquina local.

### 1. Pré-requisitos

- Python 3.9 ou superior instalado.
- Git para clonar o repositório.

### 2. Clonando o Repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DA_PASTA_DO_PROJETO>
3. Configurando o Ambiente Virtual
É crucial usar um ambiente virtual para isolar as dependências do projeto.

Bash

python -m venv .venv

# No Windows (PowerShell):
.venv\Scripts\Activate.ps1
# No macOS/Linux:
source .venv/bin/activate
4. Instalando as Dependências
Com o ambiente ativado, instale todas as bibliotecas necessárias.

Bash

pip install -r requirements.txt
5. Configurando as Chaves de API
O agente precisa de chaves de API para se conectar aos serviços externos.

Na raiz do projeto, crie um arquivo chamado .env.

Adicione as seguintes chaves ao .env, substituindo pelos seus valores:

# Chave para a busca de notícias ([https://tavily.com/](https://tavily.com/))
TAVILY_API_KEY="tvly-..."
# Chave para o LLM do Google ([https://aistudio.google.com/](https://aistudio.google.com/))
GOOGLE_API_KEY="AIza..."
# Chave para o LLM rápido da Groq ([https://console.groq.com/](https://console.groq.com/))
GROQ_API_KEY="gsk_..."

6. (Opcional) Configurando o Fallback Local com Ollama
Para garantir que o agente sempre funcione, mesmo que as APIs da nuvem falhem, configure o Ollama:

Bash

# Este comando irá baixar o modelo Llama 3 8B e o deixará pronto para uso
ollama run llama3:8b-instruct-q4_K_M
Como Usar o Projeto
Existem duas maneiras principais de interagir com o projeto:

1. Processamento dos Dados (ETL)
Sempre que o arquivo de dados brutos (data/raw/OpenSUS.csv) for atualizado, você precisa executar o pipeline de processamento para gerar a versão limpa dos dados.

Bash

python main.py
Este comando irá ler os dados brutos, aplicar todas as regras de limpeza, normalização e enriquecimento, e salvar o resultado em data/processed/OpenSUS_limpo.csv.

2. Executando a Aplicação Principal (Streamlit)
Esta é a forma principal de interagir com o agente.

Bash

streamlit run app.py
Este comando iniciará o servidor web e abrirá a interface do chatbot no seu navegador. A partir daí, você pode solicitar relatórios para diferentes localidades (ex: "São Paulo", "SC", "Fortaleza, CE", "Brasil").

Estrutura do Projeto
A estrutura de pastas foi projetada para ser modular e escalável, seguindo os princípios de Clean Code.

├── data/                    # Armazena os datasets
│   ├── processed/           # Dados limpos e prontos para análise
│   └── raw/                 # Dados brutos originais
├── output/                  # Onde os gráficos e PDFs gerados são salvos
├── src/                     # Contém todo o código-fonte da aplicação
│   ├── agents/              # Módulos dos agentes de IA
│   │   ├── clinical_protocols_agent/ # Sub-agente especialista em protocolos
│   │   ├── orchestrator/          # O agente principal que gerencia o fluxo
│   │   └── pdf_generator_agent/ # Módulo especialista em criar PDFs
│   ├── tools/               # Ferramentas reutilizáveis (ex: busca de notícias)
│   ├── config.py            # Arquivo central de configurações e parâmetros
│   ├── data_processor.py    # Pipeline de limpeza e preparação dos dados (ETL)
│   ├── llm_provider.py      # Lógica de fallback de LLMs (Gemini -> Groq -> Ollama)
│   ├── metrics_calculator.py # Classe especialista em calcular métricas
│   └── plot_generator.py    # Classe especialista em gerar gráficos
├── .env                     # Arquivo local para armazenar chaves de API (NÃO ENVIAR PARA O GITHUB)
├── .gitignore               # Especifica arquivos a serem ignorados pelo Git
├── app.py                   # Ponto de entrada da interface do usuário (Streamlit)
├── requirements.txt         # Lista de dependências Python do projeto
└── run_processing.py        # Script para executar o pipeline de ETL

Onde Fazer Alterações
Para adicionar novas colunas do CSV: Altere src/config.py na seção relevant_features.
Para adicionar novas métricas: Altere src/metrics_calculator.py adicionando um novo método de cálculo, e depois chame este método no calculate_metrics_node em src/agents/orchestrator/agent.py.
Para mudar o texto do relatório: Altere o final_report_prompt no arquivo src/agents/orchestrator/prompts.py.
```
