import re
from datetime import date, datetime


def validate_email(email: str) -> tuple[bool, str]:
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if not email or not email.strip():
        return False, "Email address is required."
    if not re.match(pattern, email.strip()):
        return False, "Invalid email format. Example: patient@email.com"
    return True, ""


def validate_date_of_birth(dob) -> tuple[bool, str]:
    if dob is None:
        return False, "Date of birth is required."
    today = date.today()
    if isinstance(dob, str):
        try:
            dob = datetime.strptime(dob, "%Y-%m-%d").date()
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD."
    if dob >= today:
        return False, "Date of birth cannot be today or a future date."
    age = (today - dob).days // 365
    if age > 130:
        return False, "Date of birth seems invalid (age > 130 years)."
    return True, ""


def validate_numeric(value, field_name: str, min_val: float = 0, max_val: float = 10000) -> tuple[bool, str]:
    try:
        val = float(value)
    except (TypeError, ValueError):
        return False, f"{field_name} must be a numeric value."
    if val < min_val or val > max_val:
        return False, f"{field_name} must be between {min_val} and {max_val}."
    return True, ""


def validate_full_name(name: str) -> tuple[bool, str]:
    if not name or not name.strip():
        return False, "Full name is required."
    if len(name.strip()) < 2:
        return False, "Full name must be at least 2 characters."
    if len(name.strip()) > 100:
        return False, "Full name must be under 100 characters."
    return True, ""


def validate_patient_form(full_name, dob, email, glucose, haemoglobin, cholesterol) -> list[str]:
    errors = []

    ok, msg = validate_full_name(full_name)
    if not ok:
        errors.append(msg)

    ok, msg = validate_date_of_birth(dob)
    if not ok:
        errors.append(msg)

    ok, msg = validate_email(email)
    if not ok:
        errors.append(msg)

    ok, msg = validate_numeric(glucose, "Glucose", min_val=0, max_val=600)
    if not ok:
        errors.append(msg)

    ok, msg = validate_numeric(haemoglobin, "Haemoglobin", min_val=0, max_val=25)
    if not ok:
        errors.append(msg)

    ok, msg = validate_numeric(cholesterol, "Cholesterol", min_val=0, max_val=700)
    if not ok:
        errors.append(msg)

    return errors
