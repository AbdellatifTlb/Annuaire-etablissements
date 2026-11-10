from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO

import pandas as pd


REQUIRED_COLUMNS = {
    "identifiant_de_l_etablissement",
    "nom_etablissement",
}

IDENTIFIER_COLUMNS = {
    "identifiant_de_l_etablissement",
    "code_postal",
    "code_commune",
    "code_departement",
    "code_academie",
    "code_region",
    "siren_siret",
    "code_nature",
    "code_type_contrat_prive",
    "etablissement_mere",
    "code_circonscription",
    "code_zone_animation_pedagogique",
    "code_bassin_formation",
}


def _read_source(source: str | Path | bytes | bytearray | BinaryIO) -> bytes:
    if isinstance(source, (str, Path)):
        try:
            return Path(source).read_bytes()
        except OSError as error:
            raise ValueError(f"Impossible de lire le fichier CSV : {error}") from error
    if isinstance(source, (bytes, bytearray)):
        return bytes(source)
    if hasattr(source, "getvalue"):
        return source.getvalue()
    try:
        source.seek(0)
        return source.read()
    except (AttributeError, OSError) as error:
        raise ValueError("La source fournie n’est pas un fichier CSV lisible.") from error


def load_annuaire(source: str | Path | bytes | bytearray | BinaryIO) -> pd.DataFrame:
    """Load an annuaire CSV while preserving identifiers and Windows text."""
    raw = _read_source(source)
    if not raw.strip():
        raise ValueError("Le fichier CSV est vide.")

    sample = raw[:65536]
    if sample.startswith(b"\xef\xbb\xbf"):
        encoding = "utf-8-sig"
    else:
        try:
            sample.decode("utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            encoding = "cp1252"

    first_line = sample.splitlines()[0].decode(encoding, errors="replace")
    delimiters = (";", ",", "\t", "|")
    delimiter = max(delimiters, key=first_line.count)
    if first_line.count(delimiter) == 0:
        raise ValueError(
            "Le séparateur du fichier n’a pas pu être identifié. "
            "Utilisez un CSV séparé par des points-virgules, virgules ou tabulations."
        )

    try:
        frame = pd.read_csv(
            io.BytesIO(raw),
            sep=delimiter,
            encoding=encoding,
            encoding_errors="replace",
            low_memory=False,
            dtype={column: "string" for column in IDENTIFIER_COLUMNS},
        )
    except (pd.errors.ParserError, UnicodeError, ValueError) as error:
        raise ValueError(f"Le fichier CSV n’a pas pu être lu : {error}") from error

    frame.columns = [str(column).strip().lstrip("\ufeff") for column in frame.columns]
    if frame.empty:
        raise ValueError("Le fichier ne contient aucun établissement.")
    missing_columns = sorted(REQUIRED_COLUMNS.difference(frame.columns))
    if missing_columns:
        expected = ", ".join(sorted(REQUIRED_COLUMNS))
        raise ValueError(
            "Ce fichier ne ressemble pas à l’annuaire attendu. "
            f"Colonnes requises manquantes : {', '.join(missing_columns)}. "
            f"Colonnes attendues : {expected}."
        )
    return frame


def display_value(value: object) -> str:
    if pd.isna(value):
        return "Non renseigné"
    return str(value).strip() or "Non renseigné"


def numeric_series(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(float("nan"), index=frame.index, dtype="float64")
    values = frame[column].astype("string").str.replace(",", ".", regex=False)
    return pd.to_numeric(values, errors="coerce")


def truthy_series(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(False, index=frame.index, dtype=bool)
    values = frame[column].astype("string").str.strip().str.lower()
    return values.isin({"1", "1.0", "oui", "true", "vrai", "yes"})


def filter_annuaire(
    frame: pd.DataFrame,
    search: str,
    regions: list[str],
    departments: list[str],
    establishment_types: list[str],
    statuses: list[str],
    states: list[str],
    commune: str,
    services: list[tuple[str, str]],
) -> pd.DataFrame:
    result = frame
    for column, selected in (
        ("libelle_region", regions),
        ("libelle_departement", departments),
        ("type_etablissement", establishment_types),
        ("statut_public_prive", statuses),
        ("etat", states),
    ):
        if selected and column in result.columns:
            result = result[result[column].astype("string").isin(selected)]

    if commune and "nom_commune" in result.columns:
        result = result[
            result["nom_commune"].astype("string").str.contains(
                commune, case=False, na=False, regex=False
            )
        ]

    if search:
        searchable_columns = [
            column
            for column in (
                "nom_etablissement",
                "identifiant_de_l_etablissement",
                "nom_commune",
                "code_postal",
                "adresse_1",
                "libelle_departement",
                "telephone",
                "mail",
            )
            if column in result.columns
        ]
        if searchable_columns:
            matches = pd.Series(False, index=result.index)
            for column in searchable_columns:
                matches |= result[column].astype("string").str.contains(
                    search, case=False, na=False, regex=False
                )
            result = result[matches]

    for column, _label in services:
        result = result[truthy_series(result, column)]
    return result
