import os
from dotenv import load_dotenv

# Importar LangChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Importar modelos locales (definidos con Pydantic en models.py)
from .models import TransferenceInput, TransferenceAnalysis

load_dotenv()


class TransferenceAnalyzer:
    """
    Analizador de transferencias usando LangChain y Gemini con salida estructurada.

    Flujo:
    1. Recibe TransferenceInput (entrada validada por Pydantic)
    2. Crea un LLM estructurado con with_structured_output(TransferenceAnalysis)
    3. Construye un prompt descriptor de la tarea
    4. Invoca el modelo y valida la salida
    5. Retorna TransferenceAnalysis (salida validada)
    """

    def __init__(self, api_key: str | None = None, temperature: float = 0.3):
        """
        Inicializar el analizador.

        Args:
            api_key: API key de Google Gemini (o desde GOOGLE_API_KEY env var)
            temperature: Temperatura del modelo (0.3 por defecto para respuestas consistentes)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY no encontrada en variables de entorno")

        # 1. Crear LLM (instancia del modelo)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=temperature,
        )

        # 2. Crear LLM estructurado con with_structured_output
        # Esto obliga al modelo a retornar salida validada contra TransferenceAnalysis
        self.structured_llm = self.llm.with_structured_output(TransferenceAnalysis)

        # 3. Definir el prompt descriptor de la tarea usando PromptTemplate
        self.prompt_template = PromptTemplate.from_template(
            """Eres un experto en detección de fraude financiero. Analiza transacciones de transferencia para determinar si son 'Usual' o 'Inusual' basándose en el concepto/descripción.

Reglas de clasificación:
- 'Usual': Operaciones comerciales estándar, transferencias personales, pagos, alquiler, servicios, etc.
- 'Inusual': Banderas rojas como terminología inusual, patrones sospechosos, indicadores de lavado de dinero, palabras clave de alto riesgo.

Analiza esta transferencia:
- ID Movimiento: {id_movimiento}
- Monto: ${monto:,.2f} USD
- Concepto: "{concepto}"

Proporciona tu análisis estructurado. Clasificación clara (Usual o Inusual) y si es inusual, explica las banderas rojas específicas detectadas."""
        )

    def analyze(self, transference: TransferenceInput) -> TransferenceAnalysis:
        """
        Analizar una transferencia individual.

        Args:
            transference: TransferenceInput validado por Pydantic

        Returns:
            TransferenceAnalysis con resultado e información

        Raises:
            ValueError: Si el análisis falla o retorna datos inválidos
        """
        try:
            # Validación de entrada (Pydantic ya valida en TransferenceInput)
            if not isinstance(transference, TransferenceInput):
                raise TypeError("El argumento debe ser una instancia de TransferenceInput")

            # Construir prompt usando PromptTemplate
            prompt_text = self.prompt_template.format(
                id_movimiento=transference.id_movimiento,
                monto=transference.monto,
                concepto=transference.concepto
            )

            # Invocar modelo estructurado (retorna TransferenceAnalysis validado)
            analysis = self.structured_llm.invoke(prompt_text)

            # Validación de salida
            if not isinstance(analysis, TransferenceAnalysis):
                raise ValueError("La salida del modelo no es una TransferenceAnalysis válida")

            return analysis

        except ValueError as e:
            raise ValueError(f"Error de validación en análisis: {str(e)}")
        except Exception as e:
            raise Exception(f"Error al analizar transferencia {transference.id_movimiento}: {str(e)}")

    def analyze_batch(self, transferences: list[TransferenceInput]) -> list[TransferenceAnalysis]:
        """
        Analizar múltiples transferencias.

        Args:
            transferences: Lista de TransferenceInput

        Returns:
            Lista de TransferenceAnalysis
        """
        results = []
        for transfer in transferences:
            try:
                result = self.analyze(transfer)
                results.append(result)
            except Exception as e:
                print(f"Error analizando {transfer.id_movimiento}: {str(e)}")
                continue
        return results
