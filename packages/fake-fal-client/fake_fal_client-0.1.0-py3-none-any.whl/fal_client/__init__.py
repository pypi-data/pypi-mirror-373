# file: fal_client.py
"""fal_client

A tiny, dependency-free fake of the fal.ai Python SDK.

Usage
-----
Drop this file as ``fal_client.py`` somewhere on your application's
``PYTHONPATH``. Your existing code (e.g., a ``FalAIRunner``) can import it as
``import fal_client`` with **no code changes**. It exposes ``subscribe``, the
``Queued``/``InProgress``/``Completed`` update classes, and a few convenience
functions compatible with common fal.ai usage patterns.

Environment toggles
-------------------
- ``FAL_FAKE_LATENCY`` (float seconds; default ~0.1): adds tiny sleeps between
  updates to better mimic network/compute latency.
- ``FAL_FAKE_ERROR_RATE`` (0–1; default 0): randomly raises a ``RuntimeError``
  to simulate transient failures.
- ``FAL_FAKE_LOGS`` (bool; default true): when false, ``subscribe`` still emits
  an ``InProgress`` update but with ``logs=[]``.

This module is reload-safe: it keeps no mutable global state that would break on
``importlib.reload(fal_client)``.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple 

import asyncio
import os
import random
import time
import uuid


# ----------------------------
# Public update event classes
# ----------------------------

@dataclass(frozen=True)
class Queued:
    """Emitted when a request is queued.

    Attributes
    ----------
    position: int
        The 1-indexed position in queue (fixed to 1 for this fake).
    """

    position: int


@dataclass(frozen=True)
class InProgress:
    """Emitted while a request is running.

    *Why*: Carries human-ish log lines that some parsers consume.

    Attributes
    ----------
    logs: list | dict
        Either a list of log lines/objects or a single JSON-like dict.
    """

    logs: Any  # list | dict


@dataclass(frozen=True)
class Completed:
    """Emitted when a request completes successfully."""


# ----------------------------
# Helpers (kept module-local)
# ----------------------------

_SIZE_MAP: Mapping[str, Tuple[int, int]] = {
    # Sensible, common resolutions; ratios match the keys.
    "square_hd": (1024, 1024),
    "portrait_4_3": (960, 1280),
    "portrait_16_9": (1080, 1920),
    "landscape_4_3": (1280, 960),
    "landscape_16_9": (1920, 1080),
}

_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-00000000f4f4")  # stable, arbitrary


def _bool_env(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _env_latency() -> float:
    try:
        return float(os.getenv("FAL_FAKE_LATENCY", "0.1"))
    except ValueError:
        return 0.1


def _env_error_rate() -> float:
    try:
        v = float(os.getenv("FAL_FAKE_ERROR_RATE", "0"))
        return min(1.0, max(0.0, v))
    except ValueError:
        return 0.0


def _env_logs() -> bool:
    return _bool_env("FAL_FAKE_LOGS", True)


def _pick_size(key: Optional[str]) -> Tuple[int, int]:
    if key and key in _SIZE_MAP:
        return _SIZE_MAP[key]
    return _SIZE_MAP["square_hd"]


def _deterministic_uuid(name: str) -> uuid.UUID:
    # uuid5 ensures stable IDs given the same name; avoids mutable global state.
    return uuid.uuid5(_NAMESPACE, name)


def _rand() -> random.Random:
    # SystemRandom avoids seeding global RNG; safer across reloads.
    return random.SystemRandom()


def _maybe_fail() -> None:
    if _rand().random() < _env_error_rate():
        # *Why*: opt-in failure mode to exercise caller retries.
        raise RuntimeError("fal_client: simulated transient error (FAL_FAKE_ERROR_RATE)")


# ----------------------------
# Public API (fal-like)
# ----------------------------

def upload_file(path: str | os.PathLike[str]) -> str:
    """Return a fal-like media URL for an uploaded file.

    *Why*: Many apps only need a well-shaped URL, not a real upload.
    """
    base = Path(path).name or "file"
    # return f"https://v3.fal.media/files/mock/{uuid.uuid4()}/{base}"
    return "https://fillthis.io/i/800x600/ddc5a2/523634.webp"



def subscribe(
    model_id: str,
    *,
    arguments: Optional[Mapping[str, Any]] = None,
    with_logs: bool = False,
    on_queue_update: Optional[Callable[[Queued | InProgress | Completed], None]] = None,
    **_: Any,
) -> Dict[str, Any]:
    """Synchronous, fal-like subscription flow.

    Emits ``Queued(1)``, then ``InProgress`` with mixed logs, then ``Completed``.
    Returns a FLUX.1 [dev]-shaped result dict.
    """
    _maybe_fail()

    args = dict(arguments or {})
    prompt: str = str(args.get("prompt", ""))
    num_images: int = int(args.get("num_images", 1)) or 1
    size_key: Optional[str] = args.get("image_size")
    width, height = _pick_size(size_key)

    # Choose/propagate a seed; ensure int and within 32-bit range.
    seed: Optional[int]
    if "seed" in args and args["seed"] is not None:
        seed = int(args["seed"])
    else:
        seed = _rand().randint(0, 2**31 - 1)

    started_wall = time.time()
    t0 = time.perf_counter()

    latency = max(0.0, _env_latency())

    if on_queue_update is not None:
        on_queue_update(Queued(1))
        if latency:
            time.sleep(latency)

        if with_logs and _env_logs():
            logs_obj: List[Any] = [
                "30/30 [00:30<00:00, 1.02s/it]",
                "100%|█████|",
                {"detail": "step 3 of 10"},
                "HTTP/1.1 200 OK",
            ]
        else:
            logs_obj = []

        on_queue_update(InProgress(logs=logs_obj))
        if latency:
            time.sleep(latency)

        on_queue_update(Completed())

    # Deterministic image IDs when seed is provided.
    images: List[Dict[str, Any]] = []
    for i in range(num_images):
        if seed is not None:
            u = _deterministic_uuid(f"{model_id}:{prompt}:{seed}:{i}:{width}x{height}")
        else:
            u = uuid.uuid4() 

        image_url = "https://fillthis.io/i/800x600/ddc5a2/523634.webp"

        images.append(
            {
                "url": image_url,
                "width": width,
                "height": height,
                "content_type": "image/jpeg",
            }
        ) 
        # logger.debug("Generated image URL: %s", images[0]["url"])


    inference = time.perf_counter() - t0
    total = inference  # identical in this simple sync flow

    result: Dict[str, Any] = {
        "images": images,
        "timings": {
            "started": float(started_wall),
            "inference": float(inference),
            "total": float(total),
        },
        "seed": int(seed if seed is not None else 0),
        "has_nsfw_concepts": [False for _ in range(num_images)],
        "prompt": prompt, 
        "first_image_url": images[0]["url"]  # Ensure this line is added.

    }
    return result


def run(model_id: str, *, arguments: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
    """fal-like convenience wrapper that returns the final result."""
    return subscribe(model_id, arguments=arguments, with_logs=False, on_queue_update=None, **kwargs)


async def run_async(
    model_id: str,
    *,
    arguments: Optional[Mapping[str, Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Async variant of ``run`` using a background thread."""
    return await asyncio.to_thread(run, model_id, arguments=arguments, **kwargs)


