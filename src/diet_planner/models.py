from pydantic import BaseModel, Field
from typing import Optional


class Comida(BaseModel):
    nombre: str = Field(description="Nombre del plato")
    ingredientes: list[str] = Field(description="Lista de ingredientes principales")
    tiempo_preparacion: int = Field(description="Tiempo de preparación en minutos")


class DiaMeal(BaseModel):
    dia: str = Field(description="Día de la semana en español")
    desayuno: Comida
    almuerzo: Comida
    cena: Comida


class PlanComidas(BaseModel):
    objetivo: str = Field(description="Objetivo dietético del usuario")
    semana: list[DiaMeal] = Field(description="Lista de 7 días con sus comidas")
    costo_total_estimado_usd: float = Field(description="Costo total estimado de la semana en USD")
    tips_nutricionales: list[str] = Field(description="3 a 5 consejos nutricionales personalizados")
    advertencias: Optional[list[str]] = Field(
        description="Advertencias relevantes según restricciones del usuario",
        default=None
    )
