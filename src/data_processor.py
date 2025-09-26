import pandas as pd
from typing import Dict, Any
import os

class SragDataProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.df = None

    def load_data(self) -> "SragDataProcessor":
        """Carrega os dados do arquivo CSV especificado na configuração."""
        try:
            file_path = self.config["file_path"]
            separator = self.config.get("separator", ",")
            print(f"Carregando dados de: {file_path}")
            self.df = pd.read_csv(file_path, sep=separator, low_memory=False, encoding='ISO-8859-1')
            print(" Dados carregados com sucesso.")
            return self
        except FileNotFoundError:
            print(f"ERRO: Arquivo {file_path} não foi encontrado.")
            raise
        except Exception as e:
            print(f"ERRO inesperado ao carregar dados: {e}")
            raise

    def select_and_rename_features(self) -> "SragDataProcessor":
        """Seleciona as colunas relevantes e as renomeia."""
        print("Selecionando e renomeando features")
        relevant_features = self.config["relevant_features"]
        rename_map = self.config["column_rename_map"]
        
        existing_features = [col for col in relevant_features if col in self.df.columns]
        self.df = self.df[existing_features].copy()
        self.df.rename(columns=rename_map, inplace=True)

        print("Features selecionadas e renomeadas.")
        return self

    def clean_and_convert_types(self) -> "SragDataProcessor":
        """Limpa, converte tipos de dados e decodifica variáveis categóricas."""
        print("Limpando e convertendo tipos de dados")
        
        date_columns = self.config.get("date_columns", [])
        for col in date_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
        
        categorical_maps = self.config.get("categorical_maps", {})
        for col, mapping in categorical_maps.items():
            if col in self.df.columns:
                self.df[col] = self.df[col].map(mapping)
        
        data_types = self.config.get("data_types", {})
        for col, dtype in data_types.items():
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').astype(dtype)
        
        print("Tipos de dados convertidos e normalizados.")
        return self
    
    def _normalize_age(self) -> "SragDataProcessor":
        """
        Converte as idades para anos com base na coluna 'tipo_idade'
        e cria a nova coluna 'idade_anos_corrigida'.
        """
        print("Normalizando idades para anos...")
        if 'idade' not in self.df.columns or 'tipo_idade' not in self.df.columns:
            print("Colunas 'idade' ou 'tipo_idade' não encontradas. Pulando normalização.")
            self.df['idade_anos_corrigida'] = self.df.get('idade', pd.Series(dtype=float))
            return self

        def convert_age(row):
            age, age_type = row['idade'], row['tipo_idade']
            if pd.isna(age) or pd.isna(age_type): return age
            if age_type == 1: return age / 365.25 
            if age_type == 2: return age / 12    
            return age

        self.df['idade_anos_corrigida'] = self.df.apply(convert_age, axis=1)
        print("Coluna 'idade_anos_corrigida' criada com sucesso.")
        return self

    def handle_missing_values(self) -> "SragDataProcessor":
        """Trata valores ausentes (NaN/NaT) no DataFrame."""
        print("Tratando valores ausentes")
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        fill_value = "Não Informado"
        self.df[categorical_cols] = self.df[categorical_cols].fillna(fill_value)
        print(f"Valores nulos em colunas categóricas preenchidos com '{fill_value}'.")
        return self

    def save_processed_data(self) -> "SragDataProcessor":
        """Salva o DataFrame processado em um novo arquivo CSV."""
        if self.df is None: raise ValueError("Não há dados para salvar.")
        print("Salvando dados limpos")
        output_path = self.config["output_file_path"]
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.df.to_csv(output_path, index=False, sep=';', encoding='utf-8')
        print(f"Arquivo limpo salvo em: {output_path}")
        return self

    def run_pipeline(self) -> pd.DataFrame:
        """Orquestra e executa o pipeline completo de preparação de dados."""
        print("\nINICIANDO PIPELINE DE PREPARAÇÃO DE DADOS")
        (self.load_data()
             .select_and_rename_features()
             .clean_and_convert_types()
             ._normalize_age()
             .handle_missing_values())
        print("PIPELINE DE PREPARAÇÃO DE DADOS FINALIZADO\n")
        return self.df