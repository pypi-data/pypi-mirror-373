from typing import List, Optional, Union
import pandas as pd
import asyncio
from tqdm.asyncio import tqdm_asyncio
from sempy.fabric.exceptions import FabricHTTPException
from sempy.fabric._client._rest_client import CognitiveServiceRestClient
from sempy.fabric._client._rest_client_async import CognitiveServiceAsyncRestClient


def _parse_translation_response(text: Union[str, List[str]], response: Union[dict, List[dict]], to_lang: List[str]):
    """
    Parse the response from the translation API and return a pandas dataframe

    Parameters
    ----------
    text: str or list
        The text to be translated
    response: dict or list
        The response from the translation API
    to_lang: list
        The target languages
    """
    if isinstance(text, str):
        text = [text]

    if isinstance(response, dict):
        response = [response]

    translated_langs = []
    column_names = ['text'] + to_lang

    # Extract values under "translations" and map them to respective columns
    for index, item in enumerate(response):
        new_data = [text[index]] + [item['translations'][lang_index]['text'] for lang_index in range(len(to_lang))]
        translated_langs.append(pd.DataFrame([new_data], columns=column_names))
    translated_langs_pd = pd.concat(translated_langs, ignore_index=True)

    return translated_langs_pd


def _slice_list(texts: List[str], languages_num: int, upperbound_elements: int = 1000, upperbound_chars: int = 50000) -> List[List[str]]:
    """
    Slice the list of texts into smaller chunks. (`Cognitive Service Documentation <https://learn.microsoft.com/en-us/azure/ai-services/Translator/service-limits>`_).

    Parameters
    ----------
    texts: list
        The list of texts to be translated
    languages_num: int
        The number of target languages
    upperbound_elements: int
        The maximum number of elements in each chunk
    upperbound_chars: int
        The maximum number of characters in each chunk
    """
    if languages_num > 0:
        chunks = []
        current_chunk: List[str] = []
        current_length = 0

        max_elements = upperbound_elements // languages_num
        max_chars = upperbound_chars // languages_num

        for text in texts:
            if len(current_chunk) < max_elements and current_length + len(text) <= max_chars:
                current_chunk.append(text)
                current_length += len(text)
            else:
                chunks.append(current_chunk)
                current_chunk = [text]
                current_length = len(text)

        if current_chunk:
            chunks.append(current_chunk)

        return chunks
    else:
        raise ValueError("You need to specify target languages")


class _CognitiveServiceAsyncRestAPI():
    """
    A class to handle Cognitive Service REST API calls asynchronously
    """

    async def translate_text_async(self, texts: Union[str, List[str]], to_lang: List[str], from_lang: Optional[str] = None):

        async def _fetch_translation(client, path, payload):
            response = await client.post(path, json=payload)
            return await response.json()

        async with CognitiveServiceAsyncRestClient() as client:
            path = client._get_default_base_url() + "texttranslation/translate?api-version=3.0"

            for lang in to_lang:
                path += f"&to={lang}"
            if from_lang is not None:
                path += f"&from={from_lang}"

            if isinstance(texts, str):
                texts = [texts]

            # Chunk the text into smaller parts
            chunks = _slice_list(texts, len(to_lang))

            tasks = []
            for chunk in chunks:
                payload = [{"Text": t} for t in chunk]
                tasks.append(_fetch_translation(client, path, payload))
            responses = await tqdm_asyncio.gather(*tasks)

            return [item for subList in responses for item in subList]

    def translate_text(self, texts: Union[str, List[str]], to_lang: List[str], from_lang: Optional[str] = None):
        from sempy.fabric._environment import _on_fabric

        # Fabric already has an event loop running, so we need to use nest_asyncio to avoid RuntimeError
        if _on_fabric():
            import nest_asyncio
            nest_asyncio.apply()

        loop = asyncio.get_event_loop()
        responses = loop.run_until_complete(self.translate_text_async(texts, to_lang, from_lang))
        return _parse_translation_response(texts, responses, to_lang)


class _CognitiveServiceRestAPI():
    """
    A class to handle Cognitive Service REST API calls
    """
    _rest_client: CognitiveServiceRestClient

    def __init__(self):
        self._rest_client = CognitiveServiceRestClient()

    def fetch_language_map(self):
        path = "https://api.cognitive.microsofttranslator.com/languages?api-version=3.0"
        response = self._rest_client.get(path)
        if response.status_code == 200:
            return response.json()
        else:
            raise FabricHTTPException(response)
