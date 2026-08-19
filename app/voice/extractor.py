"""
Transcript -> form field extraction.

`FieldExtractor` is the abstraction. `OpenAIFieldExtractor` is today's
implementation, calling the OpenAI API with the form's field definitions
and asking for a strict JSON mapping back. A future rule-based or
local-LLM implementation is a new class against the same interface —
VoiceService never needs to know which one is wired in.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.exceptions import ExtractionError
# from app.forms.models import Field, FieldType


@dataclass(frozen=True)
class ExtractedValue:
    field_id: str
    value: str
    confidence: float  # 0.0-1.0, model's self-reported confidence


class FieldExtractor(ABC):
    """Abstract contract: map free-text transcript onto a form's fields."""

    @abstractmethod
    def extract(self, transcript: str, schema: list[dict], tot_quest: int) -> list[dict]: ...


class GroqOpenAIFieldExtractor(FieldExtractor):
    """Uses an OpenAI GPT to extract structured field values."""

    def __init__(self, 
                 api_key: str, 
                 model: str = "openai/gpt-oss-20b") -> None:
        self._api_key = api_key
        self._model = model
        self._client = None                 # lazy-loaded

    def _get_client(self):
        if self._client is None:
            from groq import Groq  # imported lazily: avoid import cost when unused

            self._client = Groq(api_key=self._api_key)
        return self._client

    def extract(self, transcript: str, schema: list[dict], tot_quest: int) -> list[dict]:
        if not schema:
            return []
        
        ## Making a list of all questions in the Survey
        questions = []
        for page in schema:
            for pg_qt in page['elements']:
                pg_qt['answer'] = ""
                questions.extend([pg_qt])
                
        ## Now we can construct a LLM Prompt including a System Prompt and a User Prompt
        ## The User Prompt will carry the Form Schema and Trancribed Text, And System Prompt
        ## will carry instructions to fill the answer field based on rules & provided transcribed text.
        
        system_prompt = (
            "Extract information from a spoken transcript for a structured form. "
            "Given a transcript and a list of form questions (each with a name, type, title, answer etc.), "
            "fill the 'answer' field of provided JSON array and return that ONLY. "
            "For questions where a 'choice' must be made from a given options in another field of that "
            "question. Value of 'answer' field MUST be exactly one of the given options, or an empty string "
            "if no confident match exists. For 'number' fields, value must be numeric text only. "
            "Return no preamble, no markdown fences — JSON array ONLY."
        )
        user_prompt = json.dumps({"transcript": transcript, "form_question": questions})

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
            )
            ## Get the Textual result part from reponse
            raw_content = response.choices[0].message.content or "[]"
            
            ## Clean the Textual response and convert into JSON
            parsed = json.loads(self._strip_code_fences(raw_content, str(questions)))
            
        except Exception as exc:  # noqa: BLE001 — re-raised as a domain error below
            raise ExtractionError(f"Failed to extract fields from transcript: {exc}") from exc

        ## CASE 1: when transcribed text carry no useful information; highly likely that 
        ##         returned json is just a LIST of dictionaries. Hence return that list as 
        ##         LLM extracted answers for questions.
        if type(parsed) == list:
            return parsed

        ## CASE 2: when transcribed text carry useful information; highly likely that
        ##         returned json could be a DICTIONARY with more than one key. Hence return
        ##         only that key's value which is a LIST.
        elif len(parsed) > 1:     
            for item in parsed.values():
                if type(item) == list:
                    results = item
                    return results
            else:
                return [{
                    "type": "text",
                    "name": "emptyquestion",
                    "title": "",
                    "answer": "",
                    }]
                
        elif type(parsed.values()[0]) == list:
            results = parsed.values()[0]
            return results



    def _strip_code_fences(self, text: str, user_questions: str) -> str:
        """Defensive cleanup in case the model wraps JSON in ```json ... ``` anyway."""
        cleaned = text.strip()
        if len(cleaned) - cleaned[::-1].find("```") - cleaned.find("```") >= len(user_questions):
            cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        
        return cleaned.strip()
