"""
Evaluación de calidad de datos basada en reglas.

Misma idea que el laboratorio de Gobierno de Datos (semana 5) y el cuadro DAMA
del NoteBook07: cada regla es una Serie booleana (True = el registro CUMPLE)
más su contexto (dimensión, tabla, impacto y responsable).

Dimensiones DAMA-DMBOK usadas:
  Completitud   ¿están los datos que necesito?
  Unicidad      ¿cuento dos veces la misma cosa?
  Validez       ¿el valor pertenece al dominio permitido (formato, catálogo)?
  Consistencia  ¿los datos concuerdan entre columnas o entre tablas?
  Plausibilidad ¿el valor es creíble en el mundo real? (precisión interna)
  Oportunidad   ¿los datos cubren el período que la pregunta necesita?
"""
from __future__ import annotations

import pandas as pd

DIMENSIONES = ("Completitud", "Unicidad", "Validez", "Consistencia", "Plausibilidad", "Oportunidad")


class EvaluadorCalidad:
    """Acumula reglas evaluadas y produce la tabla que pide la rúbrica."""

    def __init__(self) -> None:
        self._resultados: list[dict] = []
        self._fallas: dict[str, pd.Index] = {}

    def evaluar(
        self,
        regla: str,
        dimension: str,
        tabla: str,
        cumple: pd.Series,
        impacto: str,
        responsable: str = "Por definir",
    ) -> dict:
        """Registra una regla.

        regla       : la regla en palabras o como expresión (p. ej. "duration > 0").
        dimension   : una de DIMENSIONES.
        tabla       : sobre qué tabla se evalúa (main_metadata, players...).
        cumple      : Serie booleana, True donde el registro cumple la regla.
        impacto     : qué conclusión o decisión se distorsiona si no se cumple.
        responsable : quién debería corregirlo (data owner, steward, el equipo...).
        """
        if dimension not in DIMENSIONES:
            raise ValueError(f"dimension debe ser una de {DIMENSIONES}")
        cumple = pd.Series(cumple).fillna(False).astype(bool)
        total = int(len(cumple))
        fallan = int((~cumple).sum())
        fila = {
            "regla": regla,
            "dimension": dimension,
            "tabla": tabla,
            "cumple": total - fallan,
            "total": total,
            "incumplimientos": fallan,
            "cumplimiento_pct": round(100 * (total - fallan) / total, 2) if total else None,
            "impacto": impacto,
            "responsable": responsable,
        }
        # Si se re-ejecuta la celda, se reemplaza la regla en vez de duplicarla
        self._resultados = [r for r in self._resultados if r["regla"] != regla]
        self._resultados.append(fila)
        self._fallas[regla] = cumple.index[~cumple]
        return fila

    def resumen(self) -> pd.DataFrame:
        """Tabla de resultados ordenada de peor a mejor cumplimiento."""
        df = pd.DataFrame(self._resultados)
        if df.empty:
            return df
        return df.sort_values("cumplimiento_pct").reset_index(drop=True)

    def indices_que_fallan(self, regla: str) -> pd.Index:
        """Índices de los registros que NO cumplen una regla (para inspeccionarlos)."""
        return self._fallas[regla]

    def guardar(self, ruta) -> None:
        self.resumen().to_csv(ruta, index=False, encoding="utf-8-sig")
