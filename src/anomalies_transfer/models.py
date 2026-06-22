from pydantic import BaseModel, Field
from typing import Optional


class TransferenceInput(BaseModel):
    id_movimiento: str = Field(
        description="Numeric identifier for the transfer movement (8 digits)",
        pattern="^\\d{8}$"
    )
    monto: float = Field(
        description="Transfer amount in USD (must be positive)",
        gt=0
    )
    concepto: str = Field(
        description="Concept or description of the transfer (1-125 characters)",
        min_length=1,
        max_length=125
    )


class TransferenceAnalysis(BaseModel):
    id_movimiento: str = Field(
        description="The transfer movement ID (8 digits)"
    )
    resultado: str = Field(
        description="Classification: 'Usual' or 'Inusual'",
        pattern="^(Usual|Inusual)$"
    )
    razon_si_inusual: Optional[str] = Field(
        description="Explanation if the transfer is marked as 'Inusual', None if 'Usual'",
        default=None,
        max_length=500
    )
