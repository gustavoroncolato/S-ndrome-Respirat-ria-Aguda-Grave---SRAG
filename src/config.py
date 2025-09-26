from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CATEGORICAL_MAPPING_CONFIG = {
    "sim_nao_ignorado": { 1: "Sim", 2: "Não", 9: "Ignorado" },
    "sexo": { "M": "Masculino", "F": "Feminino", "I": "Ignorado" },
    "evolucao_caso": { 1: "Cura", 2: "Óbito", 9: "Ignorado" },
    "suporte_ventilatorio": { 1: "Sim, invasivo", 2: "Sim, não invasivo", 3: "Não", 9: "Ignorado" },
    "raca": { 1: "Branca", 2: "Preta", 3: "Amarela", 4: "Parda", 5: "Indígena", 9: "Ignorado" },
    "gestante": { 1: "1º Trimestre", 2: "2º Trimestre", 3: "3º Trimestre", 4: "Idade gestacional ignorada", 5: "Não", 6: "Não se aplica", 9: "Ignorado" },
    "classificacao_final": { 1: "SRAG por Influenza", 2: "SRAG por Outro Vírus Respiratório", 3: "SRAG por Outro Agente Etiológico", 4: "SRAG não especificado", 5: "SRAG por COVID-19" }
}

DATA_PROCESSING_CONFIG = {
    "file_path": PROJECT_ROOT / "data" / "raw" / "OpenSUS.csv",
    "output_file_path": PROJECT_ROOT / "data" / "processed" / "OpenSUS_limpo.csv",
    "separator": ";",

    "relevant_features": [
        "DT_NOTIFIC", "DT_SIN_PRI", "SEM_NOT", "SG_UF_NOT", "ID_MUNICIP",
        "CS_SEXO", "DT_NASC", "NU_IDADE_N", "CS_RACA", "CS_GESTANT", "FEBRE",
        "TOSSE", "DISPNEIA", "DESC_RESP", "SATURACAO", "FATOR_RISC",
        "CARDIOPATI", "DIABETES", "OBESIDADE", "HOSPITAL", "DT_INTERNA",
        "UTI", "DT_ENTUTI", "SUPORT_VEN", "CLASSI_FIN", "PCR_SARS2",
        "EVOLUCAO", "DT_EVOLUCA", "VACINA_COV",
        "TP_IDADE", 
        "VACINA",  
    ],

    "column_rename_map": {
        "DT_NOTIFIC": "data_notificacao", "DT_SIN_PRI": "data_primeiros_sintomas",
        "SEM_NOT": "semana_notificacao", "SG_UF_NOT": "uf_notificacao",
        "ID_MUNICIP": "municipio_notificacao", "CS_SEXO": "sexo",
        "DT_NASC": "data_nascimento", "NU_IDADE_N": "idade",
        "CS_RACA": "raca", "CS_GESTANT": "gestante",
        "DESC_RESP": "desconforto_respiratorio", "SATURACAO": "saturacao_menor_95",
        "FATOR_RISC": "possui_fator_risco", "CARDIOPATI": "possui_cardiopatia",
        "DIABETES": "possui_diabetes", "OBESIDADE": "possui_obesidade",
        "HOSPITAL": "foi_internado", "DT_INTERNA": "data_internacao",
        "UTI": "internado_uti", "DT_ENTUTI": "data_entrada_uti",
        "SUPORT_VEN": "suporte_ventilatorio", "CLASSI_FIN": "classificacao_final",
        "PCR_SARS2": "resultado_pcr_sars2", "EVOLUCAO": "evolucao_caso",
        "DT_EVOLUCA": "data_evolucao", "VACINA_COV": "vacinado_covid",
        "TP_IDADE": "tipo_idade",
        "VACINA": "vacinado_gripe",
    },

    "date_columns": [
        "data_notificacao", "data_primeiros_sintomas", "data_nascimento",
        "data_internacao", "data_entrada_uti", "data_evolucao",
    ],
    "data_types": {
        "idade": "Int64", "semana_notificacao": "Int64", "tipo_idade": "Int64"
    },

    "categorical_maps": {
        "foi_internado": CATEGORICAL_MAPPING_CONFIG["sim_nao_ignorado"],
        "internado_uti": CATEGORICAL_MAPPING_CONFIG["sim_nao_ignorado"],
        "possui_fator_risco": CATEGORICAL_MAPPING_CONFIG["sim_nao_ignorado"],
        "vacinado_covid": CATEGORICAL_MAPPING_CONFIG["sim_nao_ignorado"],
        "vacinado_gripe": CATEGORICAL_MAPPING_CONFIG["sim_nao_ignorado"],
        "FEBRE": CATEGORICAL_MAPPING_CONFIG["sim_nao_ignorado"],
        "TOSSE": CATEGORICAL_MAPPING_CONFIG["sim_nao_ignorado"],
        "DISPNEIA": CATEGORICAL_MAPPING_CONFIG["sim_nao_ignorado"],
        "desconforto_respiratorio": CATEGORICAL_MAPPING_CONFIG["sim_nao_ignorado"],
        "saturacao_menor_95": CATEGORICAL_MAPPING_CONFIG["sim_nao_ignorado"],
        "possui_cardiopatia": CATEGORICAL_MAPPING_CONFIG["sim_nao_ignorado"],
        "possui_diabetes": CATEGORICAL_MAPPING_CONFIG["sim_nao_ignorado"],
        "possui_obesidade": CATEGORICAL_MAPPING_CONFIG["sim_nao_ignorado"],
        "sexo": CATEGORICAL_MAPPING_CONFIG["sexo"],
        "evolucao_caso": CATEGORICAL_MAPPING_CONFIG["evolucao_caso"],
        "suporte_ventilatorio": CATEGORICAL_MAPPING_CONFIG["suporte_ventilatorio"],
        "raca": CATEGORICAL_MAPPING_CONFIG["raca"],
        "gestante": CATEGORICAL_MAPPING_CONFIG["gestante"],
        "classificacao_final": CATEGORICAL_MAPPING_CONFIG["classificacao_final"]
    }
}