from .prompts import clinical_agent_prompt
from .tools import clinical_protocol_search_tool
from src.llm_provider import invoke_llm_with_fallback

def create_clinical_protocol_agent():
    """
    Cria a cadeia que define o comportamento do sub-agente de protocolos clínicos.
    """
    def agent_logic(input_dict):
        tool_result = clinical_protocol_search_tool.invoke(input_dict["disease"])
        return invoke_llm_with_fallback(
            prompt_template=clinical_agent_prompt,
            input_dict={"context": tool_result, "disease": input_dict["disease"]}
        )
    return agent_logic

clinical_protocol_agent = create_clinical_protocol_agent()