import json

from wbcore.contrib.geography.models import Geography

from wbfdm.models import ClassificationGroup

FIELDS_MAP = {
    "orgName": "name",
    "url": "primary_url",
    "description": "description",
}


def parse(import_source):
    cbinsight_group = ClassificationGroup.objects.get_or_create(name="CBinsights", max_depth=2)[0]
    content = json.load(import_source.file)

    data = []
    for org_data in content:
        d = {
            "provider_id": org_data["orgId"],
            "description": org_data["description"],
            "name": org_data["orgName"],
            "primary_url": org_data["url"],
            "instrument_type": "private_equity",
        }
        if summary := org_data.get("orgSummary", None):
            if additional_urls := summary.get("additionalUrls", None):
                d["additional_urls"] = additional_urls
            if alternative_names := summary.get("aliases", None):
                d["alternative_names"] = alternative_names
            d["founded_year"] = summary["foundedYear"]

            if (country_name := summary.get("country")) and (
                country := Geography.countries.get_by_name(country_name.strip())
            ):
                d["country"] = country.id

                if city_name := summary.get("city", None):
                    # We comment this out because looking up the city at import time drastically decrease speed
                    # if city := Geography.cities.get_by_name(city_name.strip(), parent__parent=country):
                    #     d["headquarter_city"] = city.id
                    if (postal_code := summary.get("postalCode", None)) and (street := summary.get("street", None)):
                        d["headquarter_address"] = f"{street}, {postal_code} {city_name}"

            if sector_id := summary.get("sectorId", None):
                try:
                    code_aggregated = f"{int(sector_id):03}"
                    if industry_id := summary.get("industryId", None):
                        code_aggregated += f"{int(industry_id):03}"
                        if subindustry_id := summary.get("subindustryId", None):
                            code_aggregated += f"{int(subindustry_id):03}"
                except Exception:
                    pass
                d["classifications"] = [{"code_aggregated": code_aggregated, "group": cbinsight_group.id}]
        data.append(d)
    return {"data": data}
