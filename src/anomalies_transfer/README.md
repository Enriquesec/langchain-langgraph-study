# Transfer Anomaly Detection

Chatbot para detectar transferencias financieras inusuales usando LangChain y Gemini 2.5 Flash.

## Overview

Analiza el concepto/descripción de una transferencia financiera y clasifica si es **Usual** o **Inusual** basándose en patrones sospechosos y red flags de lavado de dinero.

## Inputs

| Campo | Tipo | Restricciones |
|-------|------|--------------|
| `id_movimiento` | str | 8 dígitos numéricos |
| `monto` | float | > 0 (USD) |
| `concepto` | str | 1-125 caracteres |

## Outputs

```python
{
    "id_movimiento": "12345601",
    "resultado": "Usual" | "Inusual",
    "razon_si_inusual": "Optional description of red flags"
}
```

## Usage

### Python Script

```python
from anomalies_transfer import TransferenceAnalyzer, TransferenceInput

analyzer = TransferenceAnalyzer()

transfer = TransferenceInput(
    id_movimiento="12345601",
    monto=1500.00,
    concepto="Pago de servicios mensuales"
)

result = analyzer.analyze(transfer)
print(f"Resultado: {result.resultado}")
if result.razon_si_inusual:
    print(f"Razon: {result.razon_si_inusual}")
```

### Batch Analysis

```python
transfers = [
    TransferenceInput(...),
    TransferenceInput(...),
]

results = analyzer.analyze_batch(transfers)
```

### Jupyter Notebook

Ver `notebooks/03_anomalias_transferencias.ipynb` para ejemplos interactivos.

## Anomaly Detection Logic

El sistema detecta patrones inusuales como:
- Transferencias a paraísos fiscales sin documentación
- Mención explícita de "lavado de dinero"
- Beneficiarios desconocidos en jurisdicciones de alto riesgo
- Falta de descripción clara del propósito
- Terminología sospechosa

## Configuration

El analizador requiere la variable de entorno `GOOGLE_API_KEY`:

```bash
export GOOGLE_API_KEY=your_api_key_here
```

O crear un archivo `.env` en la raíz del proyecto:

```
GOOGLE_API_KEY=your_api_key_here
```

## Temperature & Model

- **Modelo**: `gemini-2.5-flash`
- **Temperature**: 0.3 (bajo, para respuestas consistentes)
- **Configuración**: Personalizable en `TransferenceAnalyzer.__init__()`

## Testing

```bash
# Ejecutar análisis de ejemplo
python -m src.anomalies_transfer.main

# O desde Jupyter
jupyter notebook notebooks/03_anomalias_transferencias.ipynb
```

## Architecture

```
src/anomalies_transfer/
├── __init__.py          # Exports públicas
├── models.py            # Pydantic models (TransferenceInput, TransferenceAnalysis)
├── analyzer.py          # Lógica principal (TransferenceAnalyzer)
├── main.py              # Script de prueba
└── README.md            # Este archivo
```

## Learning Resources

- [LangChain Structured Output](https://python.langchain.com/docs/guides/structured_output)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Pydantic Validation](https://docs.pydantic.dev/)
