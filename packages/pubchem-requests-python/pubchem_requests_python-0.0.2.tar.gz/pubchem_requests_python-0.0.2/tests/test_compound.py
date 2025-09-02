import pytest
import logging

logging.basicConfig(level=logging.INFO)
from pubchem_requests_python import (
    compound_from_name,
    compound_from_CAS,
    compound_from_CID,
)

name_cas_cid = [
    ["Formaldehyde", "30525-89-4", "712"],
    ["Acetone", "67-64-1", "180"],
    ["Benzene", "71-43-2", "241"],
    ["Ethanol", "64-17-5", "702"],
    ["Water", "7732-18-5", "962"],
]


@pytest.mark.parametrize("name, cas, cid", name_cas_cid)
def test_compound_from_cid(name, cas, cid):
    """Test fetching compound data by name, CAS number, and CID."""
    compound = compound_from_CID(cid)

    assert compound is not None
    assert compound.cid == cid
    assert compound.cas == cas
    assert name.lower() in [s.lower() for s in compound.synonyms or []]

    comp_dict = compound.dict()
    for key, value in comp_dict.items():
        assert value is not None, f"Value for {key} is None"


@pytest.mark.parametrize("name, cas, cid", name_cas_cid)
def test_compound_from_cas(name, cas, cid):
    """Test fetching compound data by name, CAS number, and CID."""
    compound = compound_from_CAS(cas)

    assert compound is not None
    assert compound.cid == cid
    assert compound.cas == cas
    assert name.lower() in [s.lower() for s in compound.synonyms or []]

    comp_dict = compound.dict()
    for key, value in comp_dict.items():
        assert value is not None, f"Value for {key} is None"


@pytest.mark.parametrize("name, cas, cid", name_cas_cid)
def test_compound_from_name(name, cas, cid):
    """Test fetching compound data by name, CAS number, and CID."""
    compound = compound_from_name(name)

    assert compound is not None
    assert compound.cid == cid
    assert compound.cas == cas
    assert name.lower() in [s.lower() for s in compound.synonyms or []]

    comp_dict = compound.dict()
    for key, value in comp_dict.items():
        assert value is not None, f"Value for {key} is None"
