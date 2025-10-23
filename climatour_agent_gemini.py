# -*- coding: utf-8 -*-
import os
import sys
from dotenv import load_dotenv

from langchain.tools import Tool
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI

from climatour.state_capitals import STATE_CAPITALS
from tools.weather_tool import get_weather_by_city

load_dotenv()

def build_weather_tool():
    def _tool(uf: str) -> str:
        uf_norm = uf.strip().upper()
        if uf_norm not in STATE_CAPITALS:
            return ("UF inválida. Use siglas como SP, RJ, BA, etc. "
                    "Ex.: 'SP' para São Paulo.")
        city, state_name = STATE_CAPITALS[uf_norm]
        data = get_weather_by_city(city, "BR")
        summary = (
            f"Clima em {city} ({state_name}): "
            f"{data.get('condition')}, "
            f"{data.get('temp_c')}°C (sensação {data.get('feels_like_c')}°C), "
            f"umidade {data.get('humidity')}%, vento {data.get('wind_kph')} km/h. "
            f"provider={data.get('provider')}"
        )
        return summary
    return Tool(
        name="get_weather_by_uf",
        description=(
            "Busca o clima atual da capital de um estado brasileiro. "
            "Entrada: UF (ex.: 'SP', 'RJ', 'BA'). "
            "Retorna um resumo com condição, temperatura, umidade e vento."
        ),
        func=_tool,
    )

def build_agent(model_name: str | None = None) -> AgentExecutor:
    # Permite configurar o modelo pelo .env (exemplo: GEMINI_MODEL=models/gemini-2.0-flash)
    model_name = model_name or os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash")

    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.7)

    tools = [build_weather_tool()]
    prompt = hub.pull("hwchase17/react")

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    agent_exec = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_exec

def main():
    print("=== ClimaTour — (Gemini) Assistente de Viagem Inteligente ===")
    print("Dica: digite a UF do seu estado (ex.: SP, RJ, BA).")
    uf = input("Informe sua UF: ").strip().upper()
    if not uf:
        print("UF não informada. Encerrando.")
        sys.exit(1)

    user_question = (
        "Você é um agente de turismo no Brasil. "
        "Use a ferramenta de clima para consultar a capital do estado do usuário "
        "e, com base nisso, recomende **apenas 1** passeio dentro daquele estado. "
        "Explique o porquê em 2 frases no máximo. "
        f"A UF do usuário é: {uf}."
    )

    try:
        agent = build_agent()
        result = agent.invoke({"input": user_question})
        print("\n--- Recomendações do ClimaTour ---")
        print(result["output"])
    except Exception as e:
        print(f"\nFalha ao executar o agente: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("ATENÇÃO: Defina a variável GOOGLE_API_KEY no .env ou no ambiente.")
    main()
