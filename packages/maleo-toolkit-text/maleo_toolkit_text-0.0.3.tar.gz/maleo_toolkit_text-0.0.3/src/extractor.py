import json
import re
from google import genai
from maleo.types.base.string import ListOfStrings


class TermsExtractorUtils:
    """Utility for extracting terms from free text using LLM."""

    def __init__(self, client: genai.Client, model_name: str):
        """
        Initializes the extractor with the GenAI client and model ID.

        Parameters
        ----------
        client : genai.Client
            Authenticated GenAI client instance.
        model_name : str
            Identifier of the generative model to use.
        """
        self.client = client
        self.model_name = model_name

    def extract_terms(self, text: str) -> ListOfStrings:
        """
        Extract medical terms from the given text.
        Returns a list of terms by parsing a JSON array from LLM output.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name, contents=text
            )

            if not response.text:
                raise ValueError("Model returned empty response")

            # Now response.text is guaranteed to be str
            json_match = re.search(r"\[(.*?)\]", response.text)
            if json_match:
                terms = json.loads(f"[{json_match.group(1)}]")
                if isinstance(terms, list):
                    return terms

            raise ValueError("No valid JSON array found in model output")

        except Exception as e:
            raise ValueError(f"Failed to extract terms: {e}")
