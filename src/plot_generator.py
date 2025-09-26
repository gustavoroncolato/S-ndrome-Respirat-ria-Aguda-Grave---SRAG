import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
import os

class PlotGenerator:
    """
    classe para gerar e salvar gráficos a partir de dados SRAG
    """
    def generate_daily_cases_plot(self, data: pd.Series, output_path: str) -> str:
        """
        Gráfico de barras com os casos diários e o salva como uma imagem..
        """
        print(f"Gerando gráfico de casos diários")
        plt.style.use('ggplot') 
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(data.index, data.values, color='skyblue', label='Nº de Casos Diários')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        plt.xticks(rotation=45, ha='right')
        ax.set_title('Número Diário de Casos de SRAG (Últimos 30 Dias)', fontsize=16)
        ax.set_xlabel('Data da Notificação', fontsize=12)
        ax.set_ylabel('Número de Casos', fontsize=12)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend()
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close(fig)
        print(f" # Gráfico salvo em: {output_path}")
        return output_path

    def generate_monthly_cases_plot(self, data: pd.Series, output_path: str) -> str:
        """
        Gráfico de linhas dos casos mensais e o salva como uma imagem.       
        """
        print(f"Gerando gráfico de casos mensais ")
        plt.style.use('ggplot')  
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(data.index, data.values, marker='o', linestyle='-', color='royalblue', label='Nº de Casos Mensais')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b/%Y'))
        plt.xticks(rotation=45, ha='right')

        ax.set_title('Número Mensal de Casos de SRAG (Últimos 12 Meses)', fontsize=16)
        ax.set_xlabel('Mês da Notificação', fontsize=12)
        ax.set_ylabel('Número de Casos', fontsize=12)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend()
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close(fig)
        print(f" # Gráfico salvo em: {output_path}")
        return output_path
#teste
if __name__ == '__main__':
    from src.metrics_calculator import MetricsCalculator
    from src.config import DATA_PROCESSING_CONFIG
    print("Testando o PlotGenerator de forma")
    output_dir = Path("output")
    os.makedirs(output_dir, exist_ok=True)
    cleaned_file_path = DATA_PROCESSING_CONFIG['output_file_path']
    if not Path(cleaned_file_path).exists():
        print("ARQUIVO DE DADOS LIMPO NÃO ENCONTRADO! Execute 'main.py' primeiro.")
    else:
        calculator = MetricsCalculator(cleaned_data_path=cleaned_file_path)
        daily_data = calculator.get_daily_cases()
        monthly_data = calculator.get_monthly_cases()
        plotter = PlotGenerator()
        plotter.generate_daily_cases_plot(daily_data, output_dir / "daily_cases_srag.png")
        plotter.generate_monthly_cases_plot(monthly_data, output_dir / "monthly_cases_srag.png")

