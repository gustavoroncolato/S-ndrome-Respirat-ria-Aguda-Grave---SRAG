from langchain_core.prompts import ChatPromptTemplate

# O prompt principal para a geração do relatório final, agora enriquecido
final_report_prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um analista de dados de saúde especialista em doenças respiratórias. Sua tarefa é gerar um relatório aprofundado e informativo sobre o cenário da Síndrome Respiratória Aguda Grave (SRAG), utilizando todas as métricas disponíveis."),
    ("human", """
    Por favor, gere um relatório completo e aprofundado sobre a SRAG com base em todos os dados coletados. No seu texto, mencione que os gráficos com a evolução diária e mensal dos casos foram gerados como parte desta análise.

    **Tópico da Análise:** {topic}

    **Métricas Principais (últimos dados disponíveis):**
    - Taxa de Mortalidade (Letalidade): {metrics_mortality}%
    - Percentual de Internados em UTI: {metrics_uti}%
    - Percentual de Pacientes Vacinados: {metrics_vacinacao}%
    - Variação Semanal de Casos: {metrics_aumento_casos}%
    - Tempo Médio para Notificação: {metrics_notification_time} dias
    - Proporção de Casos por Causa: {metrics_proportions}
    - Letalidade por Faixa Etária (%): {metrics_lethality_by_age}
    - % de Pacientes em UTI com Ventilação Invasiva: {metrics_invasive_ventilation}%

    **Contexto das Notícias Recentes:**
    {news_context}

    **Resumo de Protocolos Clínicos Relevantes:**
    {protocols_context}

    **ESTRUTURA DO RELATÓRIO APRIMORADA**
    1.  **Resumo Executivo:** Um parágrafo inicial com sua interpretação do cenário geral, combinando as métricas principais, as notícias e os insights mais importantes das métricas detalhadas (ex: qual vírus predomina ou qual faixa etária está em maior risco).
    2.  **Análise Epidemiológica:**
        - **Métricas Gerais:** Explique o significado das 4 métricas principais.
        - **Perfil dos Casos:** Analise a 'Proporção de Casos por Causa'. Qual vírus (COVID-19, Influenza, etc.) está impulsionando os casos de SRAG na região?
    3.  **Análise de Risco e Gravidade:**
        - **Grupos Vulneráveis:** Analise a 'Letalidade por Faixa Etária', destacando os grupos de maior risco.
        - **Gravidade dos Casos Críticos:** Comente sobre a '% de Pacientes em UTI com Ventilação Invasiva' como um indicador da severidade dos casos que necessitam de cuidados intensivos.
    4.  **Análise Operacional do Sistema de Saúde:**
        - Comente sobre o 'Tempo Médio para Notificação'. Um tempo alto pode indicar demoras no diagnóstico ou na busca por atendimento? Um tempo baixo é um bom sinal?
    5.  **Contexto Atual e Protocolos:**
        - Use as notícias para dar contexto aos números e tendências observadas.
        - Apresente os resumos de tratamentos encontrados pelo sub-agente.
    6.  **Conclusão e Recomendações:** Um parágrafo final com as principais conclusões da análise completa e possíveis recomendações.

    O relatório deve ser claro, objetivo e escrito em português do Brasil.
    """),
])

# O prompt de extração de doenças 
disease_extraction_prompt = ChatPromptTemplate.from_template(
    "Leia o seguinte conjunto de notícias e liste as principais doenças respiratórias mencionadas (como 'Influenza A', 'Vírus Sincicial Respiratório', 'Covid-19'). Responda apenas com os nomes das doenças, separados por vírgula. Notícias: {news}"
)