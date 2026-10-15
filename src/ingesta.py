"""
Ingesta reproducible (capa Bronze): descarga, trazabilidad y carga.

Estructura que se crea en Bronze (un subdirectorio por período, porque
todos los períodos tienen archivos con el mismo nombre):

    data/bronze/2025/main_metadata.csv
    data/bronze/202601/picks_bans.csv
    data/bronze/catalogos/heroes.json
    ...

Bronze conserva los datos TAL COMO LLEGAN: aquí no se limpia ni se transforma nada.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from . import config


# ---------------------------------------------------------------------------
# Descarga desde Kaggle
# ---------------------------------------------------------------------------
def verificar_token_kaggle() -> Path:
    """Comprueba que exista kaggle.json SIN mostrar su contenido."""
    token = Path.home() / ".kaggle" / "kaggle.json"
    if not token.is_file():
        raise FileNotFoundError(
            f"No se encontró {token}. Descárgalo desde Kaggle → Settings → API → Create New Token."
        )
    return token


def descargar_archivo(periodo: str, archivo: str, forzar: bool = False) -> Path:
    """Descarga UN archivo del dataset (p. ej. '202601/picks_bans.csv') a Bronze.

    Es idempotente: si el archivo ya existe, no se vuelve a descargar
    (a menos que forzar=True).
    """
    destino_dir = config.BRONZE / periodo
    destino = destino_dir / archivo
    if destino.is_file() and not forzar:
        return destino

    verificar_token_kaggle()
    destino_dir.mkdir(parents=True, exist_ok=True)
    ruta_en_dataset = f"{periodo}/{archivo}"
    # "python -m kaggle" usa el kaggle del MISMO entorno virtual que el notebook
    # (evita el error "comando kaggle no encontrado"). Igual que en el NoteBook07.
    cmd = [
        sys.executable, "-m", "kaggle", "datasets", "download",
        "-d", config.KAGGLE_DATASET,
        "-f", ruta_en_dataset,
        "-p", str(destino_dir),
        "--force",
    ]
    # encoding="utf-8": la barra de progreso de kaggle usa caracteres que la consola
    # de Windows (cp1252) no sabe leer; sin esto aparecen errores "charmap" (inofensivos).
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"Falló la descarga de {ruta_en_dataset}:\n{r.stderr or r.stdout}")

    # Kaggle puede entregar el archivo comprimido (archivo.csv.zip o archivo.zip)
    for zip_path in list(destino_dir.glob("*.zip")):
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(destino_dir)
        zip_path.unlink()

    if not destino.is_file():
        raise FileNotFoundError(
            f"La descarga terminó pero no aparece {destino}. "
            f"Revisa en Kaggle que exista la ruta '{ruta_en_dataset}'."
        )
    return destino


def descargar_periodos(periodos: list[str], archivos: list[str], forzar: bool = False) -> list[Path]:
    """Descarga varios archivos para varios períodos, mostrando el progreso."""
    rutas = []
    total = len(periodos) * len(archivos)
    i = 0
    for periodo in periodos:
        for archivo in archivos:
            i += 1
            print(f"[{i:>3}/{total}] {periodo}/{archivo} ...", end=" ", flush=True)
            try:
                ruta = descargar_archivo(periodo, archivo, forzar=forzar)
                print(f"OK ({ruta.stat().st_size / 1024**2:,.1f} MB)")
                rutas.append(ruta)
            except Exception as e:   # se informa y se continúa con el resto
                print(f"ERROR -> {e}")
    return rutas


# ---------------------------------------------------------------------------
# Descarga de catálogos (OpenDota)
# ---------------------------------------------------------------------------
def descargar_catalogo(url: str, nombre: str, forzar: bool = False) -> Path:
    """Guarda un catálogo JSON público en data/bronze/catalogos/<nombre>.json."""
    destino = config.CATALOGOS / f"{nombre}.json"
    if destino.is_file() and not forzar:
        return destino
    req = urllib.request.Request(url, headers={"User-Agent": "UNAJ-BigData-EDA/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        datos = json.loads(resp.read().decode("utf-8"))
    destino.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    return destino


def descargar_catalogos(forzar: bool = False) -> None:
    for url, nombre in [(config.URL_HEROES, "heroes"), (config.URL_PARCHES, "parches")]:
        ruta = descargar_catalogo(url, nombre, forzar=forzar)
        print(f"Catálogo {nombre:<8} OK  ->  {ruta.relative_to(config.RAIZ).as_posix()}")


def cargar_heroes() -> pd.DataFrame:
    """Catálogo de héroes: hero_id -> nombre legible, atributo, tipo de ataque y roles."""
    datos = json.loads((config.CATALOGOS / "heroes.json").read_text(encoding="utf-8"))
    df = pd.DataFrame(datos).rename(columns={
        "id": "hero_id", "localized_name": "heroe",
        "primary_attr": "atributo", "attack_type": "tipo_ataque",
    })
    df["roles"] = df["roles"].apply(lambda r: ", ".join(r) if isinstance(r, list) else r)
    return df[["hero_id", "heroe", "atributo", "tipo_ataque", "roles"]]


def cargar_parches() -> pd.DataFrame:
    """Catálogo de parches: número interno -> nombre legible ('7.41') y fecha de lanzamiento.

    La columna se llama 'parche' (no 'version') porque main_metadata ya trae una
    columna 'version' con otro significado (versión del procesamiento de datos).
    """
    datos = json.loads((config.CATALOGOS / "parches.json").read_text(encoding="utf-8"))
    df = pd.DataFrame(datos).rename(columns={"id": "patch", "name": "parche", "date": "lanzamiento"})
    # El catálogo mezcla formatos ("...T00:00:00Z" y "...T00:00:00.000Z"): ISO8601 acepta ambos
    df["lanzamiento"] = pd.to_datetime(df["lanzamiento"], utc=True, format="ISO8601").dt.tz_localize(None)
    return df[["patch", "parche", "lanzamiento"]]


# ---------------------------------------------------------------------------
# Trazabilidad
# ---------------------------------------------------------------------------
def _sha256(ruta: Path, bloque: int = 2**20) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(bloque), b""):
            h.update(trozo)
    return h.hexdigest()


def generar_manifiesto(guardar: bool = True) -> pd.DataFrame:
    """Inventario de Bronze: período, archivo, tamaño, huella SHA-256 y fecha.

    La huella permite demostrar que dos personas analizaron exactamente los
    mismos archivos, aunque el dataset de Kaggle se actualice después.
    Se guarda como CSV (outputs/) y como JSON (data/bronze/manifest.json).
    """
    filas = []
    for ruta in sorted(list(config.BRONZE.glob("*/*.csv")) + list(config.BRONZE.glob("*/*.json"))):
        filas.append({
            "periodo": ruta.parent.name,
            "archivo": ruta.name,
            "ruta_relativa": ruta.relative_to(config.RAIZ).as_posix(),
            "tamano_mb": round(ruta.stat().st_size / 1024**2, 3),
            "sha256": _sha256(ruta),
            "descargado_utc": datetime.fromtimestamp(ruta.stat().st_mtime, tz=timezone.utc)
                                      .strftime("%Y-%m-%d %H:%M"),
        })
    df = pd.DataFrame(filas)
    if guardar and not df.empty:
        df.to_csv(config.OUTPUTS / "manifiesto_bronze.csv", index=False, encoding="utf-8-sig")
        manifiesto = {
            "dataset": config.KAGGLE_DATASET,
            "catalogos": [config.URL_HEROES, config.URL_PARCHES],
            "generado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "capa": "bronze",
            "archivos": df.to_dict(orient="records"),
        }
        (config.BRONZE / "manifest.json").write_text(
            json.dumps(manifiesto, indent=2, ensure_ascii=False), encoding="utf-8")
    return df


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------
def cargar_tabla(archivo: str, periodos: list[str], columnas: list[str] | None = None,
                 **kwargs_read_csv) -> pd.DataFrame:
    """Une el mismo archivo de varios períodos en un solo DataFrame.

    - Agrega 'periodo_origen' para saber de qué carpeta vino cada fila.
    - columnas: lista de columnas a leer; las que no existan se ignoran sin error
      (útil para players.csv, que tiene muchísimas columnas).
    """
    partes = []
    for periodo in periodos:
        ruta = config.BRONZE / periodo / archivo
        if not ruta.is_file():
            print(f"  (aviso) no existe {ruta.relative_to(config.RAIZ).as_posix()}; se omite")
            continue
        usecols = (lambda c: c in columnas) if columnas else None
        df = pd.read_csv(ruta, low_memory=False, usecols=usecols, **kwargs_read_csv)
        df["periodo_origen"] = periodo
        partes.append(df)
    if not partes:
        raise FileNotFoundError(f"No hay ningún '{archivo}' descargado para {periodos}")
    return pd.concat(partes, ignore_index=True)


def columnas_de(archivo: str, periodo: str) -> list[str]:
    """Lee solo el encabezado de un CSV (rápido, aunque el archivo pese GB)."""
    return list(pd.read_csv(config.BRONZE / periodo / archivo, nrows=0).columns)
