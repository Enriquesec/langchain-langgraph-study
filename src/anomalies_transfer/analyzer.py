import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from .models import TransferenceInput, TransferenceAnalysis

load_dotenv()


class TransferenceAnalyzer:
    def __init__(self, api_key: str | None = None, temperature: float = 0.3):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=temperature,
        )
        self.structured_llm = self.llm.with_structured_output(TransferenceAnalysis)

    def analyze(self, transference: TransferenceInput) -> TransferenceAnalysis:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a financial fraud detection expert. Analyze transfer transactions to determine if they are 'Usual' or 'Inusual' based on the concept/description.

Rules for classification:
- 'Usual': Standard business operations, personal transfers, payments, rent, utilities, etc.
- 'Inusual': Red flags like unusual terminology, suspicious patterns, potential money laundering indicators, or high-risk keywords.

Always provide:
1. A clear classification (Usual or Inusual)
2. If Inusual: explain the specific red flags detected
3. A confidence score (0-1) for your assessment

Be concise and precise in your analysis."""),
            ("human", """Analyze this transfer:
- Movement ID: {id_movimiento}
- Amount: ${monto:,.2f} USD
- Concept: "{concepto}"

Provide your structured analysis.""")
        ])

        messages = prompt_template.invoke({
            "id_movimiento": transference.id_movimiento,
            "monto": transference.monto,
            "concepto": transference.concepto
        })

        analysis = self.structured_llm.invoke(messages)
        return analysis

    def analyze_batch(self, transferences: list[TransferenceInput]) -> list[TransferenceAnalysis]:
        return [self.analyze(t) for t in transferences]
