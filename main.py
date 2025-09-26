
# from src.agents.orchestrator.agent import app

# def main():
#     """
#     Função principal que orquestra a execução do agente.
#     """
#     print("INICIANDO AGENTE DE ANÁLISE DE DADOS DE SRAG")
    
#     try:
#         initial_input = {"topic": "Brasil"}

#         final_state = app.invoke(initial_input)
        
#         print("\n\n\nRELATÓRIO FINAL GERADO")
#         print("="*30)
#         print(final_state["report_text"])
#         print("="*30)
        
#         print("\n PROCESSO CONCLUÍDO COM SUCESSO!")
        
#     except Exception as e:
#         print(f"\nOCORREU UM ERRO DURANTE A EXECUÇÃO: {e}")


# if __name__ == "__main__":
#     main()

from src.data_processor import SragDataProcessor
from src.config import DATA_PROCESSING_CONFIG

if __name__ == "__main__":
    processor = SragDataProcessor(config=DATA_PROCESSING_CONFIG)
    processor.run_pipeline()
    processor.save_processed_data()
    print("\nArquivo 'OpenSUS_limpo.csv' foi atualizado com sucesso com as novas colunas!")