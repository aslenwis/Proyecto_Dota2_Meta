"""
Configuración central del proyecto (versión 2).

Todas las rutas se construyen a partir de la RAÍZ DEL PROYECTO, nunca desde
una ruta absoluta (D:\\...). Así el notebook funciona en cualquier computadora
mientras se respete la estructura interna de carpetas.

Si cambias algo aquí, REINICIA EL KERNEL: Python importa este archivo una sola vez.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Raíz del proyecto
# ---------------------------------------------------------------------------
MARCADOR_RAIZ = "proyecto.marker"   # archivo vacío que identifica la raíz


def encontrar_raiz(inicio: Path | None = None) -> Path:
    """Sube carpeta por carpeta hasta encontrar el archivo marcador."""
    actual = (inicio or Path.cwd()).resolve()
    for carpeta in [actual, *actual.parents]:
        if (carpeta / MARCADOR_RAIZ).is_file():
            return carpeta
    raise FileNotFoundError(
        f"No se encontró '{MARCADOR_RAIZ}' subiendo desde {actual}. "
        "Abre el notebook desde dentro de la carpeta del proyecto."
    )


RAIZ = encontrar_raiz(Path(__file__).parent)

# ---------------------------------------------------------------------------
# 2. Rutas del proyecto (arquitectura medallion)
# ---------------------------------------------------------------------------
DATA = RAIZ / "data"
BRONZE = DATA / "bronze"          # datos crudos, tal como se descargan
CATALOGOS = BRONZE / "catalogos"  # tablas de referencia (héroes, parches)
SILVER = DATA / "silver"          # tabla analítica validada
GOLD = DATA / "gold"              # indicadores listos para presentar
OUTPUTS = RAIZ / "outputs"        # manifiesto, calidad, diccionario
FIGURAS = RAIZ / "reports" / "figures"
DOCS = RAIZ / "docs"

for _carpeta in (BRONZE, CATALOGOS, SILVER, GOLD, OUTPUTS, FIGURAS):
    _carpeta.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 3. Fuentes de datos
# ---------------------------------------------------------------------------
KAGGLE_DATASET = "bwandowando/dota-2-pro-league-matches-2023"
KAGGLE_URL = f"https://www.kaggle.com/datasets/{KAGGLE_DATASET}"

# Catálogos públicos de OpenDota: traducen códigos a nombres legibles.
# Son clave para que una audiencia que no juega Dota entienda los gráficos.
URL_HEROES = "https://api.opendota.com/api/heroes"            # hero_id -> nombre
URL_PARCHES = "https://api.opendota.com/api/constants/patch"  # patch -> "7.41" + fecha

# ---------------------------------------------------------------------------
# 4. Alcance de la descarga  (✏️ JUSTIFÍCALO EN LA SECCIÓN 3.2 DEL NOTEBOOK)
# ---------------------------------------------------------------------------
# El docente aprobó 2025 → sep-2026 y dijo que 2026 solo también es aceptable.
# Ojo: según el catálogo de OpenDota, 2026 solo contiene 2 parches
# (7.40 desde dic-2025 y 7.41 desde mar-2026). Para comparar "parche a parche"
# conviene incluir 2025 (7.37 → 7.41 = 5 parches).
INCLUIR_2025 = True

MESES_2026 = [f"2026{m:02d}" for m in range(1, 10)]         # 202601 ... 202609
PERIODOS = (["2025"] if INCLUIR_2025 else []) + MESES_2026

# Tablas livianas: se descargan para TODOS los períodos.
ARCHIVOS_LIVIANOS = ["main_metadata.csv", "picks_bans.csv", "teams.csv"]

# players.csv es pesado (~160 MB por mes). Solo se usa para reglas de
# consistencia (10 jugadores por partida, marcador = suma de kills).
# Por eso se descarga solo para 2026 y se cargan pocas columnas.
ARCHIVO_PLAYERS = "players.csv"
PERIODOS_PLAYERS = MESES_2026
COLS_PLAYERS = ["match_id", "player_slot", "hero_id", "kills", "deaths", "assists",
                "isRadiant", "win", "leaver_status"]

# Archivos que NO se descargan, por decisión de gobierno de datos.
ARCHIVOS_EXCLUIDOS = {
    "chat.csv": "Texto libre escrito por jugadores (privacidad); no aporta a la pregunta",
    "all_word_counts.csv": "Derivado del chat; mismo motivo",
    "cosmetics.csv": "Objetos cosméticos; sin relación con la pregunta",
    "teamfights.csv": "Detalle de peleas; no se usa para medir el meta",
    "objectives.csv": "Eventos del mapa (torres, Roshan); fuera del alcance",
    "radiant_gold_adv.csv": "Series de ventaja de oro; siguiente etapa",
    "radiant_exp_adv.csv": "Series de ventaja de experiencia; siguiente etapa",
}

# ---------------------------------------------------------------------------
# 5. Nombres de columnas (confirmados o por confirmar)
# ---------------------------------------------------------------------------
# main_metadata.csv: CONFIRMADAS con el archivo 202608 (39 columnas).
COLS_META_CLAVE = [
    "match_id", "leagueid", "start_date_time", "duration", "radiant_win",
    "patch", "game_mode", "lobby_type", "human_players",
    "radiant_score", "dire_score", "radiant_team_id", "dire_team_id",
    "first_blood_time", "region", "series_id", "series_type",
]

# picks_bans.csv: nombres habituales en datos de OpenDota. ⚠️ CONFÍRMALOS en la
# sección 4 del notebook y, si difieren, cámbialos SOLO aquí.
PB_PARTIDA = "match_id"
PB_ES_PICK = "is_pick"   # True = elegido (pick), False = prohibido (ban)
PB_HEROE = "hero_id"
PB_EQUIPO = "team"       # 0 = Radiant, 1 = Dire
PB_ORDEN = "order"       # turno dentro del draft (0, 1, 2, ...)

# ---------------------------------------------------------------------------
# 6. Traducciones de códigos (constantes de OpenDota)
# ---------------------------------------------------------------------------
MODOS_JUEGO = {1: "All Pick", 2: "Captains Mode", 3: "Random Draft", 4: "Single Draft",
               5: "All Random", 16: "Captains Draft", 22: "Ranked All Pick"}
TIPOS_LOBBY = {0: "Normal", 1: "Práctica (torneo privado)", 2: "Torneo", 7: "Ranked"}

# ---------------------------------------------------------------------------
# 7. Parámetros de análisis
# ---------------------------------------------------------------------------
MUESTRA_MINIMA = 30   # partidas mínimas para interpretar el win rate de un héroe
                      # (misma regla práctica del NoteBook07 del curso)
SEMILLA = 42          # para cualquier muestreo aleatorio (reproducibilidad)
