import asyncio
import json
import tempfile
from typing import Dict, List, Optional
from urllib.parse import urlparse

import playwright
import validators
import yaml
from haralyzer import HarParser
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field

from dtx.core import logging
from dtx_models.providers.http import HttpProvider


class FuzzingRequestModel(BaseModel):
    method: str
    url: str
    headers: Dict[str, str]
    body: Optional[str] = None
    response_status: Optional[int] = None
    response_status_text: Optional[str] = None
    response_headers: Optional[Dict[str, str]] = None
    response_body: Optional[str] = None
    response_content_type: Optional[str] = None


class HttpProviderWithEnvKeys(BaseModel):
    provider: HttpProvider
    env_keys: Optional[List[str]] = Field(default_factory=list)


class HumanAssistedWebCrawler:
    def __init__(
        self, headless=False, speed=300, browser_name="Chromium", fuzz_marker="[FUZZ]"
    ):
        self._headless = headless
        self._speed = speed
        self._browser_name = browser_name
        self._fuzz_marker = fuzz_marker

    def crawl(self, url, session_file_path, handle_request_fn=None):
        loop = asyncio.new_event_loop()
        task = loop.create_task(
            self.async_crawl(url, session_file_path, handle_request_fn)
        )
        loop.run_until_complete(task)

    def _handle_request(self, request):
        pass
        # logging.debug(f'>> {request.method} {request.url} \n')
        # if request.method in ["POST", "PUT"]:
        #     post_data = request.post_data
        # if post_data and self._fuzz_marker in post_data:
        #     print("Found request to be fuzzed: ", f'>> {request.method} {request.url} {post_data} \n')

    def on_web_socket(self, ws):
        logging.warning(f"""
                     Unsupported ##############\nApp is using Web Sockets. 
                     Hacktor does not support Web Sockets yet!!!\n
                     WebSocket opened on URL {ws.url}
                     ##############""")
        ws.send
        # print(f"WebSocket opened: {ws.url}")
        # ws.on("framesent", lambda payload: print("Frame sent:", payload))
        # ws.on("framereceived", lambda payload: print("Frame received:", payload))
        # ws.on("close", lambda payload: print("WebSocket closed"))

    async def async_crawl(self, url, session_file_path, handle_request_fn=None):
        if not validators.url(url):
            raise Exception(
                "The url provided is malformed. Exiting Crawling procedure."
            )
        async with async_playwright() as p:
            try:
                if self._browser_name == "Webkit":
                    browser_instance = p.webkit
                elif self._browser_name == "Firefox":
                    browser_instance = p.firefox
                else:
                    browser_instance = p.chromium
                if not self._headless:
                    browser = await browser_instance.launch(
                        headless=False, slow_mo=self._speed
                    )
                else:
                    browser = await browser_instance.launch(
                        headless=True, slow_mo=self._speed
                    )
                context = await browser.new_context(
                    record_har_path=session_file_path, ignore_https_errors=True
                )

                context.set_default_timeout(0)
                page = await context.new_page()
                handle_request_fn = handle_request_fn or self._handle_request
                page.on("request", lambda request: handle_request_fn(request))
                page.on(
                    "response",
                    lambda response: logging.debug(
                        f"<< {response.status} {response.url} \n"
                    ),
                )
                page.on("close", lambda: logging.debug("Browser Closed Successfully"))
                # page.on("websocket", self.on_web_socket)
                await page.goto(url)
                await page.title()
                await page.wait_for_selector('text="None"')
            except playwright._impl._errors.TargetClosedError:
                pass
            except Exception as e:
                logging.exception("Page got closed manually or got crashed %s", e)
            finally:
                if page:
                    await page.close()
                await context.close()
                await browser.close()
                logging.debug(
                    f"The complete networking details can be found in {session_file_path}"
                )


class FuzzingRequestExtractor:
    def __init__(
        self,
        url,
        fuzz_marker="[FUZZ]",
        headless=False,
        speed=300,
        browser_name="Chromium",
    ):
        self.url = url
        self.fuzz_marker = fuzz_marker
        self.headless = headless
        self.speed = speed
        self.browser_name = browser_name

    def extract_fuzzing_requests(self):
        with tempfile.NamedTemporaryFile(suffix=".har", delete=False) as temp_har:
            session_file_path = temp_har.name

        # Start crawling and record to HAR file
        crawler = HumanAssistedWebCrawler(
            headless=self.headless,
            speed=self.speed,
            browser_name=self.browser_name,
            fuzz_marker=self.fuzz_marker,
        )

        logging.info(
            "Launching crawler to capture session with potential fuzzing markers..."
        )
        crawler.crawl(self.url, session_file_path)

        # Parse HAR and extract relevant requests
        fuzz_requests = []
        with open(session_file_path, "r") as f:
            har_data = json.load(f)
            har_parser = HarParser(har_data)

        for page in har_parser.pages:
            for entry in page.entries:
                request = entry.request
                response = entry.response
                post_data = request.get("postData", {}).get("text", "")
                if self.fuzz_marker in post_data:
                    logging.info(f"Found FUZZ marker in request to {request['url']}")
                    model = FuzzingRequestModel(
                        method=request["method"],
                        url=request["url"],
                        headers={
                            h["name"]: h["value"] for h in request.get("headers", [])
                        },
                        body=post_data or None,
                        response_status=response.get("status"),
                        response_status_text=response.get("statusText"),
                        response_headers={
                            h["name"]: h["value"] for h in response.get("headers", [])
                        },
                        response_body=response.get("content", {}).get("text"),
                        response_content_type=response.get("content", {}).get(
                            "mimeType"
                        ),
                    )
                    fuzz_requests.append(model)

        return fuzz_requests



