# Guía de Uso de API Gemini - RPD Limits

## Límites Actuales

- **Gemini 2.5 Flash (Free tier)**: 20 RPD (Requests Per Day)
- **Cada llamada a `analyzer.analyze()`**: 1 RPD

## Problema Identificado

El código contiene múltiples scripts y notebooks que hacen llamadas a Gemini:

| Script | Llamadas |
|--------|----------|
| `test_anomalies.py` | 2 |
| `example_step_by_step.py` | 2 |
| `notebook 03` (completo) | 7 |
| `notebook 04` (completo) | 2 |
| **TOTAL si ejecutas todo una vez** | **13** |
| **TOTAL si ejecutas todo dos veces** | **26** (EXCEDE LÍMITE) |

## Soluciones Implementadas

### 1. Sistema de Caché Automático

El `analyzer.py` ahora incluye caché automático:

```python
from anomalies_transfer import TransferenceAnalyzer, TransferenceInput

analyzer = TransferenceAnalyzer()

transfer = TransferenceInput(
    id_movimiento="12345601",
    monto=1500.00,
    concepto="Pago de servicios"
)

# Primera llamada: usa API (1 RPD)
result1 = analyzer.analyze(transfer)

# Segunda llamada: usa caché (0 RPD)
result2 = analyzer.analyze(transfer)
```

### 2. Control Manual del Caché

```python
# Desabilitar caché si necesitas respuesta fresca
result = analyzer.analyze(transfer, use_cache=False)

# Estadísticas de caché
from anomalies_transfer.cache import cache_stats
stats = cache_stats()
print(f"Items en caché: {stats['cached_items']}")
```

### 3. Borrar Caché

```python
from anomalies_transfer.cache import clear_cache
clear_cache()  # Borra .cache.json
```

## Recomendaciones

### ✓ Buenas Prácticas

1. **Usa caché por defecto** (está habilitado automáticamente)
2. **Ejecuta los notebooks una sola vez** al día
3. **Reutiliza scripts existentes** en lugar de crear nuevos
4. **Agrupa análisis** en scripts, no en notebooks separados

### ✗ Evitar

1. No ejecutes notebooks múltiples veces innecesariamente
2. No crees nuevos scripts de prueba con análisis
3. No desabilites caché sin razón
4. No ejecutes `example_step_by_step.py` en cada sesión de desarrollo

## Uso Óptimo

```python
from anomalies_transfer import TransferenceAnalyzer, TransferenceInput
from anomalies_transfer.cache import cache_stats

analyzer = TransferenceAnalyzer()

transfers = [
    TransferenceInput(id_movimiento="12345601", monto=1500, concepto="Pago normal"),
    TransferenceInput(id_movimiento="12345602", monto=50000, concepto="Transferencia offshore"),
]

# Batch analysis con caché automático
results = analyzer.analyze_batch(transfers)

# Ver uso de caché
stats = cache_stats()
print(f"Caché: {stats['cached_items']} items, {stats['file_size_kb']} KB")
```

## Archivo de Caché

- **Ubicación**: `src/anomalies_transfer/.cache.json`
- **Formato**: JSON con análisis guardados
- **Auto-generado**: Se crea en la primera ejecución
- **Seguro**: Puedes commitear a Git (datos de prueba)

## Próximos Pasos

Si necesitas más llamadas:
1. Upgrade a **Gemini Pro** (pricing)
2. Implementar rate limiting
3. Usar modelo más barato (Gemini Nano)
