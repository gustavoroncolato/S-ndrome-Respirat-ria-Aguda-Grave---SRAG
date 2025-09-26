from typing import TypedDict, List, Dict, Any, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from pathlib import Path
import os
from datetime import datetime
from src.metrics_calculator import MetricsCalculator
from src.tools.news_fetcher import news_search_tool
from src.plot_generator import PlotGenerator
from src.config import DATA_PROCESSING_CONFIG
from src.agents.clinical_protocols_agent.agent import clinical_protocol_agent
from src.agents.pdf_generator_agent.tools import PDFGeneratorTool
from .prompts import final_report_prompt, disease_extraction_prompt
from src.llm_provider import invoke_llm_with_fallback

load_dotenv()

class ReportState(TypedDict):
    topic: str
    city: Optional[str]
    metrics: Dict[str, Any]
    plot_data: Dict[str, Any]
    news: List[Dict[str, Any]]
    clinical_protocols: Dict[str, str]
    plot_image_paths: Dict[str, str]
    report_text: str
    pdf_report_path: str

def calculate_metrics_node(state: ReportState) -> Dict[str, Any]:
    print("Nó (Orquestrador): Calcular Métricas")
    topic = state.get("topic", "Brasil")
    city = state.get("city")
    calculator = MetricsCalculator(
        cleaned_data_path=DATA_PROCESSING_CONFIG['output_file_path'],
        location=topic,
        city=city
    )
    metrics = {
        "taxa_mortalidade": calculator.calculate_mortality_rate(), "taxa_uti": calculator.calculate_icu_rate(),
        "taxa_vacinacao": calculator.calculate_vaccination_rate(), "taxa_aumento_casos": calculator.calculate_case_increase_rate(),
        "tempo_medio_notificacao": calculator.calculate_avg_notification_time(),
        "proporcao_casos": calculator.get_case_proportions(),
        "letalidade_por_idade": calculator.get_lethality_by_age_group(),
        "taxa_ventilacao_invasiva": calculator.calculate_invasive_ventilation_rate()
    }
    plot_data = { "casos_diarios": calculator.get_daily_cases(), "casos_mensais": calculator.get_monthly_cases() }
    print("Concluído.")
    return {"metrics": metrics, "plot_data": plot_data}

def generate_plots_node(state: ReportState) -> Dict[str, Any]:
    print("Nó (Orquestrador): Gerar Gráficos")
    topic = (state.get("topic") or "Brasil").strip().upper().replace(" ", "_")
    city = (state.get("city") or "").strip().upper().replace(" ", "_")
    plot_identifier = f"{topic}_{city}" if city else topic
    plot_data = state.get("plot_data", {})
    daily_data, monthly_data = plot_data.get("casos_diarios"), plot_data.get("casos_mensais")
    plotter = PlotGenerator()
    image_paths = {}
    output_dir = Path("output")
    os.makedirs(output_dir, exist_ok=True)
    if daily_data is not None and not daily_data.empty:
        safe_name = "".join(c for c in plot_identifier if c.isalnum() or c in ('_', '-')).rstrip()
        path = plotter.generate_daily_cases_plot(daily_data, output_dir / f"daily_cases_{safe_name}.png")
        image_paths["daily_cases_plot"] = str(path)
    if monthly_data is not None and not monthly_data.empty:
        safe_name = "".join(c for c in plot_identifier if c.isalnum() or c in ('_', '-')).rstrip()
        path = plotter.generate_monthly_cases_plot(monthly_data, output_dir / f"monthly_cases_{safe_name}.png")
        image_paths["monthly_cases_plot"] = str(path)
    print("   - Concluído.")
    return {"plot_image_paths": image_paths}

def fetch_news_node(state: ReportState) -> Dict[str, Any]:
    print("Nó (Orquestrador): Buscar Notícias")
    topic = state.get("topic", "Brasil")
    city = state.get("city")
    search_query = f"{city}, {topic}" if city and city.lower() != topic.lower() else topic
    search_results = news_search_tool.invoke({"location": search_query})
    print("Concluído.")
    return {"news": search_results}

