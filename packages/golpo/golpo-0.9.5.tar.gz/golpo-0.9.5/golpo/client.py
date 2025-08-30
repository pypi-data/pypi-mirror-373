import concurrent.futures
import mimetypes
import time
from pathlib import Path
from typing import Iterable, Union, List, Optional
import re

import requests


class Golpo:
    """Python SDK for Golpo with transparent, parallel uploads.

    • Local file paths are uploaded to S3 via `/upload-url` (done in parallel).
    • Already‑hosted resources (strings that look like URLs) are passed through.
    • The backend receives every document as an **upload_urls** form field so it
      can fetch them internally.  This avoids the ALB 1‑MB limit.
    • The call blocks until the podcast is finished and returns its final URL.
    """

    _URL_RE = re.compile(r"^(https?|s3)://", re.I)

    def __init__(self, api_key: str, base_url: str = "https://api.golpoai.com") -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {"x-api-key": api_key}

    # ------------------------------------------------------------------
    # internal helper: presign → PUT → return S3 URL
    # ------------------------------------------------------------------
    def _upload_to_s3(self, path: Path) -> str:
        presign = requests.post(
            f"{self.base_url}/upload-url",
            headers=self.headers,
            data={"filename": path.name},
            timeout=30,
        )
        presign.raise_for_status()
        info = presign.json()  # {'url': ..., 'key': ...}

        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        with path.open("rb") as fh:
            put = requests.put(info["url"], data=fh, headers={"Content-Type": ctype})
        put.raise_for_status()
        return info["url"].split("?", 1)[0]

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def create_podcast(
        self,
        prompt: str = None,
        uploads: Optional[Union[str, Path, Iterable[Union[str, Path]]]] = None,
        *,
        add_music: bool = False,
        voice_instructions: Optional[str] = None,
        personality_1: Optional[str] = None,
        personality_2: Optional[str] = None,
        do_research: bool = False,
        tts_model: str = "accurate",
        language: Optional[str] = None,
        style: Optional[str] = "conversational", # either conversational, solo-male or solo-female
        bg_music: Optional[str] = None, # either None, jazz, lofi or dramatic. 
        poll_interval: int = 2,
        max_workers: int = 8,
        output_volume: float = 1.0
    ) -> str:
        """Generate a podcast and return its final URL."""
        if not prompt and not new_script:
            raise Error("Prompt is mandatory if new_script is not provided")
        # --------- basic form fields ----------------------------------
        fields: List[tuple[str, str]] = [
            ("prompt", prompt),
            ("add_music", str(add_music).lower()),
            ("do_research", str(do_research).lower()),
            ("tts_model", tts_model),
            ("style", style)
        ]
        if voice_instructions:
            fields.append(("voice_instructions", voice_instructions))
        if personality_1:
            fields.append(("personality_1", personality_1))
        if personality_2:
            fields.append(("personality_2", personality_2))
        if language:
            fields.append(("language", language))
        if bg_music:
            fields.append(("bg_music", bg_music))
        if output_volume:
            fields.append(("output_volume", output_volume))


        # --------- gather documents -----------------------------------
        if uploads:
            if isinstance(uploads, (str, Path)):
                uploads = [uploads]

            local_paths: List[Path] = []
            passthrough_urls: List[str] = []

            for item in uploads:  # type: ignore[not-an-iterable]
                # treat str & Path uniformly
                if isinstance(item, Path):
                    path_obj = item.expanduser()
                else:
                    # trim any accidental angle‑brackets or whitespace
                    item_str = str(item).strip().lstrip("<").rstrip(">")
                    if self._URL_RE.match(item_str):
                        passthrough_urls.append(item_str)
                        continue
                    path_obj = Path(item_str).expanduser()

                if path_obj.exists():
                    local_paths.append(path_obj)
                else:
                    raise FileNotFoundError(path_obj)

            # upload local files in parallel
            if local_paths:
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=min(max_workers, len(local_paths))
                ) as pool:
                    futs = [pool.submit(self._upload_to_s3, p) for p in local_paths]
                    for fut in concurrent.futures.as_completed(futs):
                        passthrough_urls.append(fut.result())

            # add to multipart body
            fields += [("upload_urls", url) for url in passthrough_urls]

        # --------- POST /generate ------------------------------------
        gen = requests.post(
            f"{self.base_url}/generate",
            headers=self.headers,
            data=fields,  # list[tuple] keeps order & repeats
            timeout=60,
        )
        gen.raise_for_status()
        job_id = gen.json()["job_id"]

        # --------- poll until finished -------------------------------
        while True:
            status = requests.get(
                f"{self.base_url}/status/{job_id}", headers=self.headers, timeout=30
            ).json()
            if status["status"] == "completed":
                return status["podcast_url"], status["podcast_script"]
            time.sleep(poll_interval)

    def create_video(
        self,
        prompt: str,
        uploads: Optional[Union[str, Path, Iterable[Union[str, Path]]]] = None,
        *,
        voice_instructions: Optional[str] = None,
        personality_1: Optional[str] = None,
        do_research: bool = False,
        tts_model: str = "accurate",
        language: Optional[str] = None,
        style: Optional[str] = "solo-female", # either solo-male or solo-female
        bg_music: Optional[str] = "engaging", 
        bg_volume = 1.4,
        video_type: Optional[str] = "long", 
        include_watermark = True, 
        new_script: Optional[str] = None, 
        just_return_script: bool = False, 
        logo = None, 
        timing="1", 
        poll_interval: int = 2,
        max_workers: int = 8,
        output_volume: float = 1.0, 
        use_color=False
    ) -> str:
        """Generate a podcast and return its final URL."""
        
        # Validate timing parameter
        try:
            timing_float = float(timing)
            if timing_float < 0.25:
                raise ValueError(f"Timing parameter must be 0.25 or above, got {timing_float}")
        except (ValueError, TypeError) as e:
            if "could not convert" in str(e):
                raise ValueError(f"Timing parameter must be a valid number, got {timing}")
            raise

        # --------- basic form fields ----------------------------------
        fields: List[tuple[str, str]] = [
            ("prompt", prompt),
            ("do_research", str(do_research).lower()),
            ("tts_model", tts_model),
            ("bg_volume", str(bg_volume)),
            ("style", style)
        ]
        if language:
            fields.append(("language", language))
        if voice_instructions:
            fields.append(("voice_instructions", voice_instructions))
        if personality_1:
            fields.append(("personality_1", personality_1))
        if use_color:
            fields.append(("use_color", use_color))      
        if bg_music:
            fields.append(("bg_music", bg_music))
        if timing:
            fields.append(("timing", timing))
        if new_script:
            fields.append(("new_script", new_script))
        if just_return_script:
            fields.append(("just_return_script", just_return_script))
        if output_volume:
            fields.append(("output_volume", output_volume))

        if video_type:
            fields.append(("video_type", video_type))
        else:
            fields.append(("video_type", "long"))
        
        if bg_volume:
            fields.append(("bg_volume", bg_volume))
        
        if logo:
            logo_str = str(logo).strip().lstrip("<").rstrip(">")
            if not self._URL_RE.match(logo_str):
                logo_url = self._upload_to_s3(Path(logo_str).expanduser())
            else:
                logo_url = logo_str
            include_watermark=True
            fields.append(("logo", logo_url))
        fields.append(("include_watermark", str(include_watermark).lower()))
        # --------- gather documents -----------------------------------
        if uploads:
            if isinstance(uploads, (str, Path)):
                uploads = [uploads]

            local_paths: List[Path] = []
            passthrough_urls: List[str] = []

            for item in uploads:  # type: ignore[not-an-iterable]
                # treat str & Path uniformly
                if isinstance(item, Path):
                    path_obj = item.expanduser()
                else:
                    # trim any accidental angle‑brackets or whitespace
                    item_str = str(item).strip().lstrip("<").rstrip(">")
                    if self._URL_RE.match(item_str):
                        passthrough_urls.append(item_str)
                        continue
                    path_obj = Path(item_str).expanduser()

                if path_obj.exists():
                    local_paths.append(path_obj)
                else:
                    raise FileNotFoundError(path_obj)

            # upload local files in parallel
            if local_paths:
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=min(max_workers, len(local_paths))
                ) as pool:
                    futs = [pool.submit(self._upload_to_s3, p) for p in local_paths]
                    for fut in concurrent.futures.as_completed(futs):
                        passthrough_urls.append(fut.result())

            # add to multipart body
            fields += [("upload_urls", url) for url in passthrough_urls]

        # --------- POST /generate ------------------------------------
        gen = requests.post(
            f"{self.base_url}/generate",
            headers=self.headers,
            data=fields,  # list[tuple] keeps order & repeats
            timeout=60,
        )
        gen.raise_for_status()
        job_id = gen.json()["job_id"]

        # --------- poll until finished -------------------------------
        while True:
            response = requests.get(
                f"{self.base_url}/status/{job_id}", headers=self.headers, timeout=30
            )
            try:
                response.raise_for_status()
                status = response.json()
            except requests.exceptions.HTTPError:
                time.sleep(poll_interval)
                continue
            except ValueError:  # includes JSONDecodeError
                time.sleep(poll_interval)
                continue
            
            if status["status"] == "completed":
                return status["podcast_url"], status["podcast_script"]
            time.sleep(poll_interval)
