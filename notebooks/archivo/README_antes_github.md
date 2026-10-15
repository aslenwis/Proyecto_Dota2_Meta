# ¿Quién manda en el draft? Equilibrio y diversidad del meta profesional de Dota 2 (2025–2026)

**Curso:** Big Data — UNAJ 2026-2 · **Proyecto:** Unidad 1 — EDA y calidad de datos
**Integrantes:** Apaza Mamani Ruben · Apaza Suca Elwin Junior · Mamani Quilca Richard · Quiza Apaza Kevin Manuel · Vilca Ochoa Nathaly Fiorella

## Pregunta motivadora (aprobada por el docente)
> ¿Qué tan equilibrado y diverso ha sido el meta competitivo de Dota 2 parche a parche,
> y cómo podría esa información ayudar a los analistas de equipos a priorizar su preparación de draft?

¿No conoces Dota 2? Lee primero `docs/glosario_dota2.md` (5 minutos).

## Cómo ejecutar (reproducible)

1. Activa el entorno virtual e instala dependencias:
   ```powershell
   ..\Dota2env20262\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```
2. Coloca tu token de Kaggle en `C:\Users\<tu_usuario>\.kaggle\kaggle.json`.
3. Abre `notebooks/01_eda_calidad_dota2.ipynb` y ejecuta **Kernel → Restart & Run All**.
   Las secciones 3.3 y 3.4 descargan solo lo necesario (catálogos de OpenDota + tablas de Kaggle);
   lo ya descargado no se repite.

> No hay rutas absolutas: todo se resuelve desde `proyecto.marker`. No lo borres.

## Alcance de los datos
| Tabla | Períodos | Uso |
|---|---|---|
| main_metadata, picks_bans, teams | 2025 + ene–sep 2026 | Análisis principal (5 parches: 7.37–7.41) |
| players (pocas columnas) | ene–sep 2026 | Solo reglas de consistencia |
| Catálogos OpenDota (héroes, parches) | — | Traducir códigos a nombres |

## Estructura
```
Proyecto_Dota2_Meta/
├── proyecto.marker            # marca la raíz (no borrar)
├── requirements.txt
├── notebooks/
│   ├── 01_eda_calidad_dota2.ipynb   # ENTREGABLE (Parte A = rúbrica, Parte B = pregunta)
│   └── archivo/                     # versiones anteriores
├── src/
│   ├── config.py      # rutas, períodos, nombres de columnas, parámetros
│   ├── ingesta.py     # Bronze: descarga Kaggle/OpenDota, manifiesto SHA-256, carga
│   ├── calidad.py     # reglas de calidad DAMA (6 dimensiones)
│   └── metricas.py    # diversidad, equilibrio y prioridad de draft
├── data/bronze | silver | gold      # medallion (no se sube a git)
├── docs/
│   ├── glosario_dota2.md    # para la audiencia que no juega
│   └── diccionario_datos.md # diccionario con columnas reales
├── outputs/          # manifiesto, catálogo técnico, diccionario, calidad, rechazados
└── reports/figures/  # gráficos para la exposición
```

## Fuentes
- Dota 2 Pro League Matches 2016–2026 — Kaggle (`bwandowando/dota-2-pro-league-matches-2023`) · Autor: BwandoWando · Licencia: CC0 Public Domain.
- OpenDota API pública: `/api/heroes` y `/api/constants/patch`.
