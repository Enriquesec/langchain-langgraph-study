#!/usr/bin/env python3
"""Quick test for transfer anomaly analyzer"""

import sys
sys.path.insert(0, 'src')

from anomalies_transfer import TransferenceAnalyzer, TransferenceInput

print("🧪 Testing Transfer Anomaly Detector\n")
print("=" * 70)

analyzer = TransferenceAnalyzer()

test_transfers = [
    TransferenceInput(
        id_movimiento="12345601",
        monto=1500.50,
        concepto="Pago de servicios mensuales a proveedor"
    ),
    TransferenceInput(
        id_movimiento="12345602",
        monto=25000.00,
        concepto="Transferencia anónima a cuenta offshore"
    ),
]

for transfer in test_transfers:
    print(f"\n📋 Analyzing: {transfer.id_movimiento}")
    print(f"   Concept: {transfer.concepto}")
    print(f"   Amount: ${transfer.monto:,.2f}")
    print("-" * 70)

    result = analyzer.analyze(transfer)

    print(f"✓ Resultado: {result.resultado}")

    if result.razon_si_inusual:
        print(f"  ⚠️  Razón: {result.razon_si_inusual}")

print("\n" + "=" * 70)
print("✓ Test completed successfully!")