def submit(model_id: str, *, arguments: Optional[Mapping[str, Any]] = None, **_: Any) -> Dict[str, Any]:
    """fal-like submit returning a request id only.

    *Why*: Some clients want a request handle before polling.
    """
    # Encode essentials into the name for stable IDs without globals.
    args = dict(arguments or {})
    name = f"{model_id}:{args.get('prompt','')}:{args.get('seed','')}:{args.get('image_size','')}:{args.get('num_images',1)}"
    rid = str(_deterministic_uuid(name))
    return {"request_id": rid}


def status(request_id: str, **_: Any) -> Dict[str, Any]:
    """Minimal status endpoint.

    Always returns a completed status for simplicity.
    """
    return {"request_id": request_id, "status": "COMPLETED"}


def result(request_id: str, **_: Any) -> Dict[str, Any]:
    """Return a stable, request-id-derived result.

    *Why*: Avoids keeping per-request state across reloads.
    """
    # Derive deterministic yet plausible values from the request id.
    width, height = _pick_size("square_hd")
    img_id = _deterministic_uuid(f"res:{request_id}")
    started_wall = time.time()
    res = {
        "images": [
            {
                "url": "https://fillthis.io/i/800x600/ddc5a2/523634.webp",
                "width": width,
                "height": height,
                "content_type": "image/jpeg",
            }
        ],
        "timings": {"started": float(started_wall), "inference": 0.0, "total": 0.0},
        "seed": 0,
        "has_nsfw_concepts": [False],
        "prompt": "",
    }
    return res


__all__ = [
    "Queued",
    "InProgress",
    "Completed",
    "subscribe",
    "upload_file",
    # convenience exports
    "run",
    "run_async",
    "submit",
    "status",
    "result",
]
