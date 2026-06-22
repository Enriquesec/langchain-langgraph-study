#!/usr/bin/env python3
"""
Transfer Anomaly Detection Chatbot

Analyzes financial transfers to detect unusual patterns.
Usage:
    python -m src.anomalies_transfer.main
"""

from analyzer import TransferenceAnalyzer
from models import TransferenceInput


def main():
    analyzer = TransferenceAnalyzer()

    test_cases = [
        TransferenceInput(
            id_movimiento="TRX001",
            monto=1500.00,
            concepto="Pago de servicios mensuales"
        ),
        TransferenceInput(
            id_movimiento="TRX002",
            monto=50000.00,
            concepto="Transferencia a cuenta offshore sin documentación"
        ),
        TransferenceInput(
            id_movimiento="TRX003",
            monto=250.50,
            concepto="Compra de artículos de oficina"
        ),
        TransferenceInput(
            id_movimiento="TRX004",
            monto=100000.00,
            concepto="Lavado de dinero operativo"
        ),
        TransferenceInput(
            id_movimiento="TRX005",
            monto=3200.00,
            concepto="Alquiler mensual del departamento"
        ),
    ]

    print("=" * 70)
    print("TRANSFER ANOMALY DETECTION")
    print("=" * 70)

    for transference in test_cases:
        print(f"\n📋 Analyzing: {transference.id_movimiento}")
        print(f"   Amount: ${transference.monto:,.2f}")
        print(f"   Concept: {transference.concepto}")
        print("-" * 70)

        result = analyzer.analyze(transference)

        print(f"✓ Result: {result.resultado}")
        print(f"  Confidence: {result.confianza:.1%}")

        if result.razon_si_inusual:
            print(f"  ⚠️  Reason: {result.razon_si_inusual}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
