from fpdf import FPDF
from datetime import datetime
import os

class PDFGeneratorTool:
    """
    Uma ferramenta para criar um relatório em PDF a partir do texto e dos gráficos gerados.
    """
    def create_report_pdf(self, report_text: str, plot_paths: dict, output_path: str) -> str:
        """
        Gera o relatório em PDF.
        """
        print(f"Ferramenta (PDF): Gerando PDF")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Relatório de Análise de Síndrome Respiratória Aguda Grave (SRAG)", 0, 1, "C")
        pdf.cell(0, 10, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 1, "C")
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, report_text.encode('latin-1', 'replace').decode('latin-1'))
        if plot_paths:
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Gráficos de Evolução", 0, 1, "L")
            pdf.ln(5)
            if "daily_cases_plot" in plot_paths:
                pdf.image(plot_paths["daily_cases_plot"], w=180)
                pdf.ln(5)  
            if "monthly_cases_plot" in plot_paths:
                pdf.image(plot_paths["monthly_cases_plot"], w=180)
        pdf.output(output_path)
        print(f"PDF salvo com sucesso em: {output_path}")
        return output_path