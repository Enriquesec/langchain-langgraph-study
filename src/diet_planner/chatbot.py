import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from .models import PlanComidas

load_dotenv()

# Prompt que guía el flujo conversacional por etapas
SYSTEM_PROMPT = """Eres NutriBot, un asistente nutricional amigable y profesional.
Tu objetivo es recopilar información para crear un plan de alimentación personalizado.

Sigue este flujo ESTRICTO, etapa por etapa:

ETAPA 1 - BIENVENIDA (solo en el primer mensaje):
  - Preséntate brevemente como NutriBot
  - Pregunta cuál es el objetivo dietético principal del usuario

ETAPA 2 - RECOPILACIÓN (una pregunta a la vez, en este orden):
  1. Preferencias alimentarias (vegetariano, vegano, omnívoro, etc.)
  2. Alergias o restricciones alimentarias (o si no tiene ninguna)
  3. Presupuesto semanal para comida (en USD)
  4. Tiempo disponible para cocinar por día (en minutos)
  5. Número de personas para las que cocinar

ETAPA 3 - CONFIRMACIÓN (cuando tengas toda la info):
  - Haz un resumen breve de lo recopilado
  - Pregunta si todo es correcto antes de generar el plan
  - Si el usuario confirma, di que procederás a crear su plan

REGLAS IMPORTANTES:
  - Haz UNA sola pregunta por turno
  - Sé conversacional y empático
  - Adapta el idioma del usuario
  - No generes el plan dentro de esta conversación; solo recopila info y confirma
"""


class DietChatbot:
    """
    Chatbot conversacional para planificación dietética.

    Flujo:
    1. start() → ETAPA 1: Presentación
    2. chat() × N → ETAPA 2: Recopilación de info
    3. chat() → ETAPA 3: Confirmación
    4. generate_plan() → Genera PlanComidas estructurado
    5. chat() → Maneja feedback e iteración
    """

    def __init__(self, api_key: str | None = None, temperature: float = 0.7):
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY no encontrada")

        # LLM conversacional
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=temperature,
        )

        # LLM con salida estructurada para generar el plan
        self.structured_llm = self.llm.with_structured_output(PlanComidas)

        # Historial de mensajes [(role, content), ...]
        self.history: list[tuple[str, str]] = []
        self.plan: PlanComidas | None = None

    # ─────────────────────────────────────────────────────────
    # Métodos públicos
    # ─────────────────────────────────────────────────────────

    def start(self) -> str:
        """Iniciar la conversación (ETAPA 1: Bienvenida)."""
        messages = self._build_messages(user_input="Hola, quiero planificar mi dieta")
        response = self.llm.invoke(messages)
        self.history.append(("human", "Hola, quiero planificar mi dieta"))
        self.history.append(("ai", response.content))
        return response.content

    def chat(self, user_input: str) -> str:
        """Enviar mensaje y obtener respuesta del chatbot."""
        self.history.append(("human", user_input))
        messages = self._build_messages()
        response = self.llm.invoke(messages)
        self.history.append(("ai", response.content))
        return response.content

    def generate_plan(self) -> PlanComidas:
        """
        Generar el plan de comidas estructurado basado en la conversación.
        Llama al LLM con structured_output → retorna PlanComidas validado.
        """
        conversation_text = self._conversation_as_text()

        plan_prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un nutricionista experto. Basándote en la siguiente conversación,
genera un plan de comidas personalizado para una semana completa (7 días).

Conversación con el usuario:
{conversacion}

Instrucciones:
- Crea desayuno, almuerzo y cena para cada uno de los 7 días
- Respeta estrictamente las restricciones/alergias mencionadas
- Ajusta las porciones al número de personas indicado
- El costo total debe aproximarse al presupuesto semanal dado
- Los tiempos de preparación deben ajustarse al tiempo disponible del usuario
- Los tips nutricionales deben ser específicos al objetivo indicado"""),
            ("human", "Genera el plan de comidas completo para la semana"),
        ])

        messages = plan_prompt.invoke({"conversacion": conversation_text})
        self.plan = self.structured_llm.invoke(messages)
        return self.plan

    def format_plan(self) -> str:
        """Formatear el plan de comidas como texto legible."""
        if not self.plan:
            return "No se ha generado un plan aún. Llama a generate_plan() primero."

        p = self.plan
        lines = [
            f"PLAN DE COMIDAS SEMANAL",
            f"{'=' * 60}",
            f"Objetivo: {p.objetivo}",
            f"Costo estimado: ${p.costo_total_estimado_usd:.2f} USD",
            "",
        ]

        for dia in p.semana:
            lines.append(f"{dia.dia.upper()}")
            lines.append("-" * 40)
            lines.append(f"  Desayuno: {dia.desayuno.nombre} ({dia.desayuno.tiempo_preparacion} min)")
            lines.append(f"  Almuerzo: {dia.almuerzo.nombre} ({dia.almuerzo.tiempo_preparacion} min)")
            lines.append(f"  Cena:     {dia.cena.nombre} ({dia.cena.tiempo_preparacion} min)")
            lines.append("")

        lines.append("TIPS NUTRICIONALES")
        lines.append("-" * 40)
        for tip in p.tips_nutricionales:
            lines.append(f"  • {tip}")

        if p.advertencias:
            lines.append("")
            lines.append("ADVERTENCIAS")
            lines.append("-" * 40)
            for adv in p.advertencias:
                lines.append(f"  ⚠ {adv}")

        return "\n".join(lines)

    def reset(self) -> None:
        """Reiniciar la conversación."""
        self.history = []
        self.plan = None

    # ─────────────────────────────────────────────────────────
    # Métodos privados
    # ─────────────────────────────────────────────────────────

    def _build_messages(self, user_input: str | None = None) -> list:
        """Construir lista de mensajes para el LLM incluyendo el historial."""
        messages: list = [SystemMessage(content=SYSTEM_PROMPT)]
        for role, content in self.history:
            if role == "human":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))
        if user_input:
            messages.append(HumanMessage(content=user_input))
        return messages

    def _conversation_as_text(self) -> str:
        """Convertir el historial a texto plano para el prompt de generación."""
        return "\n".join(
            f"{'Usuario' if role == 'human' else 'NutriBot'}: {content}"
            for role, content in self.history
        )
