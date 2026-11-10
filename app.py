from __future__ import annotations

import math
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from data_utils import (
    display_value,
    filter_annuaire,
    load_annuaire,
    numeric_series,
    truthy_series,
)


DEFAULT_CSV = Path(
    os.environ.get(
        "ANNUAIRE_CSV_PATH",
        r"C:\Users\SuperElectro\Downloads\annuaire_complet.csv",
    )
)
PAGE_SIZE = 25
MAX_MAP_POINTS = 5000

st.set_page_config(
    page_title="Annuaire des établissements",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
    .stApp { background: #f4f7fb; }
    [data-testid="stHeader"] { background: rgba(244,247,251,.9); }
    [data-testid="stSidebar"] { background: #fff; border-right: 1px solid #e7edf5; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: #172b4d; letter-spacing: -.025em; }
    .hero {
        padding: 1.65rem 1.9rem; margin: .25rem 0 1.4rem; border-radius: 20px;
        color: white; background: linear-gradient(115deg, #123b70 0%, #176b87 58%, #24a58b 100%);
        box-shadow: 0 12px 30px rgba(23, 67, 110, .16);
    }
    .hero h1 { color: white; font-size: 2rem; margin: 0 0 .4rem; }
    .hero p { color: #e2f1f8; margin: 0; font-size: .98rem; }
    [data-testid="stMetric"] {
        background: #fff; border: 1px solid #e7edf5; padding: 1rem 1.1rem;
        border-radius: 15px; box-shadow: 0 3px 12px rgba(26, 54, 93, .035);
    }
    [data-testid="stMetricLabel"] { color: #65758b; }
    [data-testid="stMetricValue"] { color: #16395f; font-family: 'Segoe UI', sans-serif; }
    [data-testid="stTabs"] button { font-weight: 600; }
    div[data-testid="stDataFrame"] { border: 1px solid #e6ecf3; border-radius: 12px; overflow: hidden; }
    .section-note { color: #6b7b90; font-size: .92rem; }
    .stButton > button, .stDownloadButton > button { border-radius: 9px; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False, max_entries=3)
def load_local_file(path: str, modified_ns: int, file_size: int) -> pd.DataFrame:
    return load_annuaire(path)


@st.cache_data(show_spinner=False, max_entries=2)
def load_uploaded_file(contents: bytes) -> pd.DataFrame:
    return load_annuaire(contents)


def available_values(frame: pd.DataFrame, column: str) -> list[str]:
    if column not in frame.columns:
        return []
    return sorted(
        frame[column].dropna().astype(str).str.strip().loc[lambda values: values.ne("")].unique(),
        key=str.casefold,
    )


def plotly_layout(fig: object, height: int = 330) -> object:
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, sans-serif", color="#43546c"),
        title_font=dict(family="Segoe UI, sans-serif", size=16, color="#1b3555"),
        legend_title_text="",
    )
    fig.update_xaxes(showgrid=False, linecolor="#e8edf4")
    fig.update_yaxes(gridcolor="#edf1f6", zeroline=False)
    return fig


def render_dashboard(frame: pd.DataFrame) -> None:
    total = len(frame)
    open_count = (
        int(frame["etat"].astype("string").str.upper().eq("OUVERT").sum())
        if "etat" in frame.columns
        else None
    )
    contact_count = (
        int(frame["telephone"].astype("string").str.strip().ne("").fillna(False).sum())
        if "telephone" in frame.columns
        else None
    )
    mapped_count = int(
        (numeric_series(frame, "latitude").between(-90, 90)
         & numeric_series(frame, "longitude").between(-180, 180)).sum()
    )

    metrics = st.columns(4)
    metrics[0].metric("Établissements", f"{total:,}".replace(",", " "))
    metrics[1].metric(
        "Établissements ouverts",
        f"{open_count:,}".replace(",", " ") if open_count is not None else "—",
    )
    metrics[2].metric(
        "Avec téléphone",
        f"{contact_count:,}".replace(",", " ") if contact_count is not None else "—",
    )
    metrics[3].metric("Géolocalisés", f"{mapped_count:,}".replace(",", " "))

    chart_left, chart_right = st.columns(2)
    with chart_left:
        if "type_etablissement" in frame.columns:
            types = (
                frame["type_etablissement"]
                .fillna("Non renseigné")
                .value_counts()
                .head(12)
                .rename_axis("Type")
                .reset_index(name="Nombre")
            )
            fig = px.bar(
                types.sort_values("Nombre"),
                x="Nombre",
                y="Type",
                orientation="h",
                color="Nombre",
                color_continuous_scale=["#bde6df", "#138b83"],
                title="Établissements par type",
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(plotly_layout(fig, 410), width="stretch")
        else:
            st.info("La colonne du type d’établissement est absente.")

    with chart_right:
        if "libelle_region" in frame.columns:
            regions = (
                frame["libelle_region"]
                .fillna("Non renseignée")
                .value_counts()
                .head(12)
                .rename_axis("Région")
                .reset_index(name="Nombre")
            )
            fig = px.bar(
                regions.sort_values("Nombre"),
                x="Nombre",
                y="Région",
                orientation="h",
                color="Nombre",
                color_continuous_scale=["#d9e8fb", "#3676c5"],
                title="Répartition par région",
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(plotly_layout(fig, 410), width="stretch")
        else:
            st.info("La colonne de région est absente.")

    chart_left, chart_right = st.columns(2)
    with chart_left:
        if "statut_public_prive" in frame.columns:
            status_counts = (
                frame["statut_public_prive"]
                .fillna("Non renseigné")
                .value_counts()
                .rename_axis("Statut")
                .reset_index(name="Nombre")
            )
            fig = px.pie(
                status_counts,
                names="Statut",
                values="Nombre",
                hole=0.62,
                title="Public / privé",
                color_discrete_sequence=["#168a83", "#4685c7", "#dce6f2"],
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(plotly_layout(fig, 350), width="stretch")
        else:
            st.info("La colonne du statut est absente.")

    with chart_right:
        service_columns = [
            ("restauration", "Restauration"),
            ("hebergement", "Hébergement"),
            ("apprentissage", "Apprentissage"),
            ("ulis", "ULIS"),
            ("post_bac", "Post-bac"),
            ("section_sport", "Section sport"),
            ("section_internationale", "Section internationale"),
        ]
        present_services = [(column, label) for column, label in service_columns if column in frame.columns]
        if present_services:
            service_counts = pd.DataFrame(
                {
                    "Service": [label for _, label in present_services],
                    "Nombre": [int(truthy_series(frame, column).sum()) for column, _ in present_services],
                }
            ).sort_values("Nombre")
            fig = px.bar(
                service_counts,
                x="Nombre",
                y="Service",
                orientation="h",
                color="Nombre",
                color_continuous_scale=["#f5dca9", "#dd8d2f"],
                title="Services et dispositifs",
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(plotly_layout(fig, 350), width="stretch")
        else:
            st.info("Aucune colonne de service n’est disponible dans cette source.")

    if "date_ouverture" in frame.columns:
        dates = pd.to_datetime(frame["date_ouverture"], errors="coerce")
        years = dates.dt.year.dropna().astype(int)
        if not years.empty:
            yearly = (
                years.value_counts()
                .sort_index()
                .rename_axis("Année")
                .reset_index(name="Ouvertures recensées")
            )
            fig = px.line(
                yearly,
                x="Année",
                y="Ouvertures recensées",
                markers=True,
                title="Années d’ouverture renseignées",
                color_discrete_sequence=["#6556b8"],
            )
            st.plotly_chart(plotly_layout(fig, 320), width="stretch")
            st.caption(
                "Cette courbe décrit les dates d’ouverture présentes dans le fichier, "
                "pas l’évolution annuelle du nombre d’établissements en activité."
            )

    if total == 0:
        st.info("Aucun établissement ne correspond aux filtres actuels.")


def render_directory(frame: pd.DataFrame) -> None:
    if frame.empty:
        st.info("Aucun résultat. Modifiez les filtres dans la barre latérale.")
        return

    page_count = math.ceil(len(frame) / PAGE_SIZE)
    page = st.number_input("Page", min_value=1, max_value=page_count, value=1, step=1)
    start = (int(page) - 1) * PAGE_SIZE
    page_frame = frame.iloc[start : start + PAGE_SIZE]
    st.caption(f"Résultats {start + 1:,} à {start + len(page_frame):,} sur {len(frame):,}".replace(",", " "))

    preferred_columns = [
        "identifiant_de_l_etablissement",
        "nom_etablissement",
        "type_etablissement",
        "statut_public_prive",
        "etat",
        "adresse_1",
        "code_postal",
        "nom_commune",
        "libelle_departement",
        "telephone",
        "web",
    ]
    visible_columns = [column for column in preferred_columns if column in page_frame.columns]
    column_config = (
        {"web": st.column_config.LinkColumn("Site web", display_text="Ouvrir ↗")}
        if "web" in page_frame.columns
        else None
    )
    st.dataframe(
        page_frame[visible_columns],
        width="stretch",
        hide_index=True,
        height=420,
        column_config=column_config,
    )

    def format_establishment(index: object) -> str:
        row = frame.loc[index]
        identifier = display_value(row.get("identifiant_de_l_etablissement"))
        name = display_value(row.get("nom_etablissement"))
        town = display_value(row.get("nom_commune"))
        return f"{name} · {town} · {identifier}"

    selected_index = st.selectbox(
        "Consulter la fiche complète",
        page_frame.index.tolist(),
        format_func=format_establishment,
    )
    selected = frame.loc[selected_index]
    st.subheader(display_value(selected.get("nom_etablissement")))
    address_parts = [
        display_value(selected.get(column))
        for column in ("adresse_1", "code_postal", "nom_commune")
        if column in frame.columns and display_value(selected.get(column)) != "Non renseigné"
    ]
    if address_parts:
        st.caption(" · ".join(address_parts))

    link_columns = (
        ("web", "Site de l’établissement"),
        ("fiche_onisep", "Fiche Onisep"),
    )
    links = [
        (label, display_value(selected.get(column)))
        for column, label in link_columns
        if column in frame.columns
        and display_value(selected.get(column)).startswith(("https://", "http://"))
    ]
    if links:
        link_cols = st.columns(min(len(links), 2))
        for column, (label, url) in zip(link_cols, links):
            column.link_button(label, url)

    details = pd.DataFrame(
        {
            "Information": frame.columns,
            "Valeur": [display_value(selected[column]) for column in frame.columns],
        }
    )
    st.dataframe(details, width="stretch", hide_index=True, height=520)


def render_map(frame: pd.DataFrame) -> None:
    if "latitude" not in frame.columns or "longitude" not in frame.columns:
        st.info("Cette source ne contient pas de coordonnées de latitude et longitude.")
        return
    mapped = frame.copy()
    mapped["latitude"] = numeric_series(mapped, "latitude")
    mapped["longitude"] = numeric_series(mapped, "longitude")
    mapped = mapped[
        mapped["latitude"].between(-90, 90) & mapped["longitude"].between(-180, 180)
    ]
    if mapped.empty:
        st.info("Aucun établissement géolocalisé ne correspond aux filtres.")
        return
    st.caption(f"{len(mapped):,} établissement(s) avec coordonnées valides.".replace(",", " "))
    if len(mapped) > MAX_MAP_POINTS:
        st.caption(
            f"La carte affiche un échantillon de {MAX_MAP_POINTS:,} points pour rester fluide.".replace(",", " ")
        )
        mapped = mapped.sample(MAX_MAP_POINTS, random_state=42)
    st.map(mapped[["latitude", "longitude"]], latitude="latitude", longitude="longitude", size=8)


st.markdown(
    """
    <div class="hero">
      <h1>Annuaire des établissements scolaires</h1>
      <p>Explorez, filtrez et comprenez les établissements en un seul endroit.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = None
with st.sidebar:
    st.markdown("## Votre espace d’exploration")
    st.caption("Tous les indicateurs et graphiques suivent les filtres choisis.")
    if DEFAULT_CSV.is_file():
        st.success(f"Source connectée : {DEFAULT_CSV.name}")
    else:
        st.warning("Le fichier annuaire par défaut est introuvable.")
    uploaded_file = st.file_uploader("Charger un autre fichier CSV", type=["csv"])

try:
    if uploaded_file is not None:
        source_frame = load_uploaded_file(uploaded_file.getvalue())
        source_label = uploaded_file.name
    elif DEFAULT_CSV.is_file():
        stat = DEFAULT_CSV.stat()
        source_frame = load_local_file(str(DEFAULT_CSV), stat.st_mtime_ns, stat.st_size)
        source_label = DEFAULT_CSV.name
    else:
        st.info(
            "Pour commencer, placez `annuaire_complet.csv` dans le dossier Downloads "
            "ou chargez un fichier CSV compatible dans la barre latérale."
        )
        st.stop()
except ValueError as error:
    st.error(str(error))
    st.stop()

with st.sidebar:
    st.divider()
    st.markdown("### Filtres")
    search = st.text_input("Recherche rapide", placeholder="Nom, identifiant, adresse…")
    regions = st.multiselect("Région", available_values(source_frame, "libelle_region"))
    departments_available = source_frame
    if regions and "libelle_region" in source_frame.columns:
        departments_available = source_frame[
            source_frame["libelle_region"].astype("string").isin(regions)
        ]
    departments = st.multiselect(
        "Département",
        available_values(departments_available, "libelle_departement"),
    )
    establishment_types = st.multiselect(
        "Type d’établissement",
        available_values(source_frame, "type_etablissement"),
    )
    statuses = st.multiselect(
        "Statut",
        available_values(source_frame, "statut_public_prive"),
    )
    states = st.multiselect("État", available_values(source_frame, "etat"))
    commune = st.text_input("Commune", placeholder="Ex. Lyon")

    service_labels = {
        "restauration": "Restauration",
        "hebergement": "Hébergement",
        "apprentissage": "Apprentissage",
        "ulis": "ULIS",
        "segpa": "SEGPA",
        "post_bac": "Post-bac",
        "section_sport": "Section sport",
        "section_internationale": "Section internationale",
    }
    present_services = [
        (column, label)
        for column, label in service_labels.items()
        if column in source_frame.columns
    ]
    selected_service_labels = st.multiselect(
        "Services et dispositifs",
        [label for _, label in present_services],
    )
    services = [
        (column, label)
        for column, label in present_services
        if label in selected_service_labels
    ]

filtered = filter_annuaire(
    source_frame,
    search,
    regions,
    departments,
    establishment_types,
    statuses,
    states,
    commune,
    services,
)

st.caption(
    f"Source : {source_label} · {len(source_frame):,} établissements au total".replace(",", " ")
)
dashboard_tab, directory_tab, map_tab = st.tabs(
    ["📊 Tableau de bord", "🔎 Annuaire", "🗺️ Carte"]
)
with dashboard_tab:
    render_dashboard(filtered)
with directory_tab:
    st.subheader("Les établissements")
    st.caption("Parcourez les résultats filtrés et ouvrez une fiche pour consulter tous les champs.")
    render_directory(filtered)
    if not filtered.empty:
        st.download_button(
            "Télécharger les résultats filtrés (CSV)",
            data=filtered.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig"),
            file_name="etablissements_filtres.csv",
            mime="text/csv",
        )
with map_tab:
    st.subheader("Carte des établissements")
    render_map(filtered)
