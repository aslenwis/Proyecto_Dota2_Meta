# Diccionario de datos — Dota 2 Pro League (2025–2026)

Formato de la rúbrica + dos columnas para la audiencia: **nombre simple** y **ejemplo real**.
La versión que se usa en el notebook está en la sección 7.2 y se exporta a `outputs/diccionario_datos.csv`.

## main_metadata.csv — 1 fila = 1 partida profesional
Columnas confirmadas con el archivo `202608/main_metadata.csv` (39 columnas en total).

| Columna | Nombre simple | Descripción | Ejemplo | Tipo o escala | Unidad o dominio | Importancia |
|---|---|---|---|---|---|---|
| match_id | Código de partida | Identificador único de la partida | 8923283343 | Identificador | Entero positivo, único | Une todas las tablas |
| start_date_time | Fecha y hora | Inicio de la partida | 2026-08-01 00:18:32 | Temporal | Fecha válida en el período | Asigna mes y parche |
| duration | Duración | Duración de la partida | 2743 (≈ 46 min) | Numérica continua | Segundos, > 0 | Ritmo del meta |
| radiant_win | ¿Ganó Radiant? | True si ganó Radiant | True | Booleana | True / False | Base del win rate |
| patch | Parche | Versión del juego (código interno) | 60 (= 7.41) | Categórica ordinal | Catálogo de parches OpenDota | Eje "parche a parche" |
| game_mode | Modo de draft | Formato de selección de héroes | 2 (= Captains Mode) | Categórica codificada | Constantes OpenDota | Solo Captains Mode es comparable |
| lobby_type | Tipo de sala | Tipo de partida | 1 | Categórica codificada | Constantes OpenDota | Contexto |
| leagueid | Liga | Torneo de la partida | 20030 | Identificador | Entero positivo | Peso de cada liga |
| human_players | Jugadores humanos | Personas en la partida | 10 | Numérica discreta | Debe ser 10 | Detecta partidas incompletas |
| radiant_score / dire_score | Eliminaciones | Kills totales por lado | 37 / 30 | Numérica discreta | ≥ 0 | Consistencia con players |
| first_blood_time | Primera sangre | Segundo de la primera eliminación | 241 | Numérica continua | Segundos, ≥ 0 y < duración | Plausibilidad |
| radiant_team_id / dire_team_id | Equipos | Identificador de cada equipo | 10207448 | Identificador | Entero; puede faltar | Completitud |
| version | ⚠️ Versión de procesamiento | **No es el parche**: versión del procesamiento de datos | 22.0 | Categórica | — | Evitar confusión con `patch` |

## picks_bans.csv — 1 fila = 1 acción del draft (pick o ban)
Columnas confirmadas: `is_pick`, `hero_id`, `team`, `order`, `match_id`, `leagueid` (1 062 700 filas).

| Columna | Nombre simple | Descripción | Ejemplo | Tipo o escala | Unidad o dominio | Importancia |
|---|---|---|---|---|---|---|
| match_id | Código de partida | Partida a la que pertenece la acción | 8107483721 | Clave foránea | Existe en main_metadata (100 %) | Integridad referencial |
| is_pick | ¿Elegido o prohibido? | True = pick; False = ban | True | Booleana | True / False | Separa picks de bans |
| hero_id | Héroe | Héroe elegido o prohibido | 2 (= Axe) | Categórica (código) | Catálogo de héroes (127) | Unidad del meta |
| team | Lado | Equipo que hizo la acción | 0 | Categórica binaria | 0 = Radiant, 1 = Dire (verificado con players: 100 %) | Win rate por héroe |
| order | Turno | Posición de la acción en el draft | 7 | Ordinal | 0 a 23 en un draft completo | Clave junto a match_id |
| leagueid | Liga | Torneo de la partida (repetido de main_metadata) | 17163 | Identificador | Entero positivo | Contexto |

## teams.csv — 1 fila = los dos equipos de una partida

| Columna | Nombre simple | Descripción | Ejemplo |
|---|---|---|---|
| match_id | Código de partida | Partida (1 repetida: 8954038843) | 8954038843 |
| radiant.name / dire.name | Nombre del equipo | Nombre de cada equipo | HULIGANI |
| radiant.tag / dire.tag | Sigla | Abreviatura del equipo | — |

## Columnas derivadas (creadas en el notebook)

| Columna | Nombre simple | Cómo se calcula | Ejemplo |
|---|---|---|---|
| parche | Parche legible | `patch` → catálogo de OpenDota | 7.41 |
| duracion_min | Duración (min) | `duration / 60` | 45.7 |
| ganador | Lado ganador | `radiant_win` → "Radiant" / "Dire" | Radiant |
| modo_juego | Modo legible | `game_mode` → nombre | Captains Mode |
| heroe | Nombre del héroe | `hero_id` → catálogo de OpenDota | Anti-Mage |
| gano | ¿Ganó quien eligió? | lado de la acción + `radiant_win` | True |
