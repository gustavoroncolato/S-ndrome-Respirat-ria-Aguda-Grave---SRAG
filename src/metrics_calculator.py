import pandas as pd
from pathlib import Path
from typing import Optional, Dict
from unidecode import unidecode
from src.config import CATEGORICAL_MAPPING_CONFIG

# State para siglas dos estados
STATE_MAP = {
    "acre": "AC", "alagoas": "AL", "amapa": "AP", "amazonas": "AM", "bahia": "BA",
    "ceara": "CE", "distrito federal": "DF", "espirito santo": "ES", "goias": "GO",
    "maranhao": "MA", "mato grosso": "MT", "mato grosso do sul": "MS", "minas gerais": "MG",
    "para": "PA", "paraiba": "PB", "parana": "PR", "pernambuco": "PE", "piaui": "PI",
    "rio de janeiro": "RJ", "rio grande do norte": "RN", "rio grande do sul": "RS",
    "rondonia": "RO", "roraima": "RR", "santa catarina": "SC", "sao paulo": "SP",
    "sergipe": "SE", "tocantins": "TO"
}

class MetricsCalculator:
    def __init__(self, cleaned_data_path: Path, location: str = "Brasil", city: Optional[str] = None):
        self.file_path = cleaned_data_path
        self.location = location
        self.city = city
        self.df = self._load_and_filter_data()

    def _get_uf_from_location(self, location_str: str) -> str:
        normalized_location = unidecode(location_str.lower().strip())
        if normalized_location in STATE_MAP:
            return STATE_MAP[normalized_location]
        return location_str.strip().upper()

    def _load_and_filter_data(self) -> pd.DataFrame:
        print(f"Carregando e filtrando dados para: Localidade='{self.location}', Cidade='{self.city}'")
        try:
            date_cols = ['data_notificacao', 'data_primeiros_sintomas', 'data_nascimento',
                         'data_internacao', 'data_entrada_uti', 'data_evolucao']
            full_df = pd.read_csv(self.file_path, sep=';', parse_dates=date_cols, encoding='utf-8')
            state_df = full_df
            location_upper = self.location.strip().upper()
            if location_upper not in ["BRASIL", "BR"]:
                target_uf = self._get_uf_from_location(self.location)
                state_df = full_df[full_df['uf_notificacao'].str.upper() == target_uf].copy()
            if self.city:
                city_normalized = unidecode(self.city.lower().strip())
                state_df['municipio_notificacao'] = state_df['municipio_notificacao'].astype(str)
                final_df = state_df[state_df['municipio_notificacao'].str.lower().apply(unidecode) == city_normalized].copy()
                if final_df.empty: 
                    print(f"   AVISO: Nenhum dado para a cidade '{self.city}'.")
                else: 
                    print(f"  Dados filtrados. {len(final_df)} registros para '{self.city}, {self.location}'.")
                return final_df
            if state_df.empty: 
                print(f"AVISO: Nenhum dado para a localidade '{self.location}'.")
            else: 
                print(f"  Dados filtrados. {len(state_df)} registros para '{self.location}'.")
            return state_df
        except Exception as e:
            print(f"ERRO ao carregar e filtrar dados: {e}")
            raise

    def get_daily_cases(self, days: int = 30) -> pd.Series:
        if self.df.empty or self.df['data_notificacao'].isnull().all(): 
            return pd.Series(dtype=float)
        last_date = self.df['data_notificacao'].max()
        start_date = last_date - pd.Timedelta(days=days)
        recent_cases_df = self.df[self.df['data_notificacao'] >= start_date]
        return recent_cases_df.groupby('data_notificacao').size()

    def get_monthly_cases(self, months: int = 12) -> pd.Series:
        if self.df.empty or self.df['data_notificacao'].isnull().all(): 
            return pd.Series(dtype=float)
        df_temp = self.df.set_index('data_notificacao')
        monthly_counts = df_temp.resample('ME').size()
        return monthly_counts.tail(months)

    def calculate_mortality_rate(self) -> float:
        if self.df.empty: 
            return 0.0
        known_outcomes = self.df[self.df['evolucao_caso'].isin(['Cura', 'Óbito'])]
        if known_outcomes.empty: 
            return 0.0
        deaths = (known_outcomes['evolucao_caso'] == 'Óbito').sum()
        return round((deaths / len(known_outcomes)) * 100, 2) if len(known_outcomes) > 0 else 0.0

    def calculate_icu_rate(self) -> float:
        if self.df.empty: 
            return 0.0
        hospitalized = self.df[self.df['foi_internado'] == 'Sim']
        if hospitalized.empty: 
            return 0.0
        icu_cases = (hospitalized['internado_uti'] == 'Sim').sum()
        return round((icu_cases / len(hospitalized)) * 100, 2) if len(hospitalized) > 0 else 0.0

    def calculate_vaccination_rate(self) -> float:
        if self.df.empty: 
            return 0.0
        vaccinated = (self.df['vacinado_covid'] == 'Sim').sum()
        return round((vaccinated / len(self.df)) * 100, 2) if len(self.df) > 0 else 0.0

    def calculate_case_increase_rate(self) -> float:
        if self.df.empty or self.df['data_notificacao'].nunique() < 14: 
            return 0.0
        last_date = self.df['data_notificacao'].max()
        last_week_start = last_date - pd.Timedelta(days=6)
        prev_week_start = last_date - pd.Timedelta(days=13)
        prev_week_end = last_date - pd.Timedelta(days=7)
        last_week_cases = self.df[self.df['data_notificacao'] >= last_week_start].shape[0]
        prev_week_cases = self.df[(self.df['data_notificacao'] >= prev_week_start) & (self.df['data_notificacao'] <= prev_week_end)].shape[0]
        return round(((last_week_cases - prev_week_cases) / prev_week_cases) * 100, 2) if prev_week_cases > 0 else float('inf')

    def calculate_avg_notification_time(self) -> Optional[float]:
        if self.df.empty: 
            return None
        delta = (self.df['data_notificacao'] - self.df['data_primeiros_sintomas']).dt.days
        delta = delta[delta >= 0]
        return round(delta.mean(), 1) if not delta.isnull().all() else None

    def get_case_proportions(self) -> Dict[str, float]:
        if self.df.empty or 'classificacao_final' not in self.df.columns: 
            return {}
        proportions = self.df['classificacao_final'].value_counts(normalize=True) * 100
        return proportions.round(2).to_dict()

    def get_lethality_by_age_group(self) -> Dict[str, float]:
        if self.df.empty or 'idade_anos_corrigida' not in self.df.columns: 
            return {}
        age_bins = [0, 9, 19, 29, 39, 49, 59, 69, 79, 120]
        age_labels = ['0-9 anos', '10-19 anos', '20-29 anos', '30-39 anos', '40-49 anos', '50-59 anos', '60-69 anos', '70-79 anos', '80+ anos']
        df_lethality = self.df[self.df['evolucao_caso'].isin(['Cura', 'Óbito'])].copy()
        if df_lethality.empty: 
            return {}
        df_lethality['faixa_etaria'] = pd.cut(df_lethality['idade_anos_corrigida'], bins=age_bins, labels=age_labels, right=True)
        age_groups = df_lethality.groupby('faixa_etaria', observed=False)
        lethality = age_groups.apply(lambda x: (x['evolucao_caso'] == 'Óbito').sum() / len(x) * 100 if len(x) > 0 else 0)
        
        return lethality.round(2).to_dict()
    
    def calculate_flu_vaccination_rate(self) -> float:
        if self.df.empty or 'vacinado_gripe' not in self.df.columns: 
            return 0.0
        vaccinated = (self.df['vacinado_gripe'] == 'Sim').sum()
        total_cases = len(self.df)
        return round((vaccinated / total_cases) * 100, 2) if total_cases > 0 else 0.0

    def calculate_invasive_ventilation_rate(self) -> float:
        if self.df.empty: 
            return 0.0
        icu_patients = self.df[self.df['internado_uti'] == 'Sim']
        if icu_patients.empty: 
            return 0.0
        
        invasive_vent = (icu_patients['suporte_ventilatorio'] == 'Sim, invasivo').sum()
        total_icu = len(icu_patients)
        
        return round((invasive_vent / total_icu) * 100, 2) if total_icu > 0 else 0.0