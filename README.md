# ¿Quién manda en el draft? Equilibrio y diversidad del meta profesional de Dota 2 (2025–2026)

**Curso:** Big Data — UNAJ 2026-2 · **Proyecto:** Unidad 1 — EDA y calidad de datos
**Integrantes:** Apaza Mamani Ruben · Apaza Suca Elwin Junior · Mamani Quilca Richard · Quiza Apaza Kevin Manuel · Vilca Ochoa Nathaly Fiorella

## Pregunta motivadora (aprobada por el docente)
> ¿Qué tan equilibrado y diverso ha sido el meta competitivo de Dota 2 parche a parche,
> y cómo podría esa información ayudar a los analistas de equipos a priorizar su preparación de draft?

¿No conoces Dota 2? Lee primero `docs/glosario_dota2.md` (5 minutos).

## Cómo ejecutar en cualquier computadora (reproducible)

**Requisitos:** Python 3.10 o superior (probado con 3.12), [Git](https://git-scm.com/downloads), VS Code con la extensión *Jupyter* y una cuenta gratuita de Kaggle.

1. **Clona el repositorio** en la carpeta que quieras (la ruta no importa):
   ```powershell
   git clone https://github.com/<usuario>/Proyecto_Dota2_Meta.git
   cd Proyecto_Dota2_Meta
   ```
2. **Crea un entorno virtual nuevo** e instala las dependencias:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```
   - Si PowerShell no deja activar el entorno: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a intentar.
   - En Linux o macOS: `python3 -m venv .venv` y `source .venv/bin/activate`.
   - La carpeta `.venv/` no se sube a GitHub (está en `.gitignore`).
3. **Coloca tu propio token de Kaggle.** En kaggle.com → *Settings* → *API* → *Create New Token* se descarga `kaggle.json`. Guárdalo en `C:\Users\<tu_usuario>\.kaggle\kaggle.json` (Linux/macOS: `~/.kaggle/kaggle.json`). Cada integrante usa el suyo; **nunca se sube al repositorio**.
4. **Ejecuta el notebook.** Abre `notebooks/01_eda_calidad_dota2.ipynb` en VS Code, elige el kernel `.venv` y usa **Restart → Run All**.
   La primera vez, las secciones 3.3 y 3.4 descargan los catálogos de OpenDota y las tablas de Kaggle a `data/bronze/` (puede tardar varios minutos); lo ya descargado no se repite.

> No hay rutas absolutas: todo se resuelve desde `proyecto.marker`. No lo borres.

### Cómo comprobar que obtuviste lo mismo
| Verificación | Valor esperado |
|---|---|
| Todas las celdas | Sin errores |
| Partidas en `main_metadata` | 44 988 |
| Acciones de draft en `picks_bans` | 1 062 700 |
| Reglas de calidad | 19, con 14 al 100 % |
| Silver | 44 115 partidas · 4 199 acciones rechazadas |
| Héroes efectivos en 7.41 | 100.2 |

Para comprobar que descargaste **exactamente los mismos archivos**, compara tus huellas SHA-256 con las del repositorio (ejecútalo con el entorno activado, desde la raíz del proyecto):
```powershell
python -c "import io,subprocess,pandas as pd; a=pd.read_csv(io.BytesIO(subprocess.check_output(['git','show','HEAD:outputs/manifiesto_bronze.csv'])),encoding='utf-8-sig'); b=pd.read_csv('outputs/manifiesto_bronze.csv',encoding='utf-8-sig'); m=a.merge(b,on='ruta_relativa',how='outer',suffixes=('_repo','_mio')); d=m[m.sha256_repo!=m.sha256_mio]; print('Archivos identicos:',len(m)-len(d),'de',len(m)); print(d[['ruta_relativa']].to_string(index=False) if len(d) else 'Todos los SHA-256 coinciden')"
```
La columna `descargado_utc` siempre será distinta (es la fecha de tu descarga); lo que importa es `sha256`. Si algún archivo no coincide, casi siempre es porque Kaggle u OpenDota actualizaron la fuente después de nuestra descarga (por ejemplo, más partidas de 202609): no es un error del notebook, y el manifiesto sirve justamente para detectarlo.

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
│   └── archivo/                     # versiones anteriores (respaldo)
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
