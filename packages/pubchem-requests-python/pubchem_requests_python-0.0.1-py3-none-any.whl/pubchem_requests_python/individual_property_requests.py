import requests

import logging
import stdnum.casrn as casrn

import collections

logger = logging.getLogger(__name__)

# Note: only functions with CIDs have logging, the other functions simply wrap requests


# helpers
def is_valid_cas(cas_number: str) -> bool:
    """Check if a CAS number is valid."""
    return casrn.is_valid(cas_number)


# identifier to CID
def cas_to_cid(cas_number: str) -> str | None:
    """Get the PubChem Compound ID (CID) from a CAS number."""
    logger.info(f"Fetching CID for CAS {cas_number}")
    if not is_valid_cas(cas_number):
        return None
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas_number}/cids/JSON"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return str(data["IdentifierList"]["CID"][0])
    except requests.RequestException as e:
        logger.error(f"Error fetching CID from PubChem for CAS {cas_number}: {e}")
        return None


def name_to_cid(compound_name: str) -> str | None:
    """Get the PubChem Compound ID (CID) from a compound name."""
    logger.info(f"Fetching CID for compound name: {compound_name}")

    # remove common solvents from name
    compound_name = compound_name.replace("HCl-H2O", "").replace("H2O", "")
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound_name}/cids/JSON"
    try:
        response = requests.get(url)
        if response.status_code == 404:
            logger.warning(f"No pubchem compound found for name: {compound_name}")
            return None
        response.raise_for_status()
        data = response.json()
        return str(data["IdentifierList"]["CID"][0])
    except requests.RequestException as e:
        logger.error(f"Error fetching CID for compound {compound_name}: {e}")
        return None


# CID to identifier
def cid_to_cas(cid: str) -> str | None:
    """Get the CAS number from a PubChem Compound ID (CID)."""
    logger.info(f"Fetching CAS for CID {cid}")

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/?heading=CAS"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        cas_numbers = list[str]()
        sections = data["Record"]["Section"]
        for section in sections:
            if section.get("TOCHeading", "") == "Names and Identifiers":
                for subsection in section.get("Section", []):
                    if subsection.get("TOCHeading", "") == "Other Identifiers":
                        for subsubsection in subsection.get("Section", []):
                            if subsubsection.get("TOCHeading", "") == "CAS":
                                for info in subsubsection.get("Information", []):
                                    for item in info["Value"]["StringWithMarkup"]:
                                        cas = item["String"]
                                        if is_valid_cas(cas):
                                            cas_numbers.append(cas)
                                    break
        if not cas_numbers:
            logger.error(f"No valid CAS numbers found for CID {cid}")
            return None
        cas_counter = collections.Counter(cas_numbers)
        most_common_cas, _ = cas_counter.most_common(1)[0]
        return most_common_cas

    except Exception as e:
        logger.error(f"Error fetching CAS from PubChem for CID {cid}: {e}")
        return None


def cid_to_name(cid: str) -> str | None:
    """Get the compound name from a PubChem Compound ID (CID). Returns first synonym."""
    logger.info(f"Fetching name for CID {cid}")

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        synonyms = data["InformationList"]["Information"][0]["Synonym"]
        synonyms = [s for s in synonyms if not is_valid_cas(s)]
        return synonyms[0] if synonyms else None
    except requests.RequestException as e:
        logger.error(f"Error fetching name from PubChem for CID {cid}: {e}")
        return None


def cid_to_names(cid: str) -> list[str] | None:
    """Get the compound names from a PubChem Compound ID (CID). Returns all synonyms."""
    logger.info(f"Fetching names for CID {cid}")

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        synonyms = data["InformationList"]["Information"][0]["Synonym"]
        synonyms = [s for s in synonyms if not is_valid_cas(s)]
        return synonyms if synonyms else None
    except requests.RequestException as e:
        logger.error(f"Error fetching names from PubChem for CID {cid}: {e}")
        return None


# identifier to identifier
def name_to_cas(compound_name: str) -> str | None:
    """Convert compound name to CAS number."""
    cid = name_to_cid(compound_name)
    if cid:
        return cid_to_cas(cid)
    return None


