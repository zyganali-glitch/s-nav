from __future__ import annotations

from copy import deepcopy
import re
from collections import defaultdict
from datetime import datetime, timezone
from math import sqrt
from statistics import mean, median, pstdev
from typing import Any
from uuid import uuid4

from .form_template_service import (
    DEFAULT_FORM_TEMPLATE_ID,
    DEFAULT_FORM_TEMPLATE_NAME,
    resolve_form_template,
    slugify_form_template_name,
)


HEADER_SAFE_RE = re.compile(r"[^A-Z0-9_-]+")
LEGACY_DEFAULT_NET_POLICY_CODE = "minus_025"
NO_NET_POLICY_CODE = "none"
NET_POLICY_OPTIONS: list[dict[str, Any]] = [
    {
        "code": "correct_only",
        "label": "Net = dogru sayisi",
        "description": "Yanlislar netten dusulmez; net dogru sayisina esitlenir.",
        "wrong_penalty": 0.0,
    },
    {
        "code": "minus_025",
        "label": "4 yanlis 1 dogru goturur",
        "description": "Net = dogru - (yanlis x 0.25)",
        "wrong_penalty": 0.25,
    },
    {
        "code": "minus_0333",
        "label": "3 yanlis 1 dogru goturur",
        "description": "Net = dogru - (yanlis x 0.3333)",
        "wrong_penalty": round(1 / 3, 4),
    },
    {
        "code": "minus_050",
        "label": "2 yanlis 1 dogru goturur",
        "description": "Net = dogru - (yanlis x 0.50)",
        "wrong_penalty": 0.50,
    },
    {
        "code": "minus_100",
        "label": "1 yanlis 1 dogru goturur",
        "description": "Net = dogru - yanlis",
        "wrong_penalty": 1.0,
    },
]
NET_POLICY_INDEX = {item["code"]: item for item in NET_POLICY_OPTIONS}


def now_label() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_token(value: Any) -> str:
    text = str(value or "").strip().upper()
    return HEADER_SAFE_RE.sub("", text)


def normalize_answer(value: Any) -> str:
    text = str(value or "").strip().upper()
    return HEADER_SAFE_RE.sub("", text)


def build_full_name(decoded_fields: dict[str, Any]) -> str:
    first = str(decoded_fields.get("student_name") or "").strip()
    last = str(decoded_fields.get("student_surname") or "").strip()
    full = " ".join(item for item in (first, last) if item)
    return full.strip() or str(decoded_fields.get("student_full_name") or "").strip()


def resolve_net_policy(net_rule_code: str | None) -> dict[str, Any]:
    if net_rule_code is None:
        selected = dict(NET_POLICY_INDEX[LEGACY_DEFAULT_NET_POLICY_CODE])
        selected["enabled"] = True
        selected["is_legacy_default"] = True
        return selected

    normalized_code = str(net_rule_code or "").strip().lower()
    if not normalized_code or normalized_code == NO_NET_POLICY_CODE:
        return {
            "code": NO_NET_POLICY_CODE,
            "label": "Net hesabi yapilmadi",
            "description": "Operator net kurali secmeden oturumu tamamladi; net alanlari bilincli olarak bos birakildi.",
            "wrong_penalty": 0.0,
            "enabled": False,
            "is_legacy_default": False,
        }

    selected = NET_POLICY_INDEX.get(normalized_code)
    if not selected:
        supported_codes = ", ".join(item["code"] for item in NET_POLICY_OPTIONS)
        raise ValueError(f"Bilinmeyen net kurali: {net_rule_code}. Desteklenen kodlar: {supported_codes}")

    resolved = dict(selected)
    resolved["enabled"] = True
    resolved["is_legacy_default"] = False
    return resolved


def compute_net_count(correct_count: int, wrong_count: int, net_policy: dict[str, Any]) -> float | None:
    if not net_policy.get("enabled"):
        return None
    return round(correct_count - (wrong_count * float(net_policy.get("wrong_penalty") or 0.0)), 2)


def format_response_marker(marked_answer: str, outcome: str) -> str:
    normalized_answer = normalize_answer(marked_answer)
    if outcome == "correct":
        return f"{normalized_answer or '-'}(D)"
    if outcome == "wrong":
        return f"{normalized_answer or '-'}(Y)"
    return "-(B)"


def build_rank_sort_key(student_result: dict[str, Any]) -> tuple[float, float, float, float, str]:
    return (
        -float(student_result.get("score") or 0.0),
        -float(student_result.get("correct_count") or 0),
        float(student_result.get("wrong_count") or 0),
        float(student_result.get("blank_count") or 0),
        normalize_token(student_result.get("student_id") or ""),
    )


def assign_rank_field(student_results: list[dict[str, Any]], indexes: list[int], field_name: str) -> None:
    sorted_indexes = sorted(indexes, key=lambda index: build_rank_sort_key(student_results[index]))
    previous_key: tuple[float, float, float, float, str] | None = None
    current_rank = 0
    for position, index in enumerate(sorted_indexes, start=1):
        current_key = build_rank_sort_key(student_results[index])
        if current_key != previous_key:
            current_rank = position
            previous_key = current_key
        student_results[index][field_name] = current_rank


