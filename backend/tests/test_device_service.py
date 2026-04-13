from backend.app.device_service import build_helper_failure_message, parse_mark_output


def test_parse_mark_output_summarizes_multiple_sheets() -> None:
    raw_text = """
[sheet_1]
front_rows=3
front_columns=4
front_type=16
front_marks=
0,0,0,0
0,13,0,0
0,0,12,0
[/sheet_1]
[sheet_2]
front_rows=2
front_columns=4
front_type=16
front_marks=
0,0,0,0
15,0,0,0
[/sheet_2]
""".strip()

    result = parse_mark_output(raw_text, threshold=12)

    assert result["sheet_count"] == 2
    assert result["sheets"][0]["candidate_mark_count"] == 2
    assert result["sheets"][0]["candidate_row_count"] == 2
    assert result["sheets"][0]["darkest_value"] == 13
    assert result["sheets"][1]["candidate_mark_count"] == 1
    assert result["sheets"][1]["preview"] == ["S2: K1=15"]


def test_build_helper_failure_message_translates_busy_operating_unit() -> None:
    helper_output = """
open_single_status=0x00000000
req_init_status=0x20312105
close_status=0x00000000
""".strip()

    result = build_helper_failure_message(helper_output, returncode=21)

    assert "hazirlama komutunu kabul etmedi" in result
    assert "panelinde aktif bir islem/menü" in result
    assert "req_init_status=0x20312105" in result


def test_build_helper_failure_message_translates_empty_hopper() -> None:
    helper_output = """
open_single_status=0x00000000
feed_mark_sheet_status=0x20028880
close_status=0x00000000
""".strip()

    result = build_helper_failure_message(helper_output, returncode=24)

    assert "formu besleyemedi" in result
    assert "Tepside kagit oldugunu" in result
    assert "feed_mark_sheet_status=0x20028880" in result


def test_build_helper_failure_message_translates_masked_empty_hopper_family() -> None:
    helper_output = """
open_single_status=0x00000000
feed_mark_sheet_status=0x200288A0
close_status=0x00000000
""".strip()

    result = build_helper_failure_message(helper_output, returncode=24)

    assert "formu besleyemedi" in result
    assert "feed_mark_sheet_status=0x200288A0" in result


def test_build_helper_failure_message_translates_hopper_empty_device_status() -> None:
    helper_output = """
open_single_status=0x00000000
device_status=hopper_empty
close_status=0x00000000
""".strip()

    result = build_helper_failure_message(helper_output, returncode=40)

    assert "Tepside okunacak form kalmadi" in result
    assert "device_status=hopper_empty" in result


def test_build_helper_failure_message_translates_driver_dll_missing_error() -> None:
    helper_output = """
error=driver_dll_missing
""".strip()

    result = build_helper_failure_message(helper_output, returncode=11)

    assert "surucu DLL'i bulunamadi" in result
    assert "error=driver_dll_missing" in result


def test_build_helper_failure_message_translates_generic_open_failure() -> None:
    helper_output = """
open_single_status=0x20010001
handle=0x00000000
""".strip()

    result = build_helper_failure_message(helper_output, returncode=20)

    assert "ilk baglanti kurulurken" in result
    assert "open_single_status=0x20010001" in result