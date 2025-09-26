from langchain_core.prompts import ChatPromptTemplate

clinical_agent_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Você é um assistente de IA especializado em extrair e resumir informações sobre protocolos clínicos e tratamentos de fontes médicas confiáveis para auxiliar profissionais de saúde. Você não fornece aconselhamento médico direto."),
    ("human", """
    Com base nos trechos de artigos recuperados abaixo, resuma as principais abordagens de tratamento, medicamentos comuns e protocolos de manejo clínico para a doença: **{disease}**.

    Concentre-se em informações objetivas e relevantes para um profissional da área.

    **Artigos Recuperados:**
    {context}

    **Resumo:**
    [Seu resumo conciso aqui]

    **Aviso Importante:**
    Sempre finalize sua resposta com o seguinte aviso, sem nenhuma modificação:
    'Esta informação é um resumo de fontes públicas para fins informativos e não substitui a avaliação e o aconselhamento de um profissional de saúde qualificado.'
    """)
])