def assign_student_ranks(student_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not student_results:
        return student_results

    all_indexes = list(range(len(student_results)))
    assign_rank_field(student_results, all_indexes, "exam_rank")

    classroom_indexes: dict[str, list[int]] = defaultdict(list)
    for index, student_result in enumerate(student_results):
        classroom = str(student_result.get("classroom") or "").strip()
        if classroom:
            classroom_indexes[classroom].append(index)
        else:
            student_result["class_rank"] = None

    for indexes in classroom_indexes.values():
        assign_rank_field(student_results, indexes, "class_rank")

    student_results.sort(key=lambda item: (item.get("exam_rank") or 999999, normalize_token(item.get("student_id") or "")))
    return student_results


def mean_or_none(values: list[float | int]) -> float | None:
    if not values:
        return None
    return round(mean(values), 2)


def weighted_mean_or_none(weighted_values: list[tuple[float, float]]) -> float | None:
    filtered = [(value, weight) for value, weight in weighted_values if weight > 0]
    if not filtered:
        return None
    total_weight = sum(weight for _, weight in filtered)
    if total_weight <= 0:
        return None
    return round(sum(value * weight for value, weight in filtered) / total_weight, 3)


def sort_choice_tokens(tokens: set[str]) -> list[str]:
    preferred_order = ["A", "B", "C", "D", "E"]
    remaining = sorted(token for token in tokens if token and token not in preferred_order)
    return [token for token in preferred_order if token in tokens] + remaining


def build_student_highlight(student_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "exam_rank": student_result.get("exam_rank"),
        "student_id": student_result.get("student_id"),
        "student_full_name": student_result.get("student_full_name") or student_result.get("student_name") or "",
        "classroom": student_result.get("classroom") or "",
        "booklet_code": student_result.get("booklet_code") or "",
        "score": student_result.get("score"),
        "correct_count": student_result.get("correct_count"),
        "wrong_count": student_result.get("wrong_count"),
        "blank_count": student_result.get("blank_count"),
        "net_count": student_result.get("net_count"),
    }


def pearson_correlation(values_x: list[float], values_y: list[float]) -> float | None:
    if len(values_x) < 2 or len(values_x) != len(values_y):
        return None
    mean_x = sum(values_x) / len(values_x)
    mean_y = sum(values_y) / len(values_y)
    sum_sq_x = sum((value - mean_x) ** 2 for value in values_x)
    sum_sq_y = sum((value - mean_y) ** 2 for value in values_y)
    if sum_sq_x <= 0 or sum_sq_y <= 0:
        return None
    covariance = sum((value_x - mean_x) * (value_y - mean_y) for value_x, value_y in zip(values_x, values_y))
    return round(covariance / sqrt(sum_sq_x * sum_sq_y), 3)


def classify_reliability(alpha: float | None) -> str:
    if alpha is None:
        return "Orneklem veya varyans yetersiz oldugu icin alpha hesaplanamadi."
    if alpha < 0.6:
        return "Ic tutarlilik dusuk duzeydedir."
    if alpha < 0.7:
        return "Ic tutarlilik sinirda/kisitli duzeydedir."
    if alpha < 0.8:
        return "Ic tutarlilik kabul edilebilir duzeydedir."
    if alpha < 0.9:
        return "Ic tutarlilik yuksek duzeydedir."
    return "Ic tutarlilik cok yuksek duzeydedir."


def classify_point_biserial(value: float | None) -> str:
    if value is None:
        return "Yetersiz varyans"
    if value < 0.1:
        return "Cok zayif"
    if value < 0.2:
        return "Zayif"
    if value < 0.3:
        return "Kabul edilebilir"
    if value < 0.4:
        return "Iyi"
    return "Cok iyi"


def classify_difficulty_index(value: float) -> str:
    if value < 0.3:
        return "Zor"
    if value < 0.8:
        return "Orta"
    return "Kolay"


def classify_discrimination_index(value: float) -> str:
    if value < 10:
        return "Riskli"
    if value < 20:
        return "Izlem"
    return "Guclu"


def build_analysis_glossary(net_policy: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "term": "Net kurali",
            "how": net_policy.get("description") or "Oturum aninda operator secimine gore kilitlenir.",
            "why": "Farkli kurumlarin ceza politikalari ayni ham okuma uzerinde izlenebilir ve tekrarlanabilir bicimde uygulanabilsin diye kullanilir.",
            "value_use": "Raporlanan net, sira ve ilgili ozetler ayni secili kurala deterministic olarak baglanir.",
        },
        {
            "term": "Ayirt indeksi",
            "how": "Ust %27 ve alt %27 gruplarin dogru cevaplama oranlari farki alinir.",
            "why": "Maddenin yuksek basari gosteren ogrenciler ile dusuk basari gosteren ogrencileri ayirma gucunu izlemek icin kullanilir.",
            "value_use": "Dusuk degerler madde revizyonu, yanit anahtari kontrolu veya kazanim uyumu acisindan alarm uretir.",
        },
        {
            "term": "Gucluk indeksi (p)",
            "how": "Dogru cevap oraninin 0-1 araligindaki sayisal karsiligidir; p = dogru_orani / 100.",
            "why": "Maddenin ne kadar kolay veya zor oldugunu sayisal olarak gostermek icin kullanilir.",
            "value_use": "Norm-referenced sinavlarda orta banda yakin degerler genellikle daha dengeli bilgi tasir.",
        },
        {
            "term": "Madde std sapmasi",
            "how": "Dikotom maddede std = sqrt(p*(1-p)) olarak hesaplanir.",
            "why": "Maddenin ogrenciler arasinda yayilim uretme kapasitesini gosteren klasik test kurami gostergesidir.",
            "value_use": "Degerin sifira yaklasmasi maddenin cok kolay/cok zor oldugunu ve varyans tasimadigini gosterir.",
        },
        {
            "term": "Nokta-cift serili korelasyon",
            "how": "Madde dogrulugu (0/1) ile madde disi toplam puan arasindaki Pearson korelasyonu hesaplanir.",
            "why": "Maddenin testin genel olcme dogrultusuyla ne kadar uyumlu calistigini gosterir.",
            "value_use": "Dusuk veya negatif degerler anahtar hatasi, belirsiz madde ya da hedef disi davranis isareti olabilir.",
        },
        {
            "term": "Kitapcik sirasi / anahtar",
            "how": "Ogretmen tanimindaki kanonik soru kaydinda tutulan booklet_mappings.position ve booklet_mappings.correct_answer alanlarindan uretilir.",
            "why": "Bu alanlar optikten tahmin edilmez; sinav tasariminda tanimlanan permutasyonun rapora aynen yansitilmasi icin kullanilir.",
            "value_use": "Bu nedenle sahte tamamlayici degil, kanonik sinav taniminin deterministic izdusumudur.",
        },
        {
            "term": "Genel sira / sinif sira",
            "how": "Ayni oturumdaki ogrenciler puan, dogru, yanlis, bos ve ogrenci no tie-break sirasiyla siralanir; sinif sira optikte cozulmus classroom alanina gore alt gruplarda ayni kuralla hesaplanir.",
            "why": "Operator ve ogretmenin bireysel sonucun oturum ici goreli konumunu hizli okuyabilmesi icin kullanilir.",
            "value_use": "Sinif sira yalnizca optikten cozulmus sinif bilgisine gore uretilir; sistemsel sinif tahmini yapilmaz.",
        },
    ]


