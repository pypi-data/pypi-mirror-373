from typing import Dict
from langchain_chroma import Chroma
from maleo.types.base.dict import OptionalStringToStringDict, StringToStringDict
from maleo.types.base.integer import OptionalInteger
from maleo.types.base.string import ListOfStrings
from .enums import ICDType


class ICDCodeManager:
    """Service for working with ICD-9-CM and ICD-10 codes (unified)."""

    def __init__(self, vectorstore: Chroma, icd_type: ICDType):
        self.vectorstore = vectorstore
        self.icd_type = icd_type
        self._valid: OptionalStringToStringDict = None

    @property
    def valid(self) -> StringToStringDict:
        """
        Build dictionary of valid codes and descriptions.
        Works if metadata contains 'code'.
        """
        if self._valid is None:
            results = self.vectorstore.similarity_search(" ", k=10000)  # dummy query
            self._valid = {
                str(r.metadata["code"]): r.page_content
                for r in results
                if "code" in r.metadata
            }
        return self._valid

    def retrieve(
        self, terms: ListOfStrings, max_codes_per_term: OptionalInteger = None
    ) -> StringToStringDict:
        if max_codes_per_term is None:
            max_codes_per_term = 10 if self.icd_type == ICDType.ICD9 else 5

        return {
            result.metadata["code"]: result.page_content
            for term in terms
            for result in self.vectorstore.similarity_search(term, k=max_codes_per_term)
            if "code" in result.metadata
        }

    def validate(self, model_output: list[Dict]) -> list[Dict]:
        filtered_output = [
            entry
            for entry in model_output
            if entry["code"] in self.valid
            and self.valid[entry["code"]] == entry["description"]
        ]

        if filtered_output:
            return filtered_output

        if self.icd_type == ICDType.ICD9:
            return [
                {"code": "No Match", "description": "No valid ICD-9 procedure found"}
            ]
        else:
            return [
                {
                    "code": "No Match",
                    "description": "No valid ICD-10 found",
                    "reasoning": "No matching ICD-10 code found in database",
                }
            ]
