import pytest
from pubchem_requests_python import individual_property_requests as icr

# Test data
NAME_CAS = {
    "Water": "7732-18-5",
    "Sodium Chloride": "7647-14-5",
    "Ethanol": "64-17-5",
    "Sodium Bicarbonate": "144-55-8",
    "Hydrochloric Acid": "7647-01-0",
    "Calcium Chloride": "10043-52-4",
    "Acetic Acid": "64-19-7",
    "Sucrose": "57-50-1",
    "Silver Nitrate": "7761-88-8",
    "Potassium Chloride": "7447-40-7",
}

MADE_UP_NAMES = {
    "made up name 1": "12345-67-8",
    "made up name 2": "23456-78-9",
    "made up name 3": "34567-89-0",
}

CIDS = {"aspirin": "2244", "caffeine": "2519", "glucose": "5793", "ethanol": "702"}


@pytest.mark.parametrize("name, cas", list(NAME_CAS.items()))
def test_name_to_cas(name, cas):
    """Test converting a compound name to a CAS number."""
    assert icr.name_to_cas(name) == cas


@pytest.mark.parametrize("name, cas", list(NAME_CAS.items()))
def test_cas_to_name(name, cas):
    """Test converting a CAS number to a compound name."""
    # Exact name match isn't always guaranteed, so we check if the expected name is in the list of synonyms
    synonyms = icr.cas_to_names(cas)
    assert synonyms is not None
    assert name.lower() in [s.lower() for s in synonyms]


@pytest.mark.parametrize("cas", list(NAME_CAS.values()))
def test_cas_to_names(cas):
    """Test converting a CAS number to a list of compound names."""
    names = icr.cas_to_names(cas)
    assert isinstance(names, list)
    assert all(isinstance(item, str) for item in names)


@pytest.mark.parametrize("name", list(NAME_CAS.keys()))
def test_name_to_molecular_weight(name):
    """Test fetching the molecular weight of a compound by name."""
    weight = icr.name_to_molecular_weight(name)
    assert isinstance(weight, float)
    assert weight > 0


@pytest.mark.parametrize("cas", list(NAME_CAS.values()))
def test_cas_to_molecular_weight(cas):
    """Test fetching the molecular weight of a compound by CAS number."""
    weight = icr.cas_to_molecular_weight(cas)
    assert isinstance(weight, float)
    assert weight > 0


@pytest.mark.parametrize("name", list(NAME_CAS.keys()))
def test_name_to_molecular_formula(name):
    """Test fetching the molecular formula of a compound by name."""
    formula = icr.name_to_molecular_formula(name)
    assert isinstance(formula, str)
    assert len(formula) > 0


@pytest.mark.parametrize("cas", list(NAME_CAS.values()))
def test_cas_to_molecular_formula(cas):
    """Test fetching the molecular formula of a compound by CAS number."""
    formula = icr.cas_to_molecular_formula(cas)
    assert isinstance(formula, str)
    assert len(formula) > 0


@pytest.mark.parametrize("name", list(NAME_CAS.keys()))
def test_name_to_safety_data(name):
    """Test fetching safety data for a compound by name."""
    safety_data = icr.name_to_safety_data(name)
    assert isinstance(safety_data, list)
    # Not all compounds have safety data, but if they do, it should be a list of strings
    if safety_data:
        assert all(isinstance(item, str) and len(item) > 0 for item in safety_data)


@pytest.mark.parametrize("cas", list(NAME_CAS.values()))
def test_cas_to_safety_data(cas):
    """Test fetching safety data for a compound by CAS number."""
    safety_data = icr.cas_to_safety_data(cas)
    assert isinstance(safety_data, list)
    # Not all compounds have safety data, but if they do, it should be a list of strings
    if safety_data:
        assert all(isinstance(item, str) and len(item) > 0 for item in safety_data)


# --- Negative Tests ---


@pytest.mark.parametrize("name", list(MADE_UP_NAMES.keys()))
def test_invalid_name_to_cas(name):
    """Test converting an invalid compound name to a CAS number."""
    assert icr.name_to_cas(name) is None


@pytest.mark.parametrize("cas", list(MADE_UP_NAMES.values()))
def test_invalid_cas_to_name(cas):
    """Test converting an invalid CAS number to a compound name."""
    assert icr.cas_to_name(cas) is None


@pytest.mark.parametrize("name", list(MADE_UP_NAMES.keys()))
def test_invalid_name_to_molecular_weight(name):
    """Test fetching molecular weight for an invalid compound name."""
    assert icr.name_to_molecular_weight(name) is None


@pytest.mark.parametrize("cas", list(MADE_UP_NAMES.values()))
def test_invalid_cas_to_safety_data(cas):
    """Test fetching safety data for an invalid CAS number."""
    safety_data = icr.cas_to_safety_data(cas)
    assert safety_data == [] or safety_data is None


# --- CID-based function tests ---


@pytest.mark.parametrize("name, cid", list(CIDS.items()))
def test_name_to_cid(name, cid):
    """Test converting a compound name to a CID."""
    assert icr.name_to_cid(name) == cid


@pytest.mark.parametrize("cid", list(CIDS.values()))
def test_cid_to_name(cid):
    """Test converting a CID to a compound name."""
    name = icr.cid_to_name(cid)
    assert isinstance(name, str)
    assert len(name) > 0


@pytest.mark.parametrize("cid", list(CIDS.values()))
def test_cid_to_molecular_weight(cid):
    """Test fetching molecular weight by CID."""
    weight = icr.cid_to_molecular_weight(cid)
    assert isinstance(weight, float)
    assert weight > 0


@pytest.mark.parametrize("cid", list(CIDS.values()))
def test_cid_to_molecular_formula(cid):
    """Test fetching molecular formula by CID."""
    formula = icr.cid_to_molecular_formula(cid)
    assert isinstance(formula, str)
    assert len(formula) > 0


@pytest.mark.parametrize("cid", list(CIDS.values()))
def test_cid_to_safety_data(cid):
    """Test fetching safety data by CID."""
    safety_data = icr.cid_to_safety_data(cid)
    assert isinstance(safety_data, list)
    if safety_data:
        assert all(isinstance(item, str) and len(item) > 0 for item in safety_data)