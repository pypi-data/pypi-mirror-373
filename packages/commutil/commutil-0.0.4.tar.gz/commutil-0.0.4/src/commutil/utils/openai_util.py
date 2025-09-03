import importlib
import os
import asyncio
from typing import Union, List, Dict, Any, Optional

from tqdm.asyncio import tqdm_asyncio
import time

# TODO fix this import issuse

try:
    import nest_asyncio
    nest_asyncio.apply()
except:
    pass


class OpenAIChat:
    def __init__(
            self,
            client=None,
            base_url=None,
            api_key=None,
            model_name="gpt-3.5-turbo",
            max_tokens=128,
            temperature=1,
            top_p=1,
            max_concurrency=20,
            retry_limit=10,
            initial_retry_delay=0.5,
    ):
        """
        Initialize the OpenAI Chat client for non-streaming completions.

        Args:
            client: Optional pre-configured OpenAI client
            base_url: API base URL
            api_key: OpenAI API key
            model_name: Model to use for completions
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            max_concurrency: Maximum concurrent requests
            retry_limit: Maximum number of retries per request
            initial_retry_delay: Initial delay between retries (exponential backoff)
            timeout: HTTP request timeout in seconds
        """
        self.openai = importlib.import_module('openai')
        self.tqdm = importlib.import_module('tqdm')

        self.api_key = api_key
        self.base_url = base_url

        self.client = client
        if self.client is None:
            if self.api_key is None:
                self.api_key = os.environ.get("OPENAI_API_KEY")
            if self.base_url is None:
                self.base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
            self.client = self.openai.AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.retry_limit = retry_limit
        self.initial_retry_delay = initial_retry_delay

    async def _request_with_retry(self, messages, request_id=None) -> Dict[str, Any]:
        sleep_time = self.initial_retry_delay
        errors = []

        async with self.semaphore:
            for attempt in range(self.retry_limit):
                try:
                    response = await self.client.chat.completions.create(
                        messages=messages,
                        model=self.model_name,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        top_p=self.top_p,
                        stream=False
                    )
                    return {"success": True, "response": response, "id": request_id}

                except Exception as e:
                    errors.append(str(e))
                    if attempt < self.retry_limit - 1:
                        if isinstance(e, self.openai.RateLimitError):
                            error_type = "Rate limit"
                            sleep_time = min(30, sleep_time * 2)
                        elif isinstance(e, self.openai.APITimeoutError):
                            error_type = "Timeout"
                            sleep_time = min(20, sleep_time * 1.5)
                        else:
                            error_type = "API"
                            sleep_time = min(10, sleep_time * 2)
                        print(f"[Retry {attempt + 1}/{self.retry_limit}] {error_type} error on request {request_id}: {e}")
                        await asyncio.sleep(sleep_time)
                    else:
                        return {"success": False, "errors": errors, "id": request_id}

            return {"success": False, "errors": errors, "id": request_id}

    async def dispatch_openai_requests(self, messages_list: List[List[Dict[str, str]]]) -> List[Dict[str, Any]]:
        tasks = []
        for i, messages in enumerate(messages_list):
            task = self._request_with_retry(messages, request_id=i)
            tasks.append(task)
        results = await tqdm_asyncio.gather(*tasks, desc="Processing API Requests")
        return results

    async def async_run(self, messages_list: List[List[Dict[str, str]]]) -> List[Optional[str]]:
        all_results = await self.dispatch_openai_requests(messages_list)
        preds = [None] * len(all_results)
        failed_requests = []

        for result in all_results:
            idx = result["id"]
            if result["success"]:
                preds[idx] = result["response"].choices[0].message.content
            else:
                failed_requests.append(idx)

        if failed_requests:
            print(f"Warning: {len(failed_requests)} requests failed: {failed_requests}")

        return preds


    def format(self, messages_list):
        # Convert input to a standard list of message lists
        if isinstance(messages_list, str):
            messages_list = [[{"role": "user", "content": messages_list}]]
        elif isinstance(messages_list, list) and all(isinstance(msg, str) for msg in messages_list):
            messages_list = [[{"role": "user", "content": msg}] for msg in messages_list]
        elif isinstance(messages_list, list) and all(isinstance(msg, dict) for msg in messages_list):
            messages_list = [messages_list]
        elif not (
                isinstance(messages_list, list) and
                all(isinstance(conv, list) and all(isinstance(msg, dict) for msg in conv) for conv in messages_list)
        ):
            raise ValueError("Invalid input format. Expected a string, list of strings, list of messages, or list of conversations.")

        return messages_list

    def generate(self, messages_list: Union[str, List[str], List[Dict[str, Any]], List[List[Dict[str, Any]]]]) -> List[str]:
        messages_list = self.format(messages_list)
        # return asyncio.run(self.async_run(messages_list))
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.async_run(messages_list))
        # Create a new event loop for this thread
        # loop = asyncio.get_event_loop()
        # return loop.run_until_complete(self.async_run(messages_list))

    def generate1(self, messages_list):
        sleep_time = self.initial_retry_delay
        self.client1 = self.openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        messages_list = self.format(messages_list)
        for attempt in range(self.retry_limit):
            try:
                response = self.client1.chat.completions.create(
                    messages=messages_list[0],
                    model=self.model_name,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    stream=False
                )
                return response.choices[0].message.content

            except Exception as e:
                if attempt < self.retry_limit - 1:
                    if isinstance(e, self.openai.RateLimitError):
                        error_type = "Rate limit"
                        sleep_time = min(30, sleep_time * 2)
                    elif isinstance(e, self.openai.APITimeoutError):
                        error_type = "Timeout"
                        sleep_time = min(20, sleep_time * 1.5)
                    else:
                        error_type = "API"
                        sleep_time = min(10, sleep_time * 2)
                    print(f"[Retry {attempt + 1}/{self.retry_limit}] {error_type}: {e}")
                    time.sleep(sleep_time)
                else:
                    return None