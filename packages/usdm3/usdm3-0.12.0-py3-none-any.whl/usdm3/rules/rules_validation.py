import os
import sys
import inspect
import importlib
import traceback
from pathlib import Path
from typing import List, Type
from usdm3.rules.library.rule_template import RuleTemplate
from usdm3.data_store.data_store import DataStore, DecompositionError
from usdm3.ct.cdisc.library import Library as CTLibrary
from usdm3.rules.rules_validation_results import RulesValidationResults
from usdm3.base.singleton import Singleton


class RulesValidation3(metaclass=Singleton):
    PACKAGE_NAME = "usdm3.rules.library"

    def __init__(self, root_path: str):
        self.rules_validation = RulesValidationEngine(root_path, self.PACKAGE_NAME)

    def validate(self, filename: str):
        return self.rules_validation.validate_rules(filename)


class RulesValidationEngine:
    def __init__(self, root_path: str, package_name: str):
        self.root_path = root_path
        # print(f"LIBRARY: {root_path}, {package_name}")
        self.library_path = os.path.join(self.root_path, "rules/library")
        # print(f"PATHS: {self.root_path}, {self.library_path}, {self.ct_path}")
        self.package_name = package_name
        self.rules: List[Type[RuleTemplate]] = []
        self._load_rules()

    def validate_rules(self, filename: str) -> RulesValidationResults:
        data_store, e = self._data_store(filename)
        if data_store:
            ct = CTLibrary(self.root_path)
            ct.load()
            config = {"data": data_store, "ct": ct}
            results = self._execute_rules(config)
        else:
            results = RulesValidationResults()
            results.add_exception("Decomposition", e)
        return results

    def _data_store(self, filename: str) -> DataStore:
        try:
            data_store = DataStore(filename)
            data_store.decompose()
            return data_store, None
        except DecompositionError as e:
            return None, e

    def _load_rules(self) -> None:
        # Iterate through all .py files in the library directory
        for file in Path(self.library_path).glob("rule_*.py"):
            if file.name.startswith("rule_ddf") and file.name.endswith(".py"):
                try:
                    # Create module name from file name
                    module_name = f"{self.package_name}.{file.stem}"

                    # Load module using absolute path
                    spec = importlib.util.spec_from_file_location(
                        module_name, str(file)
                    )
                    if spec is None or spec.loader is None:
                        continue

                    module = importlib.util.module_from_spec(spec)
                    sys.modules[spec.name] = module
                    spec.loader.exec_module(module)

                    for name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, RuleTemplate)
                            and obj != RuleTemplate
                            and obj.__module__.startswith(self.package_name)
                        ):
                            try:
                                self.rules.append(obj)
                            except Exception:
                                continue

                except Exception:
                    continue

    def _execute_rules(self, config: dict) -> RulesValidationResults:
        results = RulesValidationResults()
        for rule_class in self.rules:
            try:
                # Execute the rule
                rule: RuleTemplate = rule_class()
                passed = rule.validate(config)
                if passed:
                    results.add_success(rule._rule)
                else:
                    results.add_failure(rule._rule, rule.errors())
            except NotImplementedError:
                # Rule not implemented yet
                results.add_not_implemented(rule._rule)
            except Exception as e:
                results.add_exception(rule._rule, e, f"{traceback.format_exc()}")
        return results
