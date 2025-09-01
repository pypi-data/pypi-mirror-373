import os
import requests
from simple_error_log.errors import Errors
from usdm3.ct.cdisc.library import Library as CtLibrary


class LibraryAPI:
    API_ROOT = "https://api.library.cdisc.org/api/cosmos/v2"

    def __init__(
        self,
        ct_library: CtLibrary,
    ):
        self._errors = Errors()
        self._ct_library = ct_library
        self._api_key = os.getenv("CDISC_API_KEY")
        if not self._api_key:
            self._errors.error("Empty CDISC API key")
        self._headers = {"Content-Type": "application/json", "api-key": self._api_key}
        self._package_metadata = {}
        self._package_items = {}
        self._bc_responses = {}
        self._bcs_raw = {}
        self._map = {}

    def refresh(self):
        self._get_package_metadata()
        self._get_package_items()
        self._get_sdtm_bcs()
        self._get_generic_bcs()
        return self._bcs_raw

    @property
    def errors(self) -> Errors:
        return self._errors

    @property
    def valid(self) -> bool:
        return self._errors.error_count()

    def _get_package_metadata(self):
        urls = {
            "generic": "/mdr/bc/packages",
            "sdtm": "/mdr/specializations/sdtm/packages",
        }
        for url_type, url in urls.items():
            try:
                api_url = self._url(url)
                self._errors.info(f"Processing package metadata for '{api_url}'")
                raw = requests.get(api_url, headers=self._headers)
                response = raw.json()
                print("#", end="", flush=True)
                self._package_metadata[url_type] = response["_links"]["packages"]
            except Exception as e:
                self._errors.exception(
                    f"Failed to retrieve CDISC BC package metadata from '{api_url}'", e
                )

    def _get_package_items(self) -> dict:
        for package_type in ["sdtm", "generic"]:
            self._package_items[package_type] = {}
            for package in self._package_metadata[package_type]:
                self._get_package(package, package_type)

    def _get_package(self, package, package_type):
        try:
            response_field = {
                "sdtm": "datasetSpecializations",
                "generic": "biomedicalConcepts",
            }
            api_url = self._url(package["href"]) if "href" in package else "not set"
            self._errors.info(f"Processing package for '{api_url}'")
            raw = requests.get(api_url, headers=self._headers)
            response = raw.json()
            print("#", end="", flush=True)
            for item in response["_links"][response_field[package_type]]:
                key = item["title"].upper()
                if package_type == "sdtm":
                    self._package_items[package_type][key] = item
                    # map[item['href']] = key
                elif package_type == "generic" and key not in self._package_items:
                    self._package_items[package_type][key] = item
                    self._map[item["href"]] = key
        except Exception as e:
            self._errors.exception(
                f"Failed to retrieve CDISC BC metadata from '{api_url}'", e
            )
            return {}

    def _get_sdtm_bcs(self):
        print(f"\n\nSDTM: {len(self._package_items['sdtm'].keys())}")
        count = 0
        for name, item in self._package_items["sdtm"].items():
            count += 1
            # if count > 5:
            #     break
            print(f"[{count}]", end="", flush=True) if count % 10 == 0 else print(
                ".", end="", flush=True
            )
            self._errors.info(f"Processing SDTM BC '{name}' ...")
            sdtm, generic = self._get_from_url_all(name, item)
            if sdtm:
                bc = self._sdtm_bc_as_usdm(sdtm, generic)
                if bc:
                    if "variables" in sdtm:
                        for item in sdtm["variables"]:
                            property = self._sdtm_bc_property_as_usdm(item, generic)
                            if property:
                                bc["properties"].append(property)
                    self._bcs_raw[name] = bc
                if generic:
                    href = generic["_links"]["self"]["href"]
                    if href in self._map:
                        self._map.pop(href)
                    else:
                        self._errors.info(f"Missing reference when popping {href}")

    def _get_generic_bcs(self) -> dict:
        print(f"\n\nGeneric: {len(self._package_items['generic'].keys())}")
        count = 0
        for name, item in self._package_items["generic"].items():
            count += 1
            # if count > 5:
            #     break
            print(f"[{count}]", end="", flush=True) if count % 10 == 0 else print(
                ".", end="", flush=True
            )
            self._errors.info(f"Processing Generic BC '{name}' ...")
            if self._process_genric_bc(name):
                response = self._get_from_url(item["href"])
                bc = self._generic_bc_as_usdm(response)
                if "dataElementConcepts" in response:
                    for item in response["dataElementConcepts"]:
                        property = self._generic_bc_property_as_usdm(item)
                        if property:
                            bc["properties"].append(property)
                self._bcs_raw[name] = bc

    def _generic_bc_as_usdm(self, api_bc) -> dict:
        concept_code = self._code_object(api_bc["conceptId"], api_bc["shortName"])
        synonyms = api_bc["synonyms"] if "synonyms" in api_bc else []
        return self._biomedical_concept_object(
            api_bc["shortName"],
            api_bc["shortName"],
            synonyms,
            api_bc["_links"]["self"]["href"],
            concept_code,
        )

    def _generic_bc_property_as_usdm(self, property) -> dict:
        concept_code = self._code_object(property["conceptId"], property["shortName"])
        responses = []
        if "exampleSet" in property:
            for example in property["exampleSet"]:
                # term = self._ct_library.preferred_term(example)
                term = None
                if term is not None:
                    code = self._code_object(term["conceptId"], term["preferredTerm"])
                    responses.append(self._response_code_object(code))
        return self._biomedical_concept_property_object(
            property["shortName"],
            property["shortName"],
            property["dataType"],
            responses,
            concept_code,
        )

    def _sdtm_bc_as_usdm(self, sdtm, generic) -> dict:
        try:
            if self._process_sdtm_bc(sdtm["shortName"]):
                role_variable = self._get_role_variable(sdtm)
                if role_variable:
                    if "assignedTerm" in role_variable:
                        if (
                            "conceptId" in role_variable["assignedTerm"]
                            and "value" in role_variable["assignedTerm"]
                        ):
                            concept_code = self._code_object(
                                role_variable["assignedTerm"]["conceptId"],
                                role_variable["assignedTerm"]["value"],
                            )
                        else:
                            self._errors.warning(
                                f"Failed to set BC concept, assigned term path, {sdtm['shortName']}"
                            )
                            concept_code = self._code_object(
                                "No Concept Code",
                                role_variable["assignedTerm"]["value"],
                            )
                    else:
                        self._errors.warning(
                            f"Failed to set BC concept, no assigned term path, {sdtm['shortName']}"
                        )
                        concept_code = self._code_object(
                            generic["conceptId"], generic["shortName"]
                        )
                else:
                    self._errors.warning(
                        f"Failed to set BC concept, no role variable, {sdtm['shortName']}"
                    )
                    concept_code = self._code_object(
                        generic["conceptId"], generic["shortName"]
                    )
                synonyms = generic["synonyms"] if "synonyms" in generic else []
                synonyms.append(generic["shortName"])
                return self._biomedical_concept_object(
                    sdtm["shortName"],
                    sdtm["shortName"],
                    synonyms,
                    sdtm["_links"]["self"]["href"],
                    concept_code,
                )
            else:
                return None
        except Exception as e:
            self._errors.exception(f"Failed to build BC '{sdtm['shortName']}'", e)
            return None

    def _sdtm_bc_property_as_usdm(self, sdtm_property, generic) -> dict:
        try:
            if self._process_property(sdtm_property["name"]):
                if "dataElementConceptId" in sdtm_property:
                    generic_match = self._get_dec_match(
                        generic, sdtm_property["dataElementConceptId"]
                    )
                    if generic_match:
                        concept_code = self._code_object(
                            generic_match["conceptId"], generic_match["shortName"]
                        )
                    else:
                        if (
                            "assignedTerm" in sdtm_property
                            and "conceptId" in sdtm_property["assignedTerm"]
                            and "value" in sdtm_property["assignedTerm"]
                        ):
                            concept_code = self._code_object(
                                sdtm_property["dataElementConceptId"],
                                sdtm_property["name"],
                            )
                        else:
                            self._errors.warning(
                                f"Failed to set property concept, DEC path, {sdtm_property}"
                            )
                            concept_code = self._code_object(
                                sdtm_property["dataElementConceptId"],
                                sdtm_property["name"],
                            )
                else:
                    if "assignedTerm" in sdtm_property:
                        concept_code = self._code_object(
                            sdtm_property["assignedTerm"]["conceptId"],
                            sdtm_property["assignedTerm"]["value"],
                        )
                    else:
                        self._errors.error(
                            f"Failed to set property concept, non DEC path, {sdtm_property}"
                        )
                        concept_code = self._code_object(
                            "No Concept Code", sdtm_property["name"]
                        )
                responses = []
                codes = []
                if "valueList" in sdtm_property:
                    codelist = (
                        sdtm_property["codelist"]["conceptId"]
                        if "codelist" in sdtm_property
                        else None
                    )
                    for value in sdtm_property["valueList"]:
                        term = self._ct_library.preferred_term(value, codelist)
                        if term:
                            code = self._code_object(
                                term["conceptId"], term["preferredTerm"]
                            )
                            codes.append(code)
                        else:
                            term = self._ct_library.submission(value, codelist)
                            if term:
                                code = self._code_object(
                                    term["conceptId"], term["preferredTerm"]
                                )
                                codes.append(code)
                            else:
                                cl = f", code list {sdtm_property['codelist']['conceptId'] if 'codelist' in sdtm_property else '<not defined>'}"
                                self._errors.error(
                                    f"Failed to find submission or preferred term '{value}' {cl}\nProperty:\n{sdtm_property}"
                                )
                for code in codes:
                    response_code = self._response_code_object(code)
                    responses.append(response_code)
                datatype = (
                    sdtm_property["dataType"] if "dataType" in sdtm_property else ""
                )
                return self._biomedical_concept_property_object(
                    sdtm_property["name"],
                    sdtm_property["name"],
                    datatype,
                    responses,
                    concept_code,
                )
            else:
                return None
        except Exception as e:
            self._errors.exception(f"Failed to build property {sdtm_property}", e)
            return None

    def _process_sdtm_bc(self, name):
        if name in [
            "Exclusion Criteria 01",
            "Inclusion Criteria 01",
            "Medical History Prespecified: Alzheimer's Disease",
            "Medical History Prespecified: Confusional Episodes",
            "Medical History Prespecified: Essential Tremor",
            "Medical History Prespecified: Extrapyramidal Features",
            "Medical History Prespecified: Facial Masking",
            "Medical History Prespecified: Rigidity Upper Extremity",
            "Medical History Prespecified: Sensitivity to Neuroleptics",
            "Medical History Prespecified: Visual Hallucinations",
            "TTS Acceptability Survey - Patch Acceptability",
            "TTS Acceptability Survey - Patch Appearance",
            "TTS Acceptability Survey - Patch Durability",
            "TTS Acceptability Survey - Patch Size",
            "Beer Use History",
            "Cigarette History",
            "Cigar History",
            "Coffee Use History",
            "Cola Use History",
            "Distilled Spirits Use History",
            "Pipe History",
            "Tea Use History",
            "Wine Use History",
        ]:
            return False
        return True

    def _process_genric_bc(self, name):
        return True if name.upper() in ["SUBJECT AGE", "RACE", "SEX"] else False

    def _process_property(self, name):
        if name[2:] in [
            "TEST",
            "STRESN",
            "STRESU",
            "STRESC",
            "CLASCD",
            "LOINC",
            "LOT",
            "CAT",
            "SCAT",
            "LLT",
            "LLTCD",
            "HLT",
            "HLTCD",
            "PTCD",
            "BODSYS",
            "BDSYCD",
            "SOC",
            "SOCCD",
            "RLDEV",
        ]:
            return False
        if name in ["EPOCH"]:
            return False
        return True

    def _get_role_variable(self, data):
        try:
            return next(
                (item for item in data["variables"] if item["role"] == "Topic"), None
            )
        except Exception:
            self._errors.warning(f"Failed to find role in {data}")
            return None

    def _get_dec_match(self, data, id):
        try:
            return next(
                (
                    item
                    for item in data["dataElementConcepts"]
                    if item["conceptId"] == id
                ),
                None,
            )
        except Exception:
            self._errors.warning(f"Failed to find DEC in {data} for '{id}'")
            return None

    def _get_from_url_all(self, name, details) -> dict:
        try:
            sdtm_response = self._get_from_url(details["href"])
            generic = sdtm_response["_links"]["parentBiomedicalConcept"]
            generic_response = self._get_from_url(generic["href"])
            return sdtm_response, generic_response
        except Exception as e:
            self._errors.exception(
                f"Failed to retrieve CDISC BC metadata for {name} from '{details['href']}'",
                e,
            )
            return None, None

    def _get_from_url(self, url):
        api_url = self._url(url)
        raw = requests.get(api_url, headers=self._headers)
        result = raw.json()
        return result

    def _url(self, relative_url) -> str:
        return "%s%s" % (self.__class__.API_ROOT, relative_url)

    def _code_object(self, code, decode):
        return {
            "id": "tbd",
            "code": code,
            "codeSystem": self._ct_library.system,
            "codeSystemVersion": self._ct_library.version,
            "decode": decode,
            "instanceType": "Code",
        }

    def _alias_code_object(self, standard_code, aliases):
        return (
            {
                "id": "tbd",
                "standardCode": standard_code,
                "standardCodeAliases": aliases,
                "instanceType": "AliasCode",
            }
            if standard_code
            else None
        )

    def _response_code_object(self, code: dict):
        return {
            "id": "tbd",
            "name": f"RC_{code['code']}",
            "label": "",
            "isEnabled": True,
            "code": code,
            "instanceType": "ResponseCode",
        }

    def _biomedical_concept_property_object(
        self, name, label, datatype, responses, code
    ) -> dict:
        alias_code = self._alias_code_object(code, [])
        return {
            "id": "tbd",
            "name": name,
            "label": label,
            "isRequired": True,
            "isEnabled": True,
            "datatype": datatype,
            "responseCodes": responses,
            "code": alias_code,
            "instanceType": "BiomedicalConceptProperty",
        }

    def _biomedical_concept_object(
        self, name, label, synonyms, reference, code
    ) -> dict:
        alias_code = self._alias_code_object(code, [])
        return {
            "id": "tbd",
            "name": name,
            "label": label,
            "synonyms": synonyms,
            "reference": reference,
            "properties": [],
            "code": alias_code,
            "instanceType": "BiomedicalConcept",
        }
