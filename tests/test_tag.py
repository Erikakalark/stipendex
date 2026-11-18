import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
from tag import tag  # noqa: E402


def mk(andamal, co="", namn="Testfond", ort="Uppsala"):
    return {"id": "1", "namn": namn, "orgnr": "802000-0000", "co": co, "adr": "Box 1", "postnr": "751 05", "ort": ort,
            "tel": "018-1", "typ": 6, "lan": 3, "kom": 380, "andamal": andamal}


def test_nation_and_subject():
    r = tag(mk("Till behövande medicine studerande av Västmanland-Dala nation.", co="Uppsala Akademiförvaltning"))
    assert r["kat"] == "stipendium"
    assert "Västmanlands-Dala nation" in r["nationer"]
    assert "medicin" in r["amnen"] and "behov" in r["flaggor"] and r["route"] == "UU"


def test_lund_skanska():
    r = tag(mk("Stipendium till studerande av Skånska nationen vid Lunds universitet.", ort="Lund"))
    assert "Lunds nation" in r["nationer"] and r["route"] == "direkt" and "LU" in r["unis"]


def test_research_only_not_individual_aid():
    r = tag(mk("Att främja Svenska Institutet genom att utgöra ett bibliotek och arkiv."))
    assert r["kat"] == "ej_individ"


def test_aid():
    r = tag(mk("Att lämna bidrag till behövande äldre personer i Uppsala kommun."))
    assert r["kat"] == "bidrag" and "äldre" in r["malgrupp"]


def test_private_person_contact_hidden():
    r = tag(mk("Till studerande.", co="Anna Andersson"))
    assert r["kontakt"] == {"co": "", "adress": "", "telefon": ""}


def test_origin_not_from_university_name():
    r = tag(mk("Till studerande vid Uppsala universitet."))
    assert "Uppsala" not in r["orter"]
    r = tag(mk("Till studerande född i Uppsala."))
    assert "Uppsala" in r["orter"]


def test_no_personal_data_fields():
    """Taggad data får aldrig innehålla styrelse/roller."""
    r = tag(mk("Till studerande."))
    assert not any(k.lower() in ("roller", "roles", "styrelse") for k in r)
    out = ROOT / "data" / "stiftelser.json"
    if out.exists():
        text = out.read_text(encoding="utf-8")
        assert "ROLLER" not in text and "FODELSEDATUM" not in text.upper()
