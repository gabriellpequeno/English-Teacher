import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

STUDENTS_DIR = Path(__file__).parent / "students"
STUDENTS_DIR.mkdir(exist_ok=True)


def _ts():
    return datetime.now(timezone.utc).isoformat()


def _save(profile: dict):
    path = STUDENTS_DIR / f"{profile['id']}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


def find_student(name: str) -> Optional[dict]:
    name_lower = name.lower().strip()
    for path in STUDENTS_DIR.glob("*.json"):
        with open(path, encoding="utf-8") as f:
            profile = json.load(f)
        if name_lower in profile.get("name", "").lower():
            return profile
    return None


def create_student(name: str) -> dict:
    profile = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "created_at": _ts(),
        "updated_at": _ts(),
        "cefr_level": None,
        "front_scores": {
            "writing": 0,
            "listening": 0,
            "speaking": 0,
            "grammar": 0,
            "vocabulary": 0,
            "pronunciation": 0,
        },
        "current_module_id": None,
        "completed_modules": [],
        "notes": [],
        "error_patterns": [],
    }
    _save(profile)
    return profile


def get_student(uuid: str) -> Optional[dict]:
    path = STUDENTS_DIR / f"{uuid}.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def add_note(uuid: str, text: str, category: str = "geral") -> dict:
    profile = get_student(uuid)
    if not profile:
        raise ValueError(f"Student {uuid} not found")
    notes = profile.setdefault("notes", [])
    for note in notes:
        if note["text"].lower() == text.lower() and not note.get("resolved"):
            note["last_observed"] = _ts()
            note["consecutive_successes"] = 0
            _save(profile)
            return profile
    notes.append({
        "id": f"note-{len(notes) + 1:03d}",
        "text": text,
        "category": category,
        "added_at": _ts(),
        "last_observed": _ts(),
        "consecutive_successes": 0,
        "resolved": False,
        "resolved_at": None,
    })
    _save(profile)
    return profile


def record_success(uuid: str, note_id: str, threshold: int = 10) -> Optional[dict]:
    profile = get_student(uuid)
    if not profile:
        return None
    for note in profile.get("notes", []):
        if note.get("id") == note_id and not note.get("resolved"):
            note["consecutive_successes"] = note.get("consecutive_successes", 0) + 1
            if note["consecutive_successes"] >= threshold:
                note["resolved"] = True
                note["resolved_at"] = _ts()
            _save(profile)
            return profile
    return profile


def resolve_note(uuid: str, note_id: str) -> Optional[dict]:
    profile = get_student(uuid)
    if not profile:
        return None
    for note in profile.get("notes", []):
        if note.get("id") == note_id:
            note["resolved"] = True
            note["resolved_at"] = _ts()
            _save(profile)
            return profile
    return profile


def update_profile(uuid: str, **kwargs) -> Optional[dict]:
    profile = get_student(uuid)
    if not profile:
        return None
    for key, value in kwargs.items():
        if key in ("id", "created_at"):
            continue
        profile[key] = value
    profile["updated_at"] = _ts()
    _save(profile)
    return profile
