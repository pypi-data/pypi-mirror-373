import os
import re
import requests


class LibraryAPI:
    API_ROOT = "https://api.library.cdisc.org/api"

    def __init__(self, packages: list) -> None:
        self._packages = None
        self._package_list = packages
        self._headers = {
            "Content-Type": "application/json",
            "api-key": os.environ.get("CDISC_API_KEY"),
        }

    def refresh(self) -> None:
        self._packages = self._get_packages()

    def code_list(self, c_code: str) -> dict | None:
        for package in self._package_list:
            version = self._package_version(package)
            if version:
                package_full_name = f"{package}-{version}"
                api_url = self._url(
                    f"/mdr/ct/packages/{package_full_name}/codelists/{c_code}"
                )
                raw = requests.get(api_url, headers=self._headers)
                if raw.status_code == 200:
                    response = raw.json()
                    response.pop("_links", None)
                    response["source"] = {"effective_date": version, "package": package}
                    return response
        return None

    def all_code_lists(self) -> list:
        results = []
        for package in self._package_list:
            version = self._package_version(package)
            if version:
                package_full_name = f"{package}-{version}"
                api_url = self._url(f"/mdr/ct/packages/{package_full_name}/codelists")
                raw = requests.get(api_url, headers=self._headers)
                if raw.status_code == 200:
                    response = raw.json()
                    result = {
                        "effective_date": version,
                        "package": package,
                        "code_lists": [],
                    }
                    for item in response["_links"]["codelists"]:
                        href = item["href"]
                        result["code_lists"].append(href.split("/")[-1])
                    results.append(result)
        return results

    def package_code_list(self, package: str, version: str, c_code: str) -> dict:
        package_full_name = f"{package}-{version}"
        api_url = self._url(f"/mdr/ct/packages/{package_full_name}/codelists/{c_code}")
        raw = requests.get(api_url, headers=self._headers)
        if raw.status_code == 200:
            response = raw.json()
            response.pop("_links", None)
            response["source"] = {"effective_date": version, "package": package}
            return response
        else:
            return None

    def _get_packages(self) -> dict | None:
        packages = {}
        api_url = self._url("/mdr/ct/packages")
        raw = requests.get(api_url, headers=self._headers)
        if raw.status_code == 200:
            response = raw.json()
            for item in response["_links"]["packages"]:
                name = self._extract_ct_name(item["href"])
                effective_date = self._extract_effective_date(item["title"])
                if name and effective_date:
                    if name not in packages:
                        packages[name] = []
                    packages[name].append(
                        {"effective": effective_date, "url": item["href"]}
                    )
            return packages
        else:
            return None

    def _extract_ct_name(self, url: str) -> str:
        match = re.search(r"([a-zA-Z]+)-\d{4}-\d{2}-\d{2}$", url)
        if match:
            return match.group(1)
        return None

    def _extract_effective_date(self, title: str) -> str:
        match = re.search(r"Effective (\d{4}-\d{2}-\d{2})$", title)
        if match:
            return match.group(1)
        return None

    def _url(self, relative_url: str) -> str:
        return f"{self.API_ROOT}{relative_url}"

    def _package_version(self, package: str) -> str | None:
        try:
            return self._packages[package][-1]["effective"]
        except Exception:
            return None
