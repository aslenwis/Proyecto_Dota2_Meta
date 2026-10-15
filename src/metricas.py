"""
Métricas para responder la pregunta del proyecto:

    ¿Qué tan EQUILIBRADO y DIVERSO ha sido el meta competitivo parche a parche,
    y cómo ayudaría eso a un analista a priorizar su preparación de draft?

Todas son DESCRIPTIVAS: resumen lo que ocurrió, no explican por qué.

Explicación sencilla de cada métrica (para la exposición):

  pick rate      % de partidas en que un héroe fue ELEGIDO.
  ban rate       % de partidas en que un héroe fue PROHIBIDO.
  contest rate   % de partidas en que un héroe fue elegido O prohibido.
                 Mide "cuánto le importa" un héroe a los equipos: es la
                 señal principal de prioridad en el draft.
  win rate       % de veces que el equipo que eligió al héroe ganó.
                 Solo se interpreta con una muestra mínima de partidas.

  cobertura      % del total de héroes del juego que se eligió al menos una vez.
  cuota top-10   % de todos los picks que se llevan los 10 héroes más elegidos.
                 Alta = meta concentrado en pocos héroes.
  entropía norm. 0 = siempre se elige el mismo héroe; 1 = todos por igual.
  héroes efect.  "Es como si se jugaran N héroes con la misma frecuencia".
                 Es la forma más intuitiva de explicar la diversidad.
  Gini           0 = uso perfectamente parejo; 1 = todo concentrado en uno.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Medidas de concentración / diversidad sobre un vector de conteos
# ---------------------------------------------------------------------------
def _completar(conteos: pd.Series, n_total: int | None) -> np.ndarray:
    """Agrega ceros por los héroes que existen pero no se usaron (si n_total > observados)."""
    x = np.asarray(conteos, dtype=float)
    x = x[x > 0]
    if n_total and n_total > len(x):
        x = np.concatenate([x, np.zeros(n_total - len(x))])
    return x


def entropia_normalizada(conteos: pd.Series, n_total: int | None = None) -> float:
    """Entropía de Shannon dividida por su máximo posible (0 a 1)."""
    x = _completar(conteos, n_total)
    p = x[x > 0] / x.sum()
    h = -(p * np.log(p)).sum()
    n = len(x)
    return float(h / np.log(n)) if n > 1 else 0.0


def heroes_efectivos(conteos: pd.Series) -> float:
    """exp(entropía): número de héroes 'equivalentes' usados por igual."""
    x = np.asarray(conteos, dtype=float)
    p = x[x > 0] / x.sum()
    return float(np.exp(-(p * np.log(p)).sum()))


def gini(conteos: pd.Series, n_total: int | None = None) -> float:
    """Coeficiente de Gini del uso de héroes (0 = parejo, 1 = concentrado)."""
    x = np.sort(_completar(conteos, n_total))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return float("nan")
    i = np.arange(1, n + 1)
    return float((2 * (i * x).sum()) / (n * x.sum()) - (n + 1) / n)


def cuota_top(conteos: pd.Series, n: int = 10) -> float:
    """% de los picks que concentran los n héroes más elegidos."""
    x = pd.Series(conteos).sort_values(ascending=False)
    return float(100 * x.head(n).sum() / x.sum())


# ---------------------------------------------------------------------------
# Tablas por parche
# ---------------------------------------------------------------------------
def diversidad_por_parche(draft: pd.DataFrame, n_heroes_total: int,
                          col_parche: str = "parche") -> pd.DataFrame:
    """Una fila por parche con todas las medidas de diversidad de los PICKS.

    draft: tabla Silver (una fila por acción de draft) con columnas
           'es_pick', 'hero_id', 'match_id' y la columna del parche.
    """
    picks = draft[draft["es_pick"]]
    filas = []
    for parche, g in picks.groupby(col_parche, observed=True, sort=True):
        c = g["hero_id"].value_counts()
        filas.append({
            col_parche: parche,
            "partidas": g["match_id"].nunique(),
            "picks": len(g),
            "heroes_distintos": int(c.size),
            "cobertura_pct": 100 * c.size / n_heroes_total,
            "cuota_top10_pct": cuota_top(c, 10),
            "entropia_norm": entropia_normalizada(c, n_heroes_total),
            "heroes_efectivos": heroes_efectivos(c),
            "gini": gini(c, n_heroes_total),
        })
    return pd.DataFrame(filas)


def tasas_por_heroe(draft: pd.DataFrame, col_parche: str = "parche") -> pd.DataFrame:
    """Picks, bans, pick/ban/contest rate y win rate por héroe y parche.

    Las tasas se calculan sobre el número de partidas del parche, no sobre
    el número de picks: así se leen como "en X % de las partidas...".
    """
    d = draft.assign(
        es_ban=~draft["es_pick"],
        victoria_pick=draft["es_pick"] & draft["gano"],   # solo cuenta victorias de picks
    )
    partidas = d.groupby(col_parche, observed=True)["match_id"].nunique().rename("partidas_parche")
    agg = (d.groupby([col_parche, "hero_id"], observed=True)
            .agg(picks=("es_pick", "sum"), bans=("es_ban", "sum"), victorias=("victoria_pick", "sum"))
            .reset_index()
            .merge(partidas, on=col_parche))
    agg["pick_rate_pct"] = 100 * agg["picks"] / agg["partidas_parche"]
    agg["ban_rate_pct"] = 100 * agg["bans"] / agg["partidas_parche"]
    agg["contest_rate_pct"] = agg["pick_rate_pct"] + agg["ban_rate_pct"]
    agg["win_rate_pct"] = np.where(agg["picks"] > 0, 100 * agg["victorias"] / agg["picks"].clip(lower=1), np.nan)
    return agg


def equilibrio_por_parche(tasas: pd.DataFrame, muestra_minima: int,
                          col_parche: str = "parche") -> pd.DataFrame:
    """Qué tan parejos son los win rates de los héroes con muestra suficiente.

    - desv_win_rate: dispersión de los win rates (menor = más equilibrado).
    - pct_heroes_45_55: % de héroes cuyo win rate está entre 45 % y 55 %.
    """
    t = tasas[tasas["picks"] >= muestra_minima]
    return (t.groupby(col_parche, observed=True)
             .agg(heroes_con_muestra=("hero_id", "nunique"),
                  desv_win_rate=("win_rate_pct", "std"),
                  win_rate_min=("win_rate_pct", "min"),
                  win_rate_max=("win_rate_pct", "max"),
                  pct_heroes_45_55=("win_rate_pct", lambda s: 100 * s.between(45, 55).mean()))
             .reset_index())