def clinical_protocol_node(state: ReportState) -> Dict[str, str]:
    print("Nó (Orquestrador): Delegando para o Sub-Agente de Protocolos Clínicos")
    
    protocol_summaries = {}
    news_context = state.get("news", {}).get("results", [])
    if news_context:
        diseases_str = invoke_llm_with_fallback(
            prompt_template=disease_extraction_prompt,
            input_dict={"news": news_context}
        )
        diseases = [d.strip() for d in diseases_str.split(',') if d.strip()]
        print(f"Doenças identificadas nas notícias: {diseases}")
        if diseases:
            for disease in diseases:
                print(f"Invocando sub-agente para '{disease}'")
                summary_content = clinical_protocol_agent({"disease": disease})
                protocol_summaries[disease] = summary_content      
    return {"clinical_protocols": protocol_summaries}

def generate_report_node(state: ReportState) -> Dict[str, Any]:
    print("Nó (Orquestrador): Gerar Relatório Final")
    metrics, news, protocols = state.get("metrics", {}), state.get("news", {}).get("results", []), state.get("clinical_protocols", {})
    topic, city = state.get("topic"), state.get("city")
    full_topic = f"{city}, {topic}" if city and city.lower() != topic.lower() else topic

    news_context = "\n".join([f"- Título: {item['title']}\n  Resumo: {item['content']}" for item in news])
    protocols_context = "\n".join([f"**{disease.upper()}**\n{summary}" for disease, summary in protocols.items()]) if protocols else "Nenhum protocolo clínico específico foi pesquisado."
    
    prompt_input = {
        "topic": full_topic, "metrics_mortality": metrics.get("taxa_mortalidade"),
        "metrics_uti": metrics.get("taxa_uti"), "metrics_vacinacao": metrics.get("taxa_vacinacao"),
        "metrics_aumento_casos": metrics.get("taxa_aumento_casos"),
        "metrics_notification_time": metrics.get("tempo_medio_notificacao"),
        "metrics_proportions": str(metrics.get("proporcao_casos", {})),
        "metrics_lethality_by_age": str(metrics.get("letalidade_por_idade", {})),
        "metrics_invasive_ventilation": metrics.get("taxa_ventilacao_invasiva"),
        "news_context": news_context, "protocols_context": protocols_context
    }
    
    response_content = invoke_llm_with_fallback(
        prompt_template=final_report_prompt,
        input_dict=prompt_input
    )
    print("Relatório final gerado.")
    return {"report_text": response_content}

def generate_pdf_node(state: ReportState) -> Dict[str, str]:
    print("Nó (Orquestrador): Gerando Relatório em PDF")
    report_text, plot_paths, topic = state.get("report_text"), state.get("plot_image_paths"), state.get("topic", "relatorio").strip()
    city = (state.get("city") or "").strip()
    full_topic = f"{city}_{topic}" if city else topic
    pdf_tool = PDFGeneratorTool()
    safe_topic_name = "".join(c for c in full_topic if c.isalnum() or c in ('_', '-')).rstrip()
    output_path = f"output/relatorio_srag_{safe_topic_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    final_path = pdf_tool.create_report_pdf(report_text, plot_paths, output_path)
    return {"pdf_report_path": final_path}


print("Montando o Agente Orquestrador com LangGraph")
workflow = StateGraph(ReportState)
workflow.add_node("calculate_metrics", calculate_metrics_node)
workflow.add_node("generate_plots", generate_plots_node)
workflow.add_node("fetch_news", fetch_news_node)
workflow.add_node("clinical_protocol_search", clinical_protocol_node)
workflow.add_node("generate_report", generate_report_node)
workflow.add_node("generate_pdf", generate_pdf_node)
workflow.set_entry_point("calculate_metrics")
workflow.add_edge("calculate_metrics", "generate_plots")
workflow.add_edge("generate_plots", "fetch_news")
workflow.add_edge("fetch_news", "clinical_protocol_search")
workflow.add_edge("clinical_protocol_search", "generate_report")
workflow.add_edge("generate_report", "generate_pdf")
workflow.add_edge("generate_pdf", END)
app = workflow.compile()
print("Agente Orquestrador compilado com sucesso.")