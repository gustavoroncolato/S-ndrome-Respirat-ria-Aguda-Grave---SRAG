import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain.tools import tool

load_dotenv()

if not os.getenv("TAVILY_API_KEY"):
    raise ValueError("A chave de API da Tavily não foi encontrada. Verifique seu arquivo .env")

@tool
def news_search_tool(location: str = "São Paulo") -> str:
    """
    Busca notícias recentes sobre Síndrome Respiratória Aguda Grave (SRAG) para uma localidade específica.
    A entrada deve ser uma string com o nome de um estado do Brasil ou a sigla 'BR' para uma busca nacional.
    Se nenhuma localidade for fornecida, a busca padrão será para 'São Paulo'.
    """
    
    search_location = ""
    if not location or not location.strip():
        search_location = "São Paulo"  
    elif location.strip().upper() == "BR":
        search_location = "Brasil"
    else:
        search_location = location.strip()
        
    print(f"\nExecutando busca de notícias de SRAG para a localidade: '{search_location}'...")
    
    query = f"notícias recentes sobre Síndrome Respiratória Aguda Grave (SRAG) em {search_location}"
    
    tavily_search = TavilySearch(max_results=3)
    results = tavily_search.invoke(query)
    
    return results

if __name__ == '__main__':
    print("Testando a ferramenta de busca de notícias parametrizada")
    
    print("\n[TESTE BUSCA PADRÃO (SÃO PAULO)]")
    default_results = news_search_tool.invoke({})
    print(default_results)

    print("\n[TESTE BUSCA NACIONAL ('BR')]")
    brasil_results = news_search_tool.invoke({"location": "BR"})
    print(brasil_results)

    print("\n[TESTE BUSCA POR ESTADO ('Minas Gerais')]")
    minas_results = news_search_tool.invoke({"location": "Minas Gerais"})
    print(minas_results)

    print("\n[TESTE BUSCA CONTINENTAL ('América do Sul')]")
    sul_america_results = news_search_tool.invoke({"location": "América do Sul"})
    print(sul_america_results)