class FuzzingRequestToProviderConverter:
    def __init__(self, fuzz_markers: List[str], generic: bool = False):
        """
        :param fuzz_markers: markers in the request body to swap for {{prompt}}
        :param generic: if True, emit ENV placeholders (ENV_HOST, ENV_API_KEY, ENV_COOKIE)
                        and collect env_keys; otherwise, emit the concrete request.
        """
        self.fuzz_markers = fuzz_markers
        self.generic = generic

    def _set_or_update_header(self, headers: Dict[str, str], name: str, value: str):
        # Preserve original casing if present
        for k in list(headers.keys()):
            if k.lower() == name.lower():
                headers[k] = value
                return
        headers[name] = value

    def _has_header(self, headers: Dict[str, str], name: str) -> bool:
        return any(k.lower() == name.lower() for k in headers.keys())

    def convert(self, req: FuzzingRequestModel) -> HttpProviderWithEnvKeys:
        parsed = urlparse(req.url)
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"
        host = parsed.netloc
        scheme = parsed.scheme
        use_https = scheme == "https"

        # Work on a copy so we don't mutate the original headers
        headers: Dict[str, str] = dict(req.headers or {})
        env_keys: List[str] = []

        # ----- Body handling & fuzz replacement -----
        body = req.body or ""
        for marker in self.fuzz_markers:
            if marker in body:
                body = body.replace(marker, "{{prompt}}")

        # ----- Host header handling -----
        request_line = f"{req.method} {path} HTTP/1.1"
        header_lines: List[str] = []

        if self.generic:
            # Canonical ENV host
            header_lines.append("Host: {{ENV_HOST}}")
            env_keys.append("ENV_HOST")
            # If a Host was present in captured headers, skip it (we already added ENV one)
            headers = {k: v for k, v in headers.items() if k.lower() != "host"}
        else:
            # Keep/ensure concrete host
            if not self._has_header(headers, "Host") and host:
                header_lines.append(f"Host: {host}")

        # ----- Sensitive headers env-ification (generic only) -----
        for k, v in list(headers.items()):
            lower = k.lower()
            if self.generic:
                if lower == "authorization" and "bearer" in v.lower():
                    v = "Bearer {{ENV_API_KEY}}"
                    if "ENV_API_KEY" not in env_keys:
                        env_keys.append("ENV_API_KEY")
                elif lower == "cookie":
                    v = "{{ENV_COOKIE}}"
                    if "ENV_COOKIE" not in env_keys:
                        env_keys.append("ENV_COOKIE")
                elif lower == "host":
                    # skip; already emitted canonical Host above
                    continue
            header_lines.append(f"{k}: {v}")

        # ----- Content-Length (update or add when we have a body) -----
        has_body = bool(body)
        method_has_body = req.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}
        if has_body and method_has_body:
            cl_value = str(len(body.encode("utf-8")))
            if any(h.lower().startswith("content-length:") for h in header_lines) or self._has_header(headers, "Content-Length"):
                # update: rebuild header_lines with corrected CL
                new_header_lines = []
                cl_set = False
                for line in header_lines:
                    if line.lower().startswith("content-length:"):
                        new_header_lines.append(f"Content-Length: {cl_value}")
                        cl_set = True
                    else:
                        new_header_lines.append(line)
                header_lines = new_header_lines
                if not cl_set:
                    header_lines.append(f"Content-Length: {cl_value}")
            else:
                header_lines.append(f"Content-Length: {cl_value}")

        # ----- Build raw request string (CRLF per RFC) -----
        headers_block = "\r\n".join(header_lines) if header_lines else ""
        if headers_block:
            raw_request_str = f"{request_line}\r\n{headers_block}\r\n\r\n{body}"
        else:
            raw_request_str = f"{request_line}\r\n\r\n{body}"

        # ----- Determine transform_response -----
        transform_response = "text"
        try:
            parsed_json = json.loads(req.response_body or "")
            transform_response = "json"
            if isinstance(parsed_json, dict) and isinstance(parsed_json.get("choices"), list):
                transform_response = "json['choices'][0]['message']['content']"
        except Exception:
            transform_response = "text"

        provider_config = {
            "id": "http",
            "config": {
                "raw_request": raw_request_str,
                "use_https": use_https,
                "max_retries": 3,
                "validate_response": "status == 200",
                "transform_response": transform_response,
                "example_response": req.response_body.strip() if req.response_body else None,
            },
        }

        provider = HttpProvider(**provider_config)
        return HttpProviderWithEnvKeys(provider=provider, env_keys=env_keys)


# Example Usage
if __name__ == "__main__":
    # Custom YAML representer to use '|' block style for multiline strings
    class LiteralString(str):
        pass

    def literal_string_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")

    yaml.add_representer(
        LiteralString, literal_string_representer, Dumper=yaml.SafeDumper
    )

    logging.basicConfig(level=logging.INFO)
    url = "https://kissan.ai/chat"
    extractor = FuzzingRequestExtractor(url)
    fuzz_requests = extractor.extract_fuzzing_requests()

    all_providers = []
    env_vars = []  # Always include ENV_HOST
    converter = FuzzingRequestToProviderConverter(["[FUZZ]"])

    for req in fuzz_requests:
        provider = converter.convert(req)
        raw = provider.config.raw_request
        provider.config.raw_request = LiteralString(raw)
        all_providers.append(provider.provider.model_dump())
        if provider.env_keys:
            env_vars.extend(provider.env_keys)

    output = {
        "providers": all_providers,
        "environments": [
            {"vars": {env: f"{{{{env.{env}}}}}"}} for env in list(set(env_vars))
        ],
    }

    print(yaml.safe_dump(output, sort_keys=False))
