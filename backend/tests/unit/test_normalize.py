import datetime

from cid.pipeline.normalize.addresses import address_key
from cid.pipeline.normalize.dates import to_utc
from cid.pipeline.normalize.names import normalize_name
from cid.pipeline.normalize.offences import normalize_offence
from cid.pipeline.normalize.phones import normalize_msisdn


def test_phone_variants_of_same_number_agree():
    forms = ["+91 98200 11234", "09820011234", "9820011234", "+91-98200-11234"]
    normalized = {normalize_msisdn(f) for f in forms}
    assert normalized == {"+919820011234"}


def test_phone_junk_returns_none():
    assert normalize_msisdn("12345") is None
    assert normalize_msisdn("not a phone") is None
    assert normalize_msisdn("+1 5551234567") is None


def test_offence_mixed_ipc_bns_sample_maps_correctly():
    assert normalize_offence("IPC", "420") == {
        "code_system": "IPC",
        "section": "420",
        "ontology_id": "cheating",
    }
    assert normalize_offence("BNS", "303") == {
        "code_system": "BNS",
        "section": "303",
        "ontology_id": "theft",
    }


def test_offence_ipc_and_bns_equivalent_share_ontology_id():
    ipc = normalize_offence("IPC", "379")
    bns = normalize_offence("BNS", "303")
    assert ipc["ontology_id"] == bns["ontology_id"]


def test_date_kolkata_02_00_is_previous_day_in_utc():
    # 02:00 IST (UTC+05:30) on the 10th is 20:30 UTC on the 9th.
    result = to_utc("2026-03-10T02:00:00", "Asia/Kolkata")
    assert result == datetime.datetime(2026, 3, 9, 20, 30, tzinfo=datetime.UTC)


def test_date_naive_and_aware_agree():
    naive = to_utc("2026-03-10T02:00:00", "Asia/Kolkata")
    aware = to_utc("2026-03-10T02:00:00+05:30", "Asia/Kolkata")
    assert naive == aware


def test_date_ist_stays_plus_five_thirty_no_dst():
    # Regardless of season, Asia/Kolkata never shifts (no DST).
    summer = to_utc("2026-07-10T02:00:00", "Asia/Kolkata")
    winter = to_utc("2026-01-10T02:00:00", "Asia/Kolkata")
    assert summer.hour == winter.hour == 20
    assert summer.day == 9
    assert winter.day == 9


def test_address_variants_collapse_to_same_key():
    a = address_key("12, MG Rd, Shastri Nagar Extn.")
    b = address_key("12 mg road shastri nagar extension")
    assert a == b


def test_address_different_addresses_do_not_collapse():
    a = address_key("12, MG Rd, Shastri Nagar")
    b = address_key("45, Church St, Koregaon Park")
    assert a != b


def test_name_honorifics_stripped_latin():
    assert normalize_name("Dr.  Mohammad   Ali") == "Mohammad Ali"


def test_name_honorifics_stripped_devanagari_script_preserved():
    assert normalize_name("श्री मोहम्मद अली") == "मोहम्मद अली"
