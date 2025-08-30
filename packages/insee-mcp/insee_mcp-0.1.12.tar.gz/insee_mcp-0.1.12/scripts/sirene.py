from pynsee import search_sirene
import unicodedata
import pandas as pd
from rapidfuzz import process



def normalize(text: str) -> str:
    """Supprime accents et met en uppercase pour comparaison stricte."""
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    return text.upper().strip()

def search_sirene_company(
    company_name: str = None,
    siren: str = None,
    siret: str = None,
    fuzzy: bool = True
):
    """
    Recherche une entreprise dans la base SIRENE selon SIREN, SIRET ou nom.

    Args:
        company_name (str, optional): Nom de l'entreprise.
        siren (str, optional): Code SIREN.
        siret (str, optional): Code SIRET.
        fuzzy (bool): Active la recherche approximative si nom partiel.

    Returns:
        dict: Informations clés sur l'entreprise.
    """

    df = pd.DataFrame()

    # 1. Direct lookup by SIRET
    if siret:
        df = search_sirene(variable="siret", pattern=siret, number=1)

    # 2. Direct lookup by SIREN (multiple establishments possible)
    elif siren:
        df = search_sirene(variable="siren", pattern=siren, number=1000)

    # 3. Direct lookup by company name
    elif company_name:
        # Essai dans plusieurs champs (nom officiel, sigle, usuel…)
        candidates = []
        for var in [
            "denominationUniteLegale",
            "denominationUsuelle1UniteLegale",
            "sigleUniteLegale",
            "enseigne1Etablissement",
        ]:
            try:
                res = search_sirene(variable=var, pattern=company_name, number=1000)
                if not res.empty:
                    candidates.append(res)
            except Exception:
                pass
        if candidates:
            df = pd.concat(candidates).drop_duplicates()

        # 🔹 Optionnel : fuzzy matching if no exact matching
        if fuzzy and not df.empty:
            names = df["denominationUniteLegale"].fillna("").tolist()
            best_match = process.extractOne(company_name, names, score_cutoff=100)
            if best_match:
                idx = names.index(best_match[0])
                df = df.iloc[[idx]]

    if df.empty:
        return {"error": "Aucune entreprise trouvée avec les critères fournis."}

    # We take the first match if multiple
    row = df.iloc[0]

    result = {
        "siren": row.get("siren"),
        "siret": row.get("siret"),
        "denomination": row.get("denominationUniteLegale"),
        "sigle": row.get("sigleUniteLegale"),
        "forme_juridique": row.get("categorieJuridiqueUniteLegale"),
        "date_creation": row.get("dateCreationUniteLegale"),
        "adresse": row.get("libelleVoieEtablissement"),
        "code_postal": row.get("codePostalEtablissement"),
        "commune": row.get("libelleCommuneEtablissement"),
        "pays": row.get("libellePaysEtrangerEtablissement"),
        "code_ape": row.get("activitePrincipaleUniteLegale"),
        "libelle_ape": row.get("activitePrincipaleUniteLegaleLibelle"),
        "tranche_effectifs": row.get("trancheEffectifsUniteLegale"),
        "effectifs_min": float(row.get("effectifsMinUniteLegale")) if row.get("effectifsMinUniteLegale") else "Pas d'information",
        "effectifs_max": float(row.get("effectifsMaxUniteLegale")) if row.get("effectifsMaxUniteLegale") else "Pas d'information",
        "etat_unite_legale": row.get("etatAdministratifUniteLegale"),
        "etat_etablissement": row.get("etatAdministratifEtablissement"),
        "ess": row.get("economieSocialeSolidaireUniteLegale"),
        "societe_mission": row.get("societeMissionUniteLegale"),
    }

    return result