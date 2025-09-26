
from src.agents.pdf_generator_agent.tools import PDFGeneratorTool
from src.metrics_calculator import MetricsCalculator
from src.tools.news_fetcher import news_search_tool
from src.plot_generator import PlotGenerator
from src.config import DATA_PROCESSING_CONFIG
from src.agents.clinical_protocols_agent.agent import clinical_protocol_agent

def generate_pdf_node(state: ReportState) -> Dict[str, str]:
    print("Nó (Orquestrador): Gerando Relatório em PDF")
    report_text = state.get("report_text")
    plot_paths = state.get("plot_image_paths")
    topic = state.get("topic", "relatorio").strip().replace(" ", "_")
    pdf_tool = PDFGeneratorTool()
    safe_topic_name = "".join(c for c in topic if c.isalnum() or c in ('_', '-')).rstrip()
    output_path = f"output/relatorio_srag_{safe_topic_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
    final_path = pdf_tool.create_report_pdf(report_text, plot_paths, output_path)
    return {"pdf_report_path": final_path}


workflow.add_node("generate_report", generate_report_node)
workflow.add_node("generate_pdf", generate_pdf_node)
workflow.add_edge("clinical_protocol_search", "generate_report")
workflow.add_edge("generate_report", "generate_pdf") 
workflow.add_edge("generate_pdf", END)              
