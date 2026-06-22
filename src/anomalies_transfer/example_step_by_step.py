#!/usr/bin/env python3
"""
Ejemplo paso a paso de cómo funciona el analizador de transferencias.
Demuestra cada componente de LangChain y Pydantic.
"""

import os
from dotenv import load_dotenv

# ============================================================================
# PASO 1: IMPORTAR PYDANTIC Y LANGCHAIN
# ============================================================================
print("=" * 70)
print("PASO 1: Importar Pydantic y LangChain")
print("=" * 70)

from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

print("✓ Importaciones completadas")
print("  - Pydantic: para validar entrada/salida")
print("  - LangChain: para orquestación con LLM")
print()

# ============================================================================
# PASO 2: DEFINIR MODELOS PYDANTIC
# ============================================================================
print("=" * 70)
print("PASO 2: Definir modelos Pydantic")
print("=" * 70)

class TransferenceInput(BaseModel):
    """Modelo de ENTRADA: valida datos antes de enviar al LLM"""
    id_movimiento: str = Field(
        description="Identificador numérico de 8 dígitos",
        pattern="^\\d{8}$"
    )
    monto: float = Field(
        description="Monto en USD (debe ser positivo)",
        gt=0
    )
    concepto: str = Field(
        description="Descripción de la transferencia (1-125 caracteres)",
        min_length=1,
        max_length=125
    )

class TransferenceAnalysis(BaseModel):
    """Modelo de SALIDA: valida datos retornados por el LLM"""
    id_movimiento: str = Field(
        description="ID de la transferencia"
    )
    resultado: str = Field(
        description="Clasificación: 'Usual' o 'Inusual'",
        pattern="^(Usual|Inusual)$"
    )
    razon_si_inusual: str | None = Field(
        description="Explicación si es inusual",
        default=None
    )

print("✓ Modelos definidos:")
print("  - TransferenceInput: valida entrada (id, monto, concepto)")
print("  - TransferenceAnalysis: valida salida (id, resultado, razón)")
print()

# ============================================================================
# PASO 3: CARGAR API KEY Y CREAR LLM
# ============================================================================
print("=" * 70)
print("PASO 3: Crear LLM estructurado")
print("=" * 70)

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY no encontrada en .env")

# Crear instancia del LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0.3,  # Baja temperatura = respuestas más determinísticas
)

print(f"✓ LLM creado: {llm.model}")

# Crear LLM estructurado que OBLIGA retornar TransferenceAnalysis
structured_llm = llm.with_structured_output(TransferenceAnalysis)

print("✓ LLM estructurado: with_structured_output(TransferenceAnalysis)")
print("  El modelo DEBE retornar datos que validen contra TransferenceAnalysis")
print()

# ============================================================================
# PASO 4: CREAR PROMPT DESCRIPTOR
# ============================================================================
print("=" * 70)
print("PASO 4: Crear prompt descriptor de la tarea")
print("=" * 70)

prompt = PromptTemplate.from_template("""Eres un experto en detección de fraude financiero.
Analiza transferencias y clasifica como 'Usual' o 'Inusual'.

Banderas rojas: offshore, anónimo, lavado de dinero, paraíso fiscal.
Normales: alquiler, servicios, compras, pagos regulares.

Analiza:
- ID: {id_movimiento}
- Monto: ${monto:,.2f} USD
- Concepto: "{concepto}"

Retorna análisis estructurado. Sé conciso y preciso.""")

print("✓ Prompt template creado con PromptTemplate:")
print("  - Variables: {id_movimiento}, {monto}, {concepto}")
print()

# ============================================================================
# PASO 5: CREAR EJEMPLOS DE ENTRADA
# ============================================================================
print("=" * 70)
print("PASO 5: Crear ejemplos de entrada")
print("=" * 70)

# Ejemplo 1: Transferencia USUAL
transfer_usual = TransferenceInput(
    id_movimiento="12345601",
    monto=1500.00,
    concepto="Pago de servicios mensuales a proveedor"
)

print("Ejemplo 1 (USUAL):")
print(f"  - ID: {transfer_usual.id_movimiento}")
print(f"  - Monto: ${transfer_usual.monto:,.2f}")
print(f"  - Concepto: {transfer_usual.concepto}")
print()

# Ejemplo 2: Transferencia INUSUAL
transfer_inusual = TransferenceInput(
    id_movimiento="12345602",
    monto=50000.00,
    concepto="Transferencia anónima a cuenta offshore sin documentación"
)

print("Ejemplo 2 (INUSUAL):")
print(f"  - ID: {transfer_inusual.id_movimiento}")
print(f"  - Monto: ${transfer_inusual.monto:,.2f}")
print(f"  - Concepto: {transfer_inusual.concepto}")
print()

# ============================================================================
# PASO 6: INVOCAR MODELO CON MANEJO DE ERRORES
# ============================================================================
print("=" * 70)
print("PASO 6: Invocar modelo (try/except)")
print("=" * 70)

def analyze_transfer(transfer: TransferenceInput) -> TransferenceAnalysis:
    """Analizar una transferencia con manejo de errores."""
    try:
        # Construir prompt reemplazando variables con PromptTemplate.format()
        prompt_text = prompt.format(
            id_movimiento=transfer.id_movimiento,
            monto=transfer.monto,
            concepto=transfer.concepto
        )

        # Invocar structured_llm (retorna TransferenceAnalysis validado)
        analysis = structured_llm.invoke(prompt_text)

        # El modelo valida automáticamente contra TransferenceAnalysis
        # Si retorna datos inválidos, Pydantic lanza ValidationError
        return analysis

    except ValueError as e:
        print(f"✗ Error de validación: {e}")
        raise

    except Exception as e:
        print(f"✗ Error inesperado: {e}")
        raise

# ============================================================================
# PASO 7: PROBAR CON AMBOS EJEMPLOS
# ============================================================================
print("=" * 70)
print("PASO 7: Probar con ambos ejemplos")
print("=" * 70)

print("\n[ANÁLISIS 1] Transferencia USUAL")
print("-" * 70)
try:
    result1 = analyze_transfer(transfer_usual)
    print(f"✓ ID: {result1.id_movimiento}")
    print(f"✓ Resultado: {result1.resultado}")
    if result1.razon_si_inusual:
        print(f"  Razón: {result1.razon_si_inusual}")
except Exception as e:
    print(f"✗ Análisis falló: {e}")

print("\n[ANÁLISIS 2] Transferencia INUSUAL")
print("-" * 70)
try:
    result2 = analyze_transfer(transfer_inusual)
    print(f"✓ ID: {result2.id_movimiento}")
    print(f"✓ Resultado: {result2.resultado}")
    if result2.razon_si_inusual:
        print(f"  Razón: {result2.razon_si_inusual}")
except Exception as e:
    print(f"✗ Análisis falló: {e}")

print("\n" + "=" * 70)
print("✓ DEMOSTRACIÓN COMPLETADA")
print("=" * 70)
