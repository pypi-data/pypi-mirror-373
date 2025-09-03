import json
from hashlib import sha256

from talentro.vacancies.models import Vacancy as VacancyModel


def generate_vacancy_hash(vacancy_data: VacancyModel) -> str:
    data: dict = vacancy_data.model_dump()

    relevant_fields = {
        key: data[key]
        for key in [
            "title", "description", "status", "job_site_url", "company_name",
            "parent_company_name", "remote_type", "publish_date", "expiration_date",
            "last_updated_date", "category", "experience", "education", "hours_fte",
            "hours_min", "hours_max", "location_address", "location_zipcode",
            "location_city", "location_state", "location_country", "salary_min",
            "salary_max", "salary_currency", "salary_frequency", "recruiter_first_name",
            "recruiter_last_name", "recruiter_phone_number", "recruiter_email",
            "recruiter_role"
        ]
    }

    json_data = json.dumps(relevant_fields, sort_keys=True, default=str)
    return sha256(json_data.encode("utf-8")).hexdigest()