def build_academic_commentary(
    summary: dict[str, Any],
    question_summary: list[dict[str, Any]],
    highlights: dict[str, Any],
    net_policy: dict[str, Any],
) -> list[dict[str, str]]:
    student_count = int(summary.get("student_count") or 0)
    total_questions = int(summary.get("total_questions") or 0)
    weighted_difficulty = weighted_mean_or_none([
        (float(item.get("difficulty_index") or 0.0), float(item.get("weight") or 0.0))
        for item in question_summary
    ])
    weighted_point_biserial = weighted_mean_or_none([
        (float(item.get("point_biserial") or 0.0), float(item.get("weight") or 0.0))
        for item in question_summary
        if item.get("point_biserial") is not None
    ])
    hardest = highlights.get("hardest_questions", [])
    weak = highlights.get("weak_discrimination_questions", [])
    hardest_text = ", ".join(f"S{item.get('canonical_no')}" for item in hardest[:3]) or "belirgin degil"
    weak_text = ", ".join(f"S{item.get('canonical_no')}" for item in weak[:3]) or "belirgin degil"
    high_weight_risks = sorted(
        [item for item in question_summary if float(item.get("weight") or 0.0) > 0],
        key=lambda item: (-float(item.get("weight") or 0.0), float(item.get("discrimination_index") or 0.0), int(item.get("canonical_no") or 0)),
    )[:3]
    high_weight_risk_text = ", ".join(
        f"S{item.get('canonical_no')} (agirlik {item.get('weight')})" for item in high_weight_risks
    ) or "belirgin degil"

    commentary = [
        {
            "title": "Oturum metodolojisi",
            "text": (
                f"Bu rapor {student_count} ogrenci ve {total_questions} maddelik oturum uzerinden klasik test kurami gostergeleriyle uretilmistir; "
                f"net hesaplari '{net_policy.get('label')}' kuralina gore oturum aninda kilitlenmistir."
            ),
        },
        {
            "title": "Ic tutarlilik yorumu",
            "text": (
                f"Cronbach alpha {summary.get('reliability_alpha') if summary.get('reliability_alpha') is not None else 'hesaplanamadi'} olarak bulunmustur; "
                f"{classify_reliability(summary.get('reliability_alpha'))}"
            ),
        },
        {
            "title": "Gucluk dengesi",
            "text": (
                f"Soru agirliklari dikkate alindiginda agirlikli ortalama gucluk indeksi p={weighted_difficulty if weighted_difficulty is not None else 'hesaplanamadi'} duzeyindedir; "
                f"bu bulgu testin puana etkisi yuksek maddeler uzerinden genel zorluk duzeyinin {'orta banda yakin' if weighted_difficulty is not None and 0.35 <= weighted_difficulty <= 0.8 else 'asimetrik'} bir dagilim sergiledigini gosterir."
            ),
        },
        {
            "title": "Ayirt edicilik yorumu",
            "text": (
                f"Soru agirliklariyla agirliklandirilmis ortalama nokta-cift serili korelasyon {weighted_point_biserial if weighted_point_biserial is not None else 'hesaplanamadi'} olup, "
                f"en cok izlenmesi gereken ayirt edicilik riski tasiyan maddeler {weak_text}; puana etkisi yuksek maddeler icinde ilk izlenecekler {high_weight_risk_text}; en zor maddeler ise {hardest_text} olarak gorunmektedir."
            ),
        },
    ]
    return commentary


def summarize_exam(exam: dict[str, Any]) -> dict[str, Any]:
    total_weight = round(sum(float(item["weight"]) for item in exam.get("questions", [])), 2)
    answer_key_profile = exam.get("answer_key_profile") or {}
    optical_booklets = exam.get("optical_answer_key_booklets") or {}
    return {
        "exam_code": exam["exam_code"],
        "title": exam["title"],
        "description": exam.get("description", ""),
        "form_template_id": exam.get("form_template_id", DEFAULT_FORM_TEMPLATE_ID),
        "form_template_name": exam.get("form_template_name", DEFAULT_FORM_TEMPLATE_NAME),
        "has_answer_key": bool(exam.get("questions")),
        "answer_key_updated_at": answer_key_profile.get("updated_at"),
        "answer_key_source": answer_key_profile.get("source_label"),
        "optical_answer_key_ready_booklets": sorted(optical_booklets.keys()),
        "optical_answer_key_ready_count": len(optical_booklets),
        "booklet_codes": list(exam.get("booklet_codes", [])),
        "question_count": len(exam.get("questions", [])),
        "max_score": total_weight,
        "updated_at": exam.get("updated_at"),
        "session_count": len(exam.get("sessions", [])),
    }


