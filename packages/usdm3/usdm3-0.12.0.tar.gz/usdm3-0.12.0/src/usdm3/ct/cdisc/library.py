import os
from usdm3.ct.cdisc.library_api import LibraryAPI
from usdm3.ct.cdisc.config.config import Config
from usdm3.ct.cdisc.missing.missing import Missing
from usdm3.ct.cdisc.library_cache.library_cache import LibraryCache


class Library:
    """
    A class to manage CDISC controlled terminology (CT) data.

    This class handles loading, caching, and accessing CDISC controlled terminology,
    including code lists and their associated terms. It can load data from a local
    cache file or fetch it from the CDISC API when needed.
    """

    BASE_PATH = "ct/cdisc"
    USDM = "usdm"
    ALL = "all"

    def __init__(self, root_path: str, type: str = USDM):
        self.system = "http://www.cdisc.org"
        self.version = "2023-12-15"  # Default version.
        self.root_path = root_path
        self._type = (
            type.lower() if type.lower() in [self.USDM, self.ALL] else self.USDM
        )

        self._config = Config(
            os.path.join(self.root_path, self.BASE_PATH, "config")
        )  # Configuration for required code lists and mappings
        self._missing = Missing(
            os.path.join(self.root_path, self.BASE_PATH, "missing")
        )  # Handler for missing/additional code lists
        self._api = LibraryAPI(
            self._config.required_packages()
        )  # Interface to CDISC Library API
        self._cache = LibraryCache(
            os.path.join(self.root_path, self.BASE_PATH, "library_cache"),
            f"library_cache_{self._type}.yaml",
        )  # Cache file handler

        # Data structures to store and index controlled terminology
        self._by_code_list = {}  # Maps concept IDs to complete code list data
        self._by_term = {}  # Maps term concept IDs to parent code list IDs
        self._by_submission = {}  # Maps submission values to parent code list IDs
        self._by_pt = {}  # Maps preferred terms to parent code list IDs

    def load(self) -> None:
        if self._cache.exists():
            self._load_ct()  # Load from cache file
        else:
            self._api.refresh()  # Ensure API connection is fresh
            self._get_usdm_ct() if self._usdm() else self._get_all_ct()  # Fetch from API
            self._cache.save(self._by_code_list)  # Cache the results
        self._add_missing_ct()  # Add any additional required terminology

    def klass_and_attribute(self, klass, attribute) -> dict:
        try:
            concept_id = self._config.klass_and_attribute(klass, attribute)
            return self._by_code_list[concept_id]
        except Exception:
            return None

    def klass_and_attribute_value(
        self, klass: str, attribute: str, value: str
    ) -> tuple[dict, str]:
        try:
            concept_id = self._config.klass_and_attribute(klass, attribute)
            code_list = self._by_code_list[concept_id]
            return self._get_item(code_list, value), code_list["source"][
                "effective_date"
            ]
        except Exception:
            return None, None

    def unit(self, value: str) -> dict:
        try:
            code_list = self._by_code_list["C71620"]
            return self._get_item(code_list, value)
        except Exception:
            return None

    def unit_code_list(self) -> dict:
        return self._by_code_list["C71620"]

    def cl_by_term(self, term_code: str) -> dict:
        try:
            concept_ids = self._by_term[term_code]
            return self._by_code_list[concept_ids[0]]
        except Exception:
            return None

    def submission(self, value, cl=None):
        if value in list(self._by_submission.keys()):
            return self._find_in_collection(
                self._by_submission[value], "submissionValue", value, cl
            )
        else:
            return None

    def preferred_term(self, value, cl=None):
        if value in list(self._by_pt.keys()):
            return self._find_in_collection(
                self._by_pt[value], "preferredTerm", value, cl
            )
        else:
            return None

    def _usdm(self) -> bool:
        return self._type == self.USDM

    def _find_in_collection(self, concepts: list, key: str, value: str, cl: str = None):
        if len(concepts) == 0:
            return None
        elif len(concepts) == 1:
            code_list = self._by_code_list[concepts[0]]
            return next(
                (
                    item
                    for item in code_list["terms"]
                    if item[key].upper() == value.upper()
                ),
                None,
            )
        else:
            if cl and cl in concepts:
                code_list = self._by_code_list[cl]
                return next(
                    (
                        item
                        for item in code_list["terms"]
                        if item[key].upper() == value.upper()
                    ),
                    None,
                )
            else:
                return None

    def _get_item(self, code_list, value) -> dict:
        try:
            for field in ["conceptId", "preferredTerm", "submissionValue"]:
                result = next(
                    (
                        item
                        for item in code_list["terms"]
                        if item[field].upper() == value.upper()
                    ),
                    None,
                )
                if result:
                    return result
            return None
        except Exception:
            return None

    def _get_usdm_ct(self) -> None:
        for item in self._config.required_code_lists():
            print(f"[{item}] ", end="", flush=True)
            response = self._api.code_list(item)
            self._by_code_list[response["conceptId"]] = response
            for item in response["terms"]:
                # Index each term by its various identifiers
                self._check_in_and_add(
                    self._by_term, item["conceptId"], response["conceptId"]
                )
                self._check_in_and_add(
                    self._by_submission, item["submissionValue"], response["conceptId"]
                )
                self._check_in_and_add(
                    self._by_pt, item["preferredTerm"], response["conceptId"]
                )

    def _get_all_ct(self) -> None:
        for package in self._api.all_code_lists():
            length = len(package["code_lists"])
            print(f"\n\nPackage: {package}: {length}\n")
            for index, code_list in enumerate(package["code_lists"]):
                response = self._api.package_code_list(
                    package["package"], package["effective_date"], code_list
                )
                print(f"[{index}]", end="", flush=True) if index % 10 == 0 else print(
                    "#", end="", flush=True
                )
                self._by_code_list[response["conceptId"]] = response
                for item in response["terms"]:
                    # Index each term by its various identifiers
                    self._check_in_and_add(
                        self._by_term, item["conceptId"], response["conceptId"]
                    )
                    self._check_in_and_add(
                        self._by_submission,
                        item["submissionValue"],
                        response["conceptId"],
                    )
                    self._check_in_and_add(
                        self._by_pt, item["preferredTerm"], response["conceptId"]
                    )

    def _load_ct(self) -> None:
        self._by_code_list = self._cache.read()
        for c_code, entry in self._by_code_list.items():
            for item in entry["terms"]:
                # Rebuild indexes from cached data
                self._check_in_and_add(self._by_term, item["conceptId"], c_code)
                self._check_in_and_add(
                    self._by_submission, item["submissionValue"], c_code
                )
                self._check_in_and_add(self._by_pt, item["preferredTerm"], c_code)

    def _add_missing_ct(self) -> None:
        for response in self._missing.code_lists():
            self._by_code_list[response["conceptId"]] = response
            for item in response["terms"]:
                # Index the additional terms
                self._check_in_and_add(
                    self._by_term, item["conceptId"], response["conceptId"]
                )
                self._check_in_and_add(
                    self._by_submission, item["submissionValue"], response["conceptId"]
                )
                self._check_in_and_add(
                    self._by_pt, item["preferredTerm"], response["conceptId"]
                )

    def _check_in_and_add(self, collection: dict, id: str, item: str) -> None:
        if id not in collection:
            collection[id] = []
        collection[id].append(item)
