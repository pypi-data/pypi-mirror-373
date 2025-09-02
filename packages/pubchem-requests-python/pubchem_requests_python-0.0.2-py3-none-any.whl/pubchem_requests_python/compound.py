import time
import requests
import logging
import stdnum.casrn as casrn
import collections
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

from pubchem_requests_python.individual_property_requests import (
    name_to_cid,
    cas_to_cid,
    is_valid_cas,
)


def get_cid(name: str | None = None, cas: str | None = None) -> str | None:
    if cas:
        return cas_to_cid(cas)
    elif name:
        return name_to_cid(name)
    return None


class Compound:
    def __init__(
        self, name: str | None = None, cas: str | None = None, cid: str | None = None
    ):
        self.found_compound = True
        cid = cid if cid else get_cid(name=name, cas=cas)
        if cid == None:
            logger.error(f"Could not retrieve CID for {name or cas}.")
            self.found_compound = False
        self.name = name
        self.cas = cas
        self.cid = cid

        pug_view_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{self.cid}/JSON"
        pug_url = (
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{self.cid}/JSON"
        )

        self.pug_view_response = None
        self.pug_response = None
        with ThreadPoolExecutor(max_workers=2) as executor:
            pug_view_future = executor.submit(requests.get, pug_view_url)
            pug_future = executor.submit(requests.get, pug_url)
            self.pug_view_response = pug_view_future.result()
            self.pug_response = pug_future.result()

        if not self.pug_view_response or self.pug_view_response.status_code != 200:
            logger.error(f"Failed to retrieve compound information for CID {self.cid}.")
            self.found_compound = False

        if not self.pug_response or self.pug_response.status_code != 200:
            logger.error(f"Failed to retrieve compound information for CID {self.cid}.")
            self.found_compound = False

    def _get_view_items(
        self, data
    ) -> tuple[list[str] | None, list[str] | None, list[str] | None, list[str] | None]:
        sections = data.get("Record", {}).get("Section", [])

        cas_numbers = list[str]()
        descriptions = list[str]()
        summaries = list[str]()
        synonyms = list[str]()
        for section in sections:
            heading = section.get("TOCHeading", "")
            if heading == "Names and Identifiers":
                for subsection in section.get("Section", []):
                    heading = subsection.get("TOCHeading", "")
                    if heading == "Record Description":
                        for info in subsection.get("Information", []):
                            for item in info.get("Value", {}).get(
                                "StringWithMarkup", []
                            ):
                                descriptions.append(item.get("String", ""))
                    elif heading == "Other Identifiers" and not self.cas:
                        for subsubsection in subsection.get("Section", []):
                            if subsubsection.get("TOCHeading", "") == "CAS":
                                for info in subsubsection.get("Information", []):
                                    for item in info["Value"]["StringWithMarkup"]:
                                        cas = item["String"]
                                        if is_valid_cas(cas):
                                            cas_numbers.append(cas)
                                    break
                    elif heading == "Synonyms":
                        for subsubsection in subsection.get("Section", []):
                            if (
                                subsubsection.get("TOCHeading", "")
                                == "Depositor-Supplied Synonyms"
                            ):
                                for info in subsubsection.get("Information", []):
                                    for item in info.get("Value", {}).get(
                                        "StringWithMarkup", []
                                    ):
                                        name = item.get("String", "")
                                        if not is_valid_cas(name):
                                            synonyms.append(name)
            elif heading == "Safety and Hazards":
                for subsection in section.get("Section", []):
                    if subsection.get("TOCHeading") == "Hazards Identification":
                        for subsubsection in subsection.get("Section", []):
                            if subsubsection.get("TOCHeading") == "Hazards Summary":
                                summaries = list[str]()
                                for info in subsubsection.get("Information", []):
                                    for item in info.get("Value", {}).get(
                                        "StringWithMarkup", []
                                    ):
                                        summaries.append(item.get("String", ""))
                            elif subsubsection.get("TOCHeading") == "Health Hazards":
                                for info in subsubsection.get("Information", []):
                                    for item in info.get("Value", {}).get(
                                        "StringWithMarkup", []
                                    ):
                                        summaries.append(item.get("String", ""))

        return synonyms, cas_numbers, descriptions, summaries

    def _get_rest_items(self, data) -> tuple[str | None, float | None, float | None]:
        props = data.get("PC_Compounds", [{}])[0].get("props", [])

        molecular_formula = None
        molecular_weight = None
        molar_mass = None
        for prop in props:
            label = prop.get("urn", {}).get("label", "")
            if label == "Molecular Formula":
                molecular_formula = prop.get("value", {}).get("sval", "")
            elif label == "Molecular Weight":
                try:
                    molecular_weight = float(prop.get("value", {}).get("sval", None))
                except Exception as e:
                    logger.error(f"Could not convert molecular weight to float: {e}")
                    molecular_weight = None
            elif label == "Mass":
                if prop.get("urn", {}).get("name", "") == "Exact":
                    try:
                        molar_mass = float(prop.get("value", {}).get("sval", None))
                    except Exception as e:
                        logger.error(f"Could not convert molar mass to float: {e}")
                        molar_mass = None

        return molecular_formula, molecular_weight, molar_mass

    def _init_compound(self):
        view_data = self.pug_view_response.json()  # type: ignore - The pug_view_response must be valid at this point
        rest_data = self.pug_response.json()  # type: ignore - The pug_response must be valid at this point

        with ThreadPoolExecutor(max_workers=2) as executor:
            view_future = executor.submit(self._get_view_items, view_data)
            rest_future = executor.submit(self._get_rest_items, rest_data)

            synonyms, cas_numbers, descriptions, summaries = view_future.result()
            molecular_formula, molecular_weight, molar_mass = rest_future.result()

        if synonyms:
            self.synonyms = synonyms
            if not self.name:
                self.name = self.synonyms[0]
        else:
            logger.error(f"No synonyms found for CID {self.cid}")
            self.synonyms = None

        if cas_numbers and not self.cas:
            cas_counter = collections.Counter(cas_numbers)
            self.cas, _ = cas_counter.most_common(1)[0]
        elif not self.cas:
            logger.error(f"No CAS numbers found for CID {self.cid}")
            self.cas = None

        if descriptions:
            self.descriptions = descriptions
        else:
            logger.error(f"No descriptionss found for CID {self.cid}")
            self.descriptions = None

        if molecular_formula:
            self.molecular_formula = molecular_formula
        else:
            logger.error(f"No molecular formula found for CID {self.cid}")
            self.molecular_formula = None

        if molecular_weight:
            self.molecular_weight = molecular_weight
        else:
            logger.error(f"No molecular weight found for CID {self.cid}")
            self.molecular_weight = None

        if molar_mass:
            self.molar_mass = molar_mass
        else:
            logger.error(f"No molar mass found for CID {self.cid}")
            self.molar_mass = None

        if summaries:
            self.safety_data = summaries
        else:
            logger.error(f"No safety data found for CID {self.cid}")
            self.safety_data = None

        return True

    # get functions
    def get_synonyms(self) -> list[str] | None:
        return self.synonyms

    def get_name(self) -> str | None:
        return self.name

    def get_cas(self) -> str | None:
        return self.cas

    def get_descriptions(self) -> list[str] | None:
        return self.descriptions

    def get_molecular_formula(self) -> str | None:
        return self.molecular_formula

    def get_molecular_weight(self) -> float | None:
        return self.molecular_weight

    def get_molar_mass(self) -> float | None:
        return self.molar_mass

    def get_safety_data(self) -> list[str] | None:
        return self.safety_data

    # Compound class as dict
    def dict(self) -> dict:
        return {
            "name": self.name,
            "cas": self.cas,
            "cid": self.cid,
            "synonyms": self.synonyms,
            "descriptions": self.descriptions,
            "molecular_formula": self.molecular_formula,
            "molecular_weight": self.molecular_weight,
            "molar_mass": self.molar_mass,
            "safety_data": self.safety_data,
        }


def compound_from_name(name: str) -> Compound | None:
    """
    Fetch a compound from its name.

    Args:
        name (str): The name of the compound.

    Returns:
        Compound | None: The compound object or None if not found.
    """
    compound = Compound(name=name)
    if not compound.found_compound:
        logger.error(f"Could not find compound for name {name}.")
        return None
    compound._init_compound()
    return compound


def compound_from_CAS(CAS: str) -> Compound | None:
    """
    Fetch a compound from its CAS number.

    Args:
        CAS (str): The CAS number of the compound.

    Returns:
        Compound | None: The compound object or None if not found.
    """
    compound = Compound(cas=CAS)
    if not compound.found_compound:
        logger.error(f"Could not find compound for CAS {CAS}.")
        return None
    compound._init_compound()
    return compound


def compound_from_CID(CID: str) -> Compound | None:
    """
    Fetch a compound from its CID.

    Args:
        CID (str): The CID of the compound.

    Returns:
        Compound | None: The compound object or None if not found.
    """
    compound = Compound(cid=CID)
    if not compound.found_compound:
        logger.error(f"Could not find compound for CID {CID}.")
        return None
    compound._init_compound()
    return compound
