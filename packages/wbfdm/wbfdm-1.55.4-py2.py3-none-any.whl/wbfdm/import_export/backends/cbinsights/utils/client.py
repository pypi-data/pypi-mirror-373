import time
from datetime import date, datetime
from typing import Optional

import requests
from celery import shared_task
from tqdm import tqdm


class RateLimitException(Exception):
    pass


class CreditLimitException(Exception):
    pass


class Client:
    MAX_ORG_IDS_SIZE = 100

    def __init__(
        self, client_id: str, client_secret: str, limit: Optional[int] = 10, rate_limit_sleep: Optional[int] = 60
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.limit = limit
        self.rate_limit_sleep = rate_limit_sleep
        super().__init__()

    def connect(self):
        token = self._fetch_authorization_token()
        self.jwt_header_value = f"Bearer {token}"

    def _request(self, url, params=None, next_page_token=None):
        if not params:
            params = dict()
        resp = requests.get(
            url,
            params={**params, **{"nextPageToken": next_page_token}} if next_page_token else params,
            headers={"authorization": self.jwt_header_value},
        )
        if resp.status_code != 200:
            if resp.status_code == 429:
                raise RateLimitException()
            raise requests.ConnectionError(
                f"unexpected error from api\nstatus_code: {resp.status_code}\nerror: {resp.text}"
            )

        if credits_remaining_str := resp.headers.get("x-cbinsights-credits-remaining", None):
            if int(credits_remaining_str) <= 0:
                raise CreditLimitException()

        return resp.json()

    def _paginated_request(
        self,
        data_url: str,
        extra_params=None,
        last_update_time: Optional[datetime] = None,
    ):
        params = {"limit": self.limit}
        if last_update_time:
            params["lastUpdateTime"] = last_update_time.isoformat()
        if extra_params:
            params.update(extra_params)
        resp = self._request(data_url, params=params)
        yield resp
        next_page_token = resp["nextPageToken"]
        retry = 0
        while next_page_token and retry < 5:
            try:
                resp = self._request(data_url, params=params, next_page_token=next_page_token)
                yield resp
                next_page_token = resp["nextPageToken"]
            except RateLimitException:
                time.sleep(self.rate_limit_sleep)
                retry += 1
        if retry >= 5:
            raise RateLimitException()

    def _chunk_paginated_request(self, data_url, org_ids, extra_params, endpoint, debug: bool = False):
        data = []
        ranges = list(range(0, len(org_ids), self.MAX_ORG_IDS_SIZE))
        gen = tqdm(ranges, total=len(ranges)) if debug else ranges
        for x in gen:
            ids = org_ids[x : x + 100]
            for res in self._paginated_request(
                data_url,
                extra_params={"orgIds": ",".join(map(str, ids)), **extra_params},
            ):
                if _data := res.get(endpoint, None):
                    data.extend(_data)
        return data

    def _fetch_authorization_token(self):
        auth_url = "https://api.cbinsights.com/v1/authorize"

        auth_resp = requests.get(
            auth_url,
            params={"clientId": self.client_id, "clientSecret": self.client_secret},
        )

        if auth_resp.status_code != 200:
            raise Exception(
                f"unexpected error from api\nstatus_code: {auth_resp.status_code}\nerror: {auth_resp.text}"
            )

        token = auth_resp.json()["token"]

        return token

    def _get_tasks_signatures(self, org_ids, last_update_time, data_url):
        return [
            fetch_datapoint_by_id_asynchronously.s(self.jwt_header_value, data_url.format(org_id), limit=self.limit)
            for org_id in org_ids
        ]

    def fetch_credit_logs(self):
        return self._request("https://api.cbinsights.com/v1/credits")["creditLogs"]

    def fetch_organizations(
        self,
        org_ids: list[str],
        include_datapacks: Optional[str] = "orgSummary,orgKPIs,orgRevenue",
        last_update_time: date = None,
        debug: bool = False,
        **kwargs,
    ):
        extra_params = {"include": include_datapacks, **kwargs}
        if last_update_time:
            extra_params["lastUpdateTime"] = last_update_time.isoformat()
        return self._chunk_paginated_request(
            "https://api.cbinsights.com/v1/organizations", org_ids, extra_params, "organizations", debug=debug
        )

    def fetch_deals(
        self,
        org_ids: list[str],
        start: date = None,
        end: date = None,
        last_update_time: date = None,
        debug: bool = False,
        **extra_params,
    ):
        if start:
            extra_params["minDealDate"] = start.isoformat()
        if end:
            extra_params["maxDealDate"] = end.isoformat()
        if last_update_time:
            extra_params["lastUpdateTime"] = last_update_time.isoformat()
        return self._chunk_paginated_request(
            "https://api.cbinsights.com/v1/deals", org_ids, extra_params, "deals", debug=debug
        )

    # Sub deals utility functions.
    def fetch_fundings_for_id(self, org_id: str):
        data = []
        for res in self._paginated_request(f"https://api.cbinsights.com/v1/organizations/{org_id}/fundings"):
            if fundings_data := res.get("fundings", None):
                data.extend(fundings_data)
        return data

    def fetch_investments_for_id(self, org_id: str):
        data = []
        for res in self._paginated_request(f"https://api.cbinsights.com/v1/organizations/{org_id}/investments"):
            if investments_data := res.get("investments", None):
                data.extend(investments_data)
        return data

    def fetch_portfolioexits_for_id(self, org_id: str):
        data = []
        for res in self._paginated_request(f"https://api.cbinsights.com/v1/organizations/{org_id}/portfolioExits"):
            if portfolioexits_data := res.get("portfolioExits", None):
                data.extend(portfolioexits_data)
        return data

    def fetch_org_id(self, org_name, org_urls: list[str]) -> int:
        org_id = None
        i = 0
        while not org_id and i < len(org_urls):
            params = {"url": org_urls[i], "orgName": org_name}
            try:
                hits = self._request(
                    "https://api.cbinsights.com/v1/organizations/lookup",
                    params={k: v for k, v in params.items() if v},
                )["hits"]
                if len(hits) > 0:
                    org_id = hits[0]["orgId"]
            except requests.ConnectionError as e:
                print(e)  # noqa: T201
            i += 1
        return org_id


@shared_task(
    queue="importexport",
    autoretry_for=(Exception,),
    exponential_backoff=2,
    retry_kwargs={"max_retries": 2},
    retry_jitter=False,
)
def fetch_datapoint_by_id_asynchronously(
    jwt_header_value,
    data_url,
    last_update_time: Optional[datetime] = None,
    limit: Optional[int] = 10,
    rate_limit_sleep: Optional[int] = 60,
):
    params = {"limit": limit}
    if last_update_time:
        params["lastUpdateTime"] = last_update_time.isoformat()
    data = []

    resp = Client._request(jwt_header_value, data_url, params=params)
    data.append(resp)

    return data