def cas_to_name(cas_number: str) -> str | None:
    """Convert CAS number to compound name."""
    cid = cas_to_cid(cas_number)
    if cid:
        return cid_to_name(cid)
    return None


def cas_to_names(cas_number: str) -> list[str] | None:
    """Convert CAS number to compound names."""
    cid = cas_to_cid(cas_number)
    if cid:
        return cid_to_names(cid)
    return None


#  identifier to compound info
def cid_to_molecular_weight(cid: str) -> float | None:
    """Get the molecular weight of a compound from its CID."""
    logger.info(f"Fetching molecular weight for CID {cid}")

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularWeight/JSON"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return float(
            data.get("PropertyTable", {})
            .get("Properties", [{}])[0]
            .get("MolecularWeight", None)
        )

    except requests.RequestException as e:
        logger.error(f"Error fetching molecular weight for cid {cid}: {e}")
        return None


def name_to_molecular_weight(compound_name: str) -> float | None:
    """Get the molecular weight of a compound from its name."""
    cid = name_to_cid(compound_name)
    if cid:
        return cid_to_molecular_weight(cid)
    return None


def cas_to_molecular_weight(cas_number: str) -> float | None:
    """Get the molecular weight of a compound from its CAS number."""
    cid = cas_to_cid(cas_number)
    if cid:
        return cid_to_molecular_weight(cid)
    return None


def cid_to_safety_data(cid: str) -> list[str] | None:
    """Get a compounds safety data from its CID."""
    logger.info(f"Fetching safety data for CID {cid}")
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON/?heading=Hazards%20Summary"
        response = requests.get(url)
        if response.status_code != 200:
            logger.info("Failed to fetch compound data.")
            return []

        data = response.json()
        sections = data.get("Record", {}).get("Section", [])

        # Step 1: Locate "Safety and Hazards"
        safety_section = None
        for s in sections:
            if s.get("TOCHeading") == "Safety and Hazards":
                safety_section = s.get("Section", [])
        if not safety_section:
            return []

        # Step 2: Locate "Hazards Identification" inside it
        hazards_id_section = None
        for s in safety_section:
            if s.get("TOCHeading") == "Hazards Identification":
                hazards_id_section = s.get("Section", [])
        if not hazards_id_section:
            return []

        # Step 3: Locate "Hazards Summary" inside that
        summary = list[str]()
        for s in hazards_id_section:
            if s.get("TOCHeading") == "Hazards Summary":
                for info in s.get("Information", []):
                    for item in info.get("Value", {}).get("StringWithMarkup", []):
                        summary.append(item.get("String", ""))

        return summary
    except Exception as e:
        logger.error(f"Error fetching safety data for CID {cid}: {e}")
        return []


def name_to_safety_data(name: str) -> list[str] | None:
    """Get a compound's safety data from its name."""
    cid = name_to_cid(name)
    if cid:
        return cid_to_safety_data(cid)
    return None


def cas_to_safety_data(cas_number: str) -> list[str] | None:
    """Get a compound's safety data from its CAS number."""
    cid = cas_to_cid(cas_number)
    if cid:
        return cid_to_safety_data(cid)
    return None


def cid_to_molecular_formula(cid: str) -> str | None:
    """Get a compound's molecular formula from its CID."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularFormula/JSON"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return (
            data.get("PropertyTable", {})
            .get("Properties", [{}])[0]
            .get("MolecularFormula", None)
        )
    except requests.RequestException as e:
        logger.error(f"Error fetching molecular formula for CID {cid}: {e}")
        return None


def name_to_molecular_formula(name: str) -> str | None:
    """Get a compound's molecular formula from its name."""
    cid = name_to_cid(name)
    if cid:
        return cid_to_molecular_formula(cid)
    return None


def cas_to_molecular_formula(cas_number: str) -> str | None:
    """Get a compound's molecular formula from its CAS number."""
    cid = cas_to_cid(cas_number)
    if cid:
        return cid_to_molecular_formula(cid)
    return None
