import os
from usdm3.bc.cdisc.library_api import LibraryAPI
from usdm3.bc.cdisc.library_cache.library_cache import LibraryCache
from usdm3.ct.cdisc.library import Library as CtLibrary


class Library:
    API_ROOT = "https://api.library.cdisc.org/api/cosmos/v2"
    BASE_PATH = "bc/cdisc"

    def __init__(self, root_path: str, ct_library: CtLibrary):
        self._ct_library = CtLibrary
        self.root_path = root_path
        self._api = LibraryAPI(ct_library)  # Interface to CDISC Library API
        self._cache = LibraryCache(
            os.path.join(self.root_path, self.BASE_PATH, "library_cache"),
            "library_cache.yaml",
        )  # Cache file handler
        self._bcs = {}
        self._bc_index = {}

    def load(self) -> None:
        if self._cache.exists():
            self._load_bcs()  # Load from cache file
        else:
            self._get_bcs()  # Fetch from API
            self._cache.save(self._bcs)  # Cache the results
        self._create_bc_index()

    def exists(self, name: str) -> bool:
        return True if name.upper() in self._bc_index else False

    def catalogue(self) -> list:
        return list(self._bcs.keys())

    def usdm(self, name: str) -> dict:
        return self._get_bc_data(name) if self.exists(name) else None

    def _load_bcs(self) -> None:
        self._bcs = self._cache.read()

    def _get_bcs(self) -> None:
        self._bcs = self._api.refresh()  # Ensure API connection is fresh

    def _create_bc_index(self) -> None:
        for name, item in self._bcs.items():
            self._bc_index[name] = name
            for synonym in item["synonyms"]:
                self._bc_index[synonym.upper()] = name

    def _get_bc_data(self, name: str) -> dict:
        return self._bcs[self._bc_index[name.upper()]]