def build_exam_detail(exam: dict[str, Any]) -> dict[str, Any]:
    enriched_exam = enrich_exam_sessions_for_reporting(exam)
    detail = dict(enriched_exam)
    detail["summary"] = summarize_exam(enriched_exam)
    detail["active_form_template"] = {
        "id": enriched_exam.get("form_template_id", DEFAULT_FORM_TEMPLATE_ID),
        "name": enriched_exam.get("form_template_name", DEFAULT_FORM_TEMPLATE_NAME),
    }
    detail["answer_key_profile"] = deepcopy(enriched_exam.get("answer_key_profile") or {})
    detail["optical_answer_key_booklets"] = deepcopy(enriched_exam.get("optical_answer_key_booklets") or {})
    detail["recent_sessions"] = list(enriched_exam.get("sessions", []))
    return detail


def build_answer_key_profile(
    *,
    source_type: str,
    source_label: str,
    question_count: int,
    import_format: str,
    booklet_strategy: str,
    source_file: str | None = None,
) -> dict[str, Any]:
    return {
        "source_type": source_type,
        "source_label": source_label,
        "source_file": source_file or "",
        "import_format": import_format,
        "booklet_strategy": booklet_strategy,
        "question_count": question_count,
        "updated_at": now_label(),
    }


def normalize_exam_payload(
    payload: dict[str, Any],
    existing_exam: dict[str, Any] | None = None,
    form_template_catalog: list[dict[str, Any]] | None = None,
    answer_key_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    exam_code = normalize_token(payload.get("exam_code"))
    if not exam_code:
        raise ValueError("Sınav kodu zorunludur.")

    title = str(payload.get("title", "")).strip()
    if len(title) < 1:
        raise ValueError("Sınav başlığı zorunludur.")

    booklet_codes: list[str] = []
    for raw_code in payload.get("booklet_codes", []):
        code = normalize_token(raw_code)
        if code and code not in booklet_codes:
            booklet_codes.append(code)
    if not booklet_codes:
        raise ValueError("En az bir kitapcik kodu girilmelidir.")

    catalog = list(form_template_catalog or [])
    requested_template_id = payload.get("form_template_id") or (existing_exam or {}).get("form_template_id")
    normalized_requested_template_id = slugify_form_template_name(requested_template_id)
    selected_template = resolve_form_template(requested_template_id, catalog)
    if catalog and requested_template_id and selected_template["id"] != normalized_requested_template_id:
        raise ValueError("Secilen optik kagit formati bulunamadi.")

    seen_canonical: set[int] = set()
    position_registry: dict[str, dict[int, int]] = {code: {} for code in booklet_codes}
    questions: list[dict[str, Any]] = []

    for raw_question in payload.get("questions", []):
        canonical_no = int(raw_question.get("canonical_no") or 0)
        if canonical_no <= 0:
            raise ValueError("Her soru icin gecerli bir kanonik sira gerekir.")
        if canonical_no in seen_canonical:
            raise ValueError(f"Ayni kanonik soru numarasi iki kez kullanildi: {canonical_no}")
        seen_canonical.add(canonical_no)

        weight = float(raw_question.get("weight") or 0)
        if weight <= 0:
            raise ValueError(f"Soru {canonical_no} icin agirlik sifirdan buyuk olmalidir.")

        group_label = str(raw_question.get("group_label", "Genel")).strip() or "Genel"
        booklet_mappings: dict[str, dict[str, Any]] = {}
        raw_mappings = raw_question.get("booklet_mappings", {}) or {}

        for booklet_code in booklet_codes:
            raw_mapping = raw_mappings.get(booklet_code, {}) or {}
            position = int(raw_mapping.get("position") or 0)
            correct_answer = normalize_answer(raw_mapping.get("correct_answer"))
            if position <= 0:
                raise ValueError(f"Soru {canonical_no} / {booklet_code} icin soru sirasi girilmelidir.")
            if not correct_answer:
                raise ValueError(f"Soru {canonical_no} / {booklet_code} icin dogru cevap girilmelidir.")
            if position in position_registry[booklet_code]:
                other_question = position_registry[booklet_code][position]
                raise ValueError(
                    f"{booklet_code} kitapciginda {position}. sira hem {other_question} hem {canonical_no} icin kullanildi."
                )
            position_registry[booklet_code][position] = canonical_no
            booklet_mappings[booklet_code] = {
                "position": position,
                "correct_answer": correct_answer,
            }

        questions.append(
            {
                "canonical_no": canonical_no,
                "group_label": group_label,
                "weight": round(weight, 2),
                "booklet_mappings": booklet_mappings,
            }
        )

    questions.sort(key=lambda item: item["canonical_no"])
    exam = {
        "exam_code": exam_code,
        "title": title,
        "description": str(payload.get("description", "")).strip(),
        "form_template_id": selected_template["id"],
        "form_template_name": selected_template["name"],
        "booklet_codes": booklet_codes,
        "questions": questions,
        "sessions": list((existing_exam or {}).get("sessions", [])),
    }

    existing_questions = list((existing_exam or {}).get("questions", []))
    if answer_key_profile is not None:
        exam["answer_key_profile"] = deepcopy(answer_key_profile)
    elif not questions:
        exam["answer_key_profile"] = {}
    elif existing_questions == questions:
        exam["answer_key_profile"] = deepcopy((existing_exam or {}).get("answer_key_profile") or {})
    else:
        exam["answer_key_profile"] = build_answer_key_profile(
            source_type="manual",
            source_label="Form duzenleyici",
            question_count=len(questions),
            import_format="manual",
            booklet_strategy="manual",
        )
    return exam


def compute_import_session(
    exam: dict[str, Any],
    parsed_rows: list[dict[str, Any]],
    file_name: str,
    import_format: str,
    net_rule_code: str | None = None,
) -> dict[str, Any]:
    if not parsed_rows:
        raise ValueError("Import dosyasinda islenecek satir bulunamadi.")

    net_policy = resolve_net_policy(net_rule_code)

    question_groups: dict[str, float] = defaultdict(float)
    group_question_counts: dict[str, int] = defaultdict(int)
    for question in exam["questions"]:
        question_groups[question["group_label"]] += float(question["weight"])
        group_question_counts[question["group_label"]] += 1

    question_stats: dict[int, dict[str, Any]] = {}
    for question in exam["questions"]:
        question_stats[question["canonical_no"]] = {
            "canonical_no": question["canonical_no"],
            "group_label": question["group_label"],
            "weight": question["weight"],
            "correct_count": 0,
            "wrong_count": 0,
            "blank_count": 0,
            "student_count": 0,
            "option_counts": defaultdict(int),
            "observations": [],
            "booklets": {
                booklet: {"correct_count": 0, "wrong_count": 0, "blank_count": 0, "student_count": 0}
                for booklet in exam["booklet_codes"]
            },
        }

    booklet_totals: dict[str, dict[str, Any]] = {
        booklet: {"student_count": 0, "scores": [], "accuracies": [], "corrects": [], "wrongs": [], "blanks": [], "nets": []}
        for booklet in exam["booklet_codes"]
    }
    group_totals: dict[str, dict[str, Any]] = {
        group: {
            "scores": [],
            "accuracy_values": [],
            "corrects": [],
            "wrongs": [],
            "blanks": [],
            "nets": [],
            "max_score": round(max_score, 2),
            "question_count": group_question_counts.get(group, 0),
        }
        for group, max_score in question_groups.items()
    }

    warnings: list[str] = []
    student_results: list[dict[str, Any]] = []
    total_weight = round(sum(float(question["weight"]) for question in exam["questions"]), 2)
    total_questions = len(exam["questions"])
    skipped_rows = 0

    for row in parsed_rows:
        booklet_code = normalize_token(row.get("booklet_code"))
        if booklet_code not in booklet_totals:
            skipped_rows += 1
            warnings.append(
                f"{row.get('source_row')} numarali satir bilinmeyen kitapcik nedeniyle atlandi: {booklet_code or 'BOS'}"
            )
            continue

        answers = {str(key): normalize_answer(value) for key, value in (row.get("answers") or {}).items()}
        decoded_fields = {
            str(key): str(value).strip()
            for key, value in (row.get("decoded_fields") or {}).items()
            if str(value).strip()
        }
        score = 0.0
        correct_count = 0
        wrong_count = 0
        blank_count = 0
        group_score_map: dict[str, float] = defaultdict(float)
        group_correct_map: dict[str, int] = defaultdict(int)
        group_wrong_map: dict[str, int] = defaultdict(int)
        group_blank_map: dict[str, int] = defaultdict(int)
        per_question_outcomes: dict[int, tuple[bool, bool]] = {}
        question_responses: list[dict[str, Any]] = []

        for question in exam["questions"]:
            group_label = question["group_label"]
            mapping = question["booklet_mappings"][booklet_code]
            position_key = str(mapping["position"])
            expected_answer = normalize_answer(mapping["correct_answer"])
            actual_answer = answers.get(position_key, "")
            stats = question_stats[question["canonical_no"]]
            booklet_stats = stats["booklets"][booklet_code]
            stats["student_count"] += 1
            booklet_stats["student_count"] += 1

            outcome = "blank"

            if not actual_answer:
                blank_count += 1
                stats["blank_count"] += 1
                stats["option_counts"]["BLANK"] += 1
                booklet_stats["blank_count"] += 1
                group_blank_map[group_label] += 1
                per_question_outcomes[question["canonical_no"]] = (False, True)
            elif actual_answer == expected_answer:
                score += float(question["weight"])
                correct_count += 1
                stats["correct_count"] += 1
                stats["option_counts"][actual_answer] += 1
                booklet_stats["correct_count"] += 1
                group_score_map[group_label] += float(question["weight"])
                group_correct_map[group_label] += 1
                per_question_outcomes[question["canonical_no"]] = (True, False)
                outcome = "correct"
            else:
                wrong_count += 1
                stats["wrong_count"] += 1
                stats["option_counts"][actual_answer] += 1
                booklet_stats["wrong_count"] += 1
                group_wrong_map[group_label] += 1
                per_question_outcomes[question["canonical_no"]] = (False, False)
                outcome = "wrong"

            question_responses.append(
                {
                    "canonical_no": question["canonical_no"],
                    "group_label": group_label,
                    "booklet_position": mapping["position"],
                    "expected_answer": expected_answer,
                    "marked_answer": normalize_answer(actual_answer),
                    "outcome": outcome,
                    "display_value": format_response_marker(actual_answer, outcome),
                }
            )

        for canonical_no, (is_correct, is_blank) in per_question_outcomes.items():
            question_stats[canonical_no]["observations"].append(
                {
                    "score": score,
                    "correct_count": correct_count,
                    "is_correct": is_correct,
                    "is_blank": is_blank,
                }
            )

        weighted_percent = round((score / total_weight) * 100, 2) if total_weight else 0.0
        accuracy_percent = round((correct_count / total_questions) * 100, 2) if total_questions else 0.0
        net_count = compute_net_count(correct_count, wrong_count, net_policy)
        booklet_totals[booklet_code]["student_count"] += 1
        booklet_totals[booklet_code]["scores"].append(score)
        booklet_totals[booklet_code]["accuracies"].append(accuracy_percent)
        booklet_totals[booklet_code]["corrects"].append(correct_count)
        booklet_totals[booklet_code]["wrongs"].append(wrong_count)
        booklet_totals[booklet_code]["blanks"].append(blank_count)
        if net_count is not None:
            booklet_totals[booklet_code]["nets"].append(net_count)

        group_scores: list[dict[str, Any]] = []
        for group_name, max_score in question_groups.items():
            group_total_questions = group_question_counts.get(group_name, 0)
            group_score = round(group_score_map.get(group_name, 0.0), 2)
            group_correct_count = group_correct_map.get(group_name, 0)
            group_wrong_count = group_wrong_map.get(group_name, 0)
            group_blank_count = group_blank_map.get(group_name, 0)
            group_accuracy = round((group_correct_count / group_total_questions) * 100, 2) if group_total_questions else 0.0
            group_net_count = compute_net_count(group_correct_count, group_wrong_count, net_policy)
            group_totals[group_name]["scores"].append(group_score)
            group_totals[group_name]["accuracy_values"].append(group_accuracy)
            group_totals[group_name]["corrects"].append(group_correct_count)
            group_totals[group_name]["wrongs"].append(group_wrong_count)
            group_totals[group_name]["blanks"].append(group_blank_count)
            if group_net_count is not None:
                group_totals[group_name]["nets"].append(group_net_count)
            group_scores.append(
                {
                    "group_label": group_name,
                    "score": group_score,
                    "max_score": round(max_score, 2),
                    "question_count": group_total_questions,
                    "accuracy_percent": group_accuracy,
                    "correct_count": group_correct_count,
                    "wrong_count": group_wrong_count,
                    "blank_count": group_blank_count,
                    "net_count": group_net_count,
                }
            )

        student_results.append(
            {
                "student_id": row.get("student_id") or f"SATIR-{row.get('source_row')}",
                "student_name": decoded_fields.get("student_name", ""),
                "student_surname": decoded_fields.get("student_surname", ""),
                "student_full_name": build_full_name(decoded_fields),
                "class_number": decoded_fields.get("class_number", ""),
                "class_section": decoded_fields.get("class_section", ""),
                "classroom": decoded_fields.get("classroom", ""),
                "system_exam_code": exam["exam_code"],
                "scanned_exam_code": decoded_fields.get("exam_code", ""),
                "scanned_exam_date": decoded_fields.get("exam_date", ""),
                "booklet_code": booklet_code,
                "source_row": row.get("source_row"),
                "total_questions": total_questions,
                "score": round(score, 2),
                "weighted_percent": weighted_percent,
                "accuracy_percent": accuracy_percent,
                "correct_count": correct_count,
                "wrong_count": wrong_count,
                "blank_count": blank_count,
                "net_count": net_count,
                "decoded_fields": decoded_fields,
                "group_scores": group_scores,
                "question_responses": question_responses,
                "response_summary": " | ".join(
                    f"S{item['canonical_no']}:{item['display_value']}" for item in question_responses
                ),
            }
        )

    if not student_results:
        raise ValueError("Import dosyasindaki satirlar gecerli kitapcik kodlariyla eslesmedi.")

    booklet_summary = []
    for booklet_code, aggregate in booklet_totals.items():
        if not aggregate["student_count"]:
            continue
        booklet_summary.append(
            {
                "booklet_code": booklet_code,
                "student_count": aggregate["student_count"],
                "total_score": round(sum(aggregate["scores"]), 2),
                "total_correct_count": sum(aggregate["corrects"]),
                "total_wrong_count": sum(aggregate["wrongs"]),
                "total_blank_count": sum(aggregate["blanks"]),
                "total_net_count": round(sum(aggregate["nets"]), 2) if aggregate["nets"] else None,
                "average_score": round(mean(aggregate["scores"]), 2),
                "average_accuracy_percent": round(mean(aggregate["accuracies"]), 2),
                "average_correct_count": round(mean(aggregate["corrects"]), 2),
                "average_wrong_count": round(mean(aggregate["wrongs"]), 2),
                "average_blank_count": round(mean(aggregate["blanks"]), 2),
                "average_net_count": mean_or_none(aggregate["nets"]),
                "max_score": total_weight,
            }
        )
    booklet_summary.sort(key=lambda item: item["booklet_code"])

    group_summary = []
    for group_name, aggregate in group_totals.items():
        group_summary.append(
            {
                "group_label": group_name,
                "question_count": aggregate["question_count"],
                "student_count": len(student_results),
                "total_score": round(sum(aggregate["scores"]), 2) if aggregate["scores"] else 0.0,
                "total_correct_count": sum(aggregate["corrects"]),
                "total_wrong_count": sum(aggregate["wrongs"]),
                "total_blank_count": sum(aggregate["blanks"]),
                "total_net_count": round(sum(aggregate["nets"]), 2) if aggregate["nets"] else None,
                "average_score": round(mean(aggregate["scores"]), 2) if aggregate["scores"] else 0.0,
                "average_correct_count": round(mean(aggregate["corrects"]), 2) if aggregate["corrects"] else 0.0,
                "average_wrong_count": round(mean(aggregate["wrongs"]), 2) if aggregate["wrongs"] else 0.0,
                "average_blank_count": round(mean(aggregate["blanks"]), 2) if aggregate["blanks"] else 0.0,
                "average_net_count": mean_or_none(aggregate["nets"]),
                "average_accuracy_percent": round(mean(aggregate["accuracy_values"]), 2) if aggregate["accuracy_values"] else 0.0,
                "max_score": aggregate["max_score"],
            }
        )
    group_summary.sort(key=lambda item: item["group_label"])

    sorted_indexes = sorted(range(len(student_results)), key=lambda index: build_rank_sort_key(student_results[index]))
    upper_group_size = max(1, int(round(len(student_results) * 0.27))) if student_results else 0
    upper_indexes = set(sorted_indexes[:upper_group_size])
    lower_indexes = set(sorted_indexes[-upper_group_size:])

    question_summary = []
    for question in exam["questions"]:
        stats = question_stats[question["canonical_no"]]
        student_count = stats["student_count"]
        observations = stats.get("observations") or []
        upper_group = [observations[index] for index in sorted(upper_indexes) if index < len(observations)]
        lower_group = [observations[index] for index in sorted(lower_indexes) if index < len(observations)]
        upper_correct_rate = round((sum(1 for item in upper_group if item["is_correct"]) / len(upper_group)) * 100, 2) if upper_group else 0.0
        lower_correct_rate = round((sum(1 for item in lower_group if item["is_correct"]) / len(lower_group)) * 100, 2) if lower_group else 0.0
        discrimination_index = round(upper_correct_rate - lower_correct_rate, 2)
        correct_rate = round((stats["correct_count"] / student_count) * 100, 2) if student_count else 0.0
        wrong_rate = round((stats["wrong_count"] / student_count) * 100, 2) if student_count else 0.0
        blank_rate = round((stats["blank_count"] / student_count) * 100, 2) if student_count else 0.0
        difficulty_index = round(correct_rate / 100, 4)
        item_variance = round(difficulty_index * (1 - difficulty_index), 4)
        item_std_dev = round(sqrt(item_variance), 4)
        item_scores = [1.0 if item["is_correct"] else 0.0 for item in observations]
        corrected_total_scores = [
            float(item["score"]) - float(question["weight"]) if item["is_correct"] else float(item["score"])
            for item in observations
        ]
        point_biserial = pearson_correlation(item_scores, corrected_total_scores)
        expected_choices = {
            normalize_answer(mapping.get("correct_answer") or "")
            for mapping in question.get("booklet_mappings", {}).values()
            if normalize_answer(mapping.get("correct_answer") or "")
        }
        observed_choices = {token for token, count in stats["option_counts"].items() if token != "BLANK" and count > 0}
        distribution_choices = sort_choice_tokens(expected_choices | observed_choices | {"A", "B", "C", "D", "E"})
        choice_distribution = {
            choice: {
                "count": int(stats["option_counts"].get(choice, 0)),
                "rate": round((int(stats["option_counts"].get(choice, 0)) / student_count) * 100, 2) if student_count else 0.0,
            }
            for choice in distribution_choices
        }
        blank_distribution = {
            "count": int(stats["option_counts"].get("BLANK", 0)),
            "rate": round((int(stats["option_counts"].get("BLANK", 0)) / student_count) * 100, 2) if student_count else 0.0,
        }
        question_summary.append(
            {
                "canonical_no": question["canonical_no"],
                "group_label": question["group_label"],
                "student_count": student_count,
                "weight": question["weight"],
                "correct_rate": correct_rate,
                "wrong_rate": wrong_rate,
                "blank_rate": blank_rate,
                "difficulty_index": difficulty_index,
                "item_variance": item_variance,
                "item_std_dev": item_std_dev,
                "point_biserial": point_biserial,
                "point_biserial_label": classify_point_biserial(point_biserial),
                "upper_group_correct_rate": upper_correct_rate,
                "lower_group_correct_rate": lower_correct_rate,
                "discrimination_index": discrimination_index,
                "difficulty_label": classify_difficulty_index(difficulty_index),
                "discrimination_label": classify_discrimination_index(discrimination_index),
                "choice_distribution": choice_distribution,
                "blank_distribution": blank_distribution,
                "booklet_positions": {
                    booklet: question["booklet_mappings"][booklet]["position"]
                    for booklet in exam["booklet_codes"]
                    if booklet in question["booklet_mappings"]
                },
                "booklet_answer_key": {
                    booklet: question["booklet_mappings"][booklet]["correct_answer"]
                    for booklet in exam["booklet_codes"]
                    if booklet in question["booklet_mappings"]
                },
                "booklets": {
                    booklet: {
                        "correct_rate": round((booklet_stats["correct_count"] / booklet_stats["student_count"]) * 100, 2) if booklet_stats["student_count"] else 0.0,
                        "wrong_rate": round((booklet_stats["wrong_count"] / booklet_stats["student_count"]) * 100, 2) if booklet_stats["student_count"] else 0.0,
                        "blank_rate": round((booklet_stats["blank_count"] / booklet_stats["student_count"]) * 100, 2) if booklet_stats["student_count"] else 0.0,
                    }
                    for booklet, booklet_stats in stats["booklets"].items()
                },
            }
        )

    assign_student_ranks(student_results)
    score_values = [float(item["score"]) for item in student_results]
    average_score = round(mean(item["score"] for item in student_results), 2)
    average_percent = round(mean(item["weighted_percent"] for item in student_results), 2)
    average_accuracy = round(mean(item["accuracy_percent"] for item in student_results), 2)
    average_correct_count = round(mean(item["correct_count"] for item in student_results), 2)
    average_wrong_count = round(mean(item["wrong_count"] for item in student_results), 2)
    average_blank_count = round(mean(item["blank_count"] for item in student_results), 2)
    average_net_count = mean_or_none([item["net_count"] for item in student_results if item.get("net_count") is not None])

    reliability_alpha: float | None = None
    if total_questions >= 2 and len(student_results) >= 2:
        total_correct_values = [float(item["correct_count"]) for item in student_results]
        total_variance = pstdev(total_correct_values) ** 2 if len(total_correct_values) > 1 else 0.0
        if total_variance > 0:
            item_variance_sum = 0.0
            for stats in question_stats.values():
                observations = stats.get("observations") or []
                if not observations:
                    continue
                p_value = sum(1 for item in observations if item["is_correct"]) / len(observations)
                item_variance_sum += p_value * (1 - p_value)
            reliability_alpha = round((total_questions / (total_questions - 1)) * (1 - (item_variance_sum / total_variance)), 2)

    hardest_questions = sorted(question_summary, key=lambda item: (item["correct_rate"], -item["blank_rate"], item["canonical_no"]))[:3]
    easiest_questions = sorted(question_summary, key=lambda item: (-item["correct_rate"], item["blank_rate"], item["canonical_no"]))[:3]
    most_blank_questions = sorted(question_summary, key=lambda item: (-item["blank_rate"], item["canonical_no"]))[:3]
    weak_discrimination = sorted(question_summary, key=lambda item: (item["discrimination_index"], item["canonical_no"]))[:3]
    top_students = [build_student_highlight(item) for item in student_results[:3]]
    lowest_students = [build_student_highlight(item) for item in sorted(student_results, key=build_rank_sort_key, reverse=True)[:3]]
    assessment_highlights = {
        "hardest_questions": hardest_questions,
        "easiest_questions": easiest_questions,
        "most_blank_questions": most_blank_questions,
        "weak_discrimination_questions": weak_discrimination,
        "top_students": top_students,
        "lowest_students": lowest_students,
    }
    academic_commentary = build_academic_commentary(
        {
            "student_count": len(student_results),
            "total_questions": total_questions,
            "reliability_alpha": reliability_alpha,
        },
        question_summary,
        assessment_highlights,
        net_policy,
    )
    analysis_glossary = build_analysis_glossary(net_policy)

    return {
        "session_id": uuid4().hex[:10],
        "created_at": now_label(),
        "source_file": file_name,
        "import_format": import_format,
        "net_policy": net_policy,
        "summary": {
            "student_count": len(student_results),
            "total_questions": total_questions,
            "average_score": average_score,
            "average_percent": average_percent,
            "average_accuracy_percent": average_accuracy,
            "average_correct_count": average_correct_count,
            "average_wrong_count": average_wrong_count,
            "average_blank_count": average_blank_count,
            "average_net_count": average_net_count,
            "net_policy_code": net_policy["code"],
            "net_policy_label": net_policy["label"],
            "max_score": total_weight,
            "min_score": round(min(score_values), 2),
            "median_score": round(median(score_values), 2),
            "max_observed_score": round(max(score_values), 2),
            "score_std_dev": round(pstdev(score_values), 2) if len(score_values) > 1 else 0.0,
            "completion_rate": round(((total_questions - average_blank_count) / total_questions) * 100, 2) if total_questions else 0.0,
            "reliability_alpha": reliability_alpha,
            "skipped_rows": skipped_rows,
        },
        "analysis_glossary": analysis_glossary,
        "academic_commentary": academic_commentary,
        "booklet_summary": booklet_summary,
        "group_summary": group_summary,
        "question_summary": question_summary,
        "assessment_highlights": assessment_highlights,
        "student_preview": student_results[:25],
        "student_results": student_results,
        "warnings": warnings,
    }


def session_needs_reporting_upgrade(session: dict[str, Any]) -> bool:
    if not session.get("analysis_glossary") or not session.get("academic_commentary"):
        return True

    if not any("agirlik" in str(item.get("text") or "").lower() for item in session.get("academic_commentary") or []):
        return True

    booklet_summary = list(session.get("booklet_summary") or [])
    if booklet_summary and any("total_score" not in row for row in booklet_summary):
        return True

    group_summary = list(session.get("group_summary") or [])
    if group_summary and any("total_score" not in row or "student_count" not in row for row in group_summary):
        return True

    question_summary = list(session.get("question_summary") or [])
    if question_summary and any(
        any(field not in row for field in (
            "difficulty_index",
            "item_variance",
            "item_std_dev",
            "point_biserial",
            "point_biserial_label",
            "upper_group_correct_rate",
            "lower_group_correct_rate",
            "choice_distribution",
            "blank_distribution",
        ))
        for row in question_summary
    ):
        return True

    return False


def rebuild_parsed_rows_from_session(session: dict[str, Any]) -> list[dict[str, Any]]:
    parsed_rows: list[dict[str, Any]] = []
    for index, student in enumerate(session.get("student_results") or session.get("student_preview") or [], start=1):
        booklet_code = normalize_token(student.get("booklet_code"))
        if not booklet_code:
            continue

        answers: dict[str, str] = {}
        for response in student.get("question_responses") or []:
            booklet_position = response.get("booklet_position")
            if booklet_position is None:
                continue
            marked_answer = normalize_answer(response.get("marked_answer") or "")
            if marked_answer:
                answers[str(booklet_position)] = marked_answer

        decoded_fields = deepcopy(student.get("decoded_fields") or {})
        for key in (
            "student_number",
            "student_name",
            "student_surname",
            "student_full_name",
            "class_number",
            "class_section",
            "classroom",
            "exam_code",
            "exam_date",
        ):
            value = str(student.get(key) or "").strip()
            if value and not decoded_fields.get(key):
                decoded_fields[key] = value

        parsed_rows.append(
            {
                "student_id": student.get("student_id") or f"SATIR-{student.get('source_row') or index}",
                "booklet_code": booklet_code,
                "answers": answers,
                "source_row": student.get("source_row") or index,
                "decoded_fields": decoded_fields,
            }
        )

    return parsed_rows


def enrich_session_for_reporting(exam: dict[str, Any], session: dict[str, Any]) -> dict[str, Any]:
    if not session_needs_reporting_upgrade(session):
        return deepcopy(session)

    parsed_rows = rebuild_parsed_rows_from_session(session)
    if not parsed_rows:
        return deepcopy(session)

    net_policy_code = (session.get("net_policy") or {}).get("code") or (session.get("summary") or {}).get("net_policy_code")
    rebuilt = compute_import_session(
        exam,
        parsed_rows,
        str(session.get("source_file") or "legacy-session"),
        str(session.get("import_format") or "legacy-session"),
        net_rule_code=str(net_policy_code) if net_policy_code is not None else None,
    )
    rebuilt["session_id"] = session.get("session_id") or rebuilt.get("session_id")
    rebuilt["created_at"] = session.get("created_at") or rebuilt.get("created_at")
    rebuilt["warnings"] = list(dict.fromkeys([*(session.get("warnings") or []), *(rebuilt.get("warnings") or [])]))
    return rebuilt


def enrich_exam_sessions_for_reporting(exam: dict[str, Any]) -> dict[str, Any]:
    enriched_exam = deepcopy(exam)
    enriched_exam["sessions"] = [
        enrich_session_for_reporting(exam, session)
        for session in exam.get("sessions", [])
    ]
    return enriched_exam
