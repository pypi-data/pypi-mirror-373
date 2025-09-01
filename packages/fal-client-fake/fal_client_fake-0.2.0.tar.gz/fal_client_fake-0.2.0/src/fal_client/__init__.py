# """fal_client

# A tiny, dependency-free fake of the fal.ai Python SDK.

# This version is *type-aware*:
# - If the model is **image** it returns the original image-shaped payload and also
#   adds: `kind="image"` and a shorthand `url` (same as `first_image_url`).
# - If the model is **text** it returns: {"kind":"text","text": "...", "timings":..., "prompt":...}
# - If the model is **video** it returns: {"kind":"video","video_url":"...", "timings":..., "prompt":...}

# How the kind is chosen
# ----------------------
# - Prefer `arguments["type"]` ∈ {"image","text","video"} (case-insensitive).
# - Otherwise infer from `model_id` string:
#   - contains any of {"video","vid","gen-2","sora"} → "video"
#   - contains any of {"text","chat","qa","llama","gpt"} → "text"
#   - else → "image" (default)

# Environment toggles
# -------------------
# - FAL_FAKE_LATENCY (float seconds; default ~0.1)
# - FAL_FAKE_ERROR_RATE (0–1; default 0)
# - FAL_FAKE_LOGS (bool; default true)

# Reload-safe: no mutable global state that breaks on importlib.reload(fal_client).
# """
# from __future__ import annotations

# from dataclasses import dataclass
# from pathlib import Path
# from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple
# import asyncio
# import os
# import random
# import time
# import uuid


# # ----------------------------
# # Public update event classes
# # ----------------------------

# @dataclass(frozen=True)
# class Queued:
#     """Emitted when a request is queued.

#     Attributes
#     ----------
#     position: int
#         The 1-indexed position in queue (fixed to 1 for this fake).
#     """
#     position: int


# @dataclass(frozen=True)
# class InProgress:
#     """Emitted while a request is running.

#     Attributes
#     ----------
#     logs: list | dict
#         Either a list of log lines/objects or a single JSON-like dict.
#     """
#     logs: Any  # list | dict


# @dataclass(frozen=True)
# class Completed:
#     """Emitted when a request completes successfully."""


# # ----------------------------
# # Helpers (kept module-local)
# # ----------------------------

# _SIZE_MAP: Mapping[str, Tuple[int, int]] = {
#     "square_hd": (1024, 1024),
#     "portrait_4_3": (960, 1280),
#     "portrait_16_9": (1080, 1920),
#     "landscape_4_3": (1280, 960),
#     "landscape_16_9": (1920, 1080),
# }

# _NAMESPACE = uuid.UUID("00000000-0000-0000-0000-00000000f4f4")  # stable, arbitrary


# def _bool_env(name: str, default: bool) -> bool:
#     val = os.getenv(name)
#     if val is None:
#         return default
#     return val.strip().lower() in {"1", "true", "yes", "on"}


# def _env_latency() -> float:
#     try:
#         return float(os.getenv("FAL_FAKE_LATENCY", "0.1"))
#     except ValueError:
#         return 0.1


# def _env_error_rate() -> float:
#     try:
#         v = float(os.getenv("FAL_FAKE_ERROR_RATE", "0"))
#         return min(1.0, max(0.0, v))
#     except ValueError:
#         return 0.0


# def _env_logs() -> bool:
#     return _bool_env("FAL_FAKE_LOGS", True)


# def _pick_size(key: Optional[str]) -> Tuple[int, int]:
#     if key and key in _SIZE_MAP:
#         return _SIZE_MAP[key]
#     return _SIZE_MAP["square_hd"]


# def _deterministic_uuid(name: str) -> uuid.UUID:
#     # uuid5 ensures stable IDs given the same name; avoids mutable global state.
#     return uuid.uuid5(_NAMESPACE, name)


# def _rand() -> random.Random:
#     # SystemRandom avoids seeding global RNG; safer across reloads.
#     return random.SystemRandom()


# def _maybe_fail() -> None:
#     if _rand().random() < _env_error_rate():
#         # opt-in failure mode to exercise caller retries.
#         raise RuntimeError("fal_client: simulated transient error (FAL_FAKE_ERROR_RATE)")


# def _detect_kind(model_id: str, args: Mapping[str, Any]) -> str:
#     """Return 'image' | 'text' | 'video' based on arguments['type'] or model_id."""
#     t = str(args.get("type", "")).strip().lower() if args else ""
#     if t in {"image", "img"}:
#         return "image"
#     if t in {"text", "txt"}:
#         return "text"
#     if t in {"video", "vid"}:
#         return "video"

#     m = (model_id or "").lower()
#     if any(k in m for k in ("video", "vid", "gen-2", "sora")):
#         return "video"
#     if any(k in m for k in ("text", "chat", "qa", "llama", "gpt")):
#         return "text"
#     return "image"


# # ----------------------------
# # Public API (fal-like)
# # ----------------------------

# def upload_file(path: str | os.PathLike[str]) -> str:
#     """Return a fal-like media URL for an uploaded file."""
#     base = Path(path).name or "file"
#     # return f"https://v3.fal.media/files/mock/{uuid.uuid4()}/{base}"
#     return "https://fillthis.io/i/800x600/ddc5a2/523634.webp"


# def subscribe(
#     model_id: str,
#     *,
#     arguments: Optional[Mapping[str, Any]] = None,
#     with_logs: bool = False,
#     on_queue_update: Optional[Callable[[Queued | InProgress | Completed], None]] = None,
#     **_: Any,
# ) -> Dict[str, Any]:
#     """Synchronous, fal-like subscription flow (now type-aware).

#     Emits Queued(1) → InProgress(logs?) → Completed().
#     Returns a dict whose *shape* depends on the detected kind:
#       - image: original image-shaped payload + kind/url
#       - text:  {"kind":"text","text": "...", "timings":..., "prompt":...}
#       - video: {"kind":"video","video_url":"...", "timings":..., "prompt":...}
#     """
#     _maybe_fail()

#     args = dict(arguments or {})
#     prompt: str = str(args.get("prompt", ""))
#     num_images: int = int(args.get("num_images", 1)) or 1
#     size_key: Optional[str] = args.get("image_size")
#     width, height = _pick_size(size_key)

#     # Choose/propagate a seed; ensure int and within 32-bit range.
#     if "seed" in args and args["seed"] is not None:
#         seed: Optional[int] = int(args["seed"])
#     else:
#         seed = _rand().randint(0, 2**31 - 1)

#     kind = _detect_kind(model_id, args)

#     started_wall = time.time()
#     t0 = time.perf_counter()
#     latency = max(0.0, _env_latency())

#     if on_queue_update is not None:
#         on_queue_update(Queued(1))
#         if latency:
#             time.sleep(latency)

#         if with_logs and _env_logs():
#             logs_obj: List[Any] = [
#                 "30/30 [00:30<00:00, 1.02s/it]",
#                 "100%|█████|",
#                 {"detail": "step 3 of 10"},
#                 "HTTP/1.1 200 OK",
#             ]
#         else:
#             logs_obj = []

#         on_queue_update(InProgress(logs=logs_obj))
#         if latency:
#             time.sleep(latency)

#         on_queue_update(Completed())

#     # Build type-specific result
#     inference = time.perf_counter() - t0
#     total = inference

#     if kind == "image":
#         images: List[Dict[str, Any]] = []
#         for i in range(num_images):
#             # keep deterministic path (even if URL is static) for parity with real clients
#             _ = _deterministic_uuid(f"{model_id}:{prompt}:{seed}:{i}:{width}x{height}") if seed is not None else uuid.uuid4()
#             image_url = "https://fillthis.io/i/800x600/ddc5a2/523634.webp"
#             images.append(
#                 {
#                     "url": image_url,
#                     "width": width,
#                     "height": height,
#                     "content_type": "image/jpeg",
#                 }
#             )

#         result: Dict[str, Any] = {
#             "kind": "image",
#             "images": images,
#             "timings": {
#                 "started": float(started_wall),
#                 "inference": float(inference),
#                 "total": float(total),
#             },
#             "seed": int(seed if seed is not None else 0),
#             "has_nsfw_concepts": [False for _ in range(num_images)],
#             "prompt": prompt,
#             "first_image_url": images[0]["url"],
#             "url": images[0]["url"],  # shorthand
#         }
#         return result

#     if kind == "text":
#         sample = f"Sample text output for '{prompt}'" if prompt else "Sample text output"
#         return {
#             "kind": "text",
#             "text": sample,
#             "timings": {
#                 "started": float(started_wall),
#                 "inference": float(inference),
#                 "total": float(total),
#             },
#             "prompt": prompt,
#         }

#     # kind == "video"
#     video_url = "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"

#     # Optional: a stable-but-fake file name/size
#     file_name = "output.mp4"
#     file_size = 1_048_576  # 1 MB placeholder

#     return {
#         "kind": "video",
#         "video": {
#             "url": video_url,
#             "content_type": "video/mp4",
#             "file_name": file_name,
#             "file_size": file_size,
#             # "file_data": None,  # usually omitted; include if you need the field present
#         },
#         # keep useful metadata alongside, if you want
#         "timings": {
#             "started": float(started_wall),
#             "inference": float(inference),
#             "total": float(total),
#         },
#         "prompt": prompt,

#         # ---- (optional backward-compat) ----
#         # Return the old field too so any existing callers don't break.
#         # Remove these if you want a *strict* new shape:
#         "video_url": video_url,
#         "width": 1280,
#         "height": 720,
#         "content_type": "video/mp4",
#     }



# def run(model_id: str, *, arguments: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
#     """fal-like convenience wrapper that returns the final (type-aware) result."""
#     return subscribe(model_id, arguments=arguments, with_logs=False, on_queue_update=None, **kwargs)


# async def run_async(
#     model_id: str,
#     *,
#     arguments: Optional[Mapping[str, Any]] = None,
#     **kwargs: Any,
# ) -> Dict[str, Any]:
#     """Async variant of `run` using a background thread."""
#     return await asyncio.to_thread(run, model_id, arguments=arguments, **kwargs)


# def submit(model_id: str, *, arguments: Optional[Mapping[str, Any]] = None, **_: Any) -> Dict[str, Any]:
#     """fal-like submit returning a request id only."""
#     args = dict(arguments or {})
#     name = f"{model_id}:{args.get('prompt','')}:{args.get('seed','')}:{args.get('image_size','')}:{args.get('num_images',1)}"
#     rid = str(_deterministic_uuid(name))
#     return {"request_id": rid}


# def status(request_id: str, **_: Any) -> Dict[str, Any]:
#     """Minimal status endpoint (always completed for simplicity)."""
#     return {"request_id": request_id, "status": "COMPLETED"}


# def result(request_id: str, **_: Any) -> Dict[str, Any]:
#     """Return a stable, request-id-derived *image-shaped* result.

#     Note: We can't infer kind from request_id alone, so this remains image-shaped.
#     """
#     width, height = _pick_size("square_hd")
#     started_wall = time.time()
#     return {
#         "images": [
#             {
#                 "url": "https://fillthis.io/i/800x600/ddc5a2/523634.webp",
#                 "width": width,
#                 "height": height,
#                 "content_type": "image/jpeg",
#             }
#         ],
#         "timings": {"started": float(started_wall), "inference": 0.0, "total": 0.0},
#         "seed": 0,
#         "has_nsfw_concepts": [False],
#         "prompt": "",
#     }


# __all__ = [
#     "Queued",
#     "InProgress",
#     "Completed",
#     "subscribe",
#     "upload_file",
#     # convenience exports
#     "run",
#     "run_async",
#     "submit",
#     "status",
#     "result",
# ]


"""fal_client

A tiny, dependency-free fake of the fal.ai Python SDK.

This version is *type-aware*:
- If the model is **image** it returns the original image-shaped payload and also
  adds: `kind="image"` and a shorthand `url` (same as `first_image_url`).
- If the model is **text** it returns: {"kind":"text","text": "...", "timings":..., "prompt":...}
- If the model is **video** it returns: {"kind":"video","video": { "url": "...", ... }, "timings":..., "prompt":...}

How the kind is chosen (in order)
---------------------------------
1) Env override: FAL_FAKE_KIND=image|text|video
2) Request arguments (first match): "fal_kind" | "__mock_kind" | "type"
3) Heuristic from model_id: contains "video"/"vid"/"gen-2"/"sora" → video,
   contains "text"/"chat"/"qa"/"llama"/"gpt" → text,
   else image (default)

Environment toggles
-------------------
- FAL_FAKE_LATENCY (float seconds; default ~0.1)
- FAL_FAKE_ERROR_RATE (0–1; default 0)
- FAL_FAKE_LOGS (bool; default true)

Reload-safe: no mutable global state that breaks on importlib.reload(fal_client).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

import asyncio
import base64
import json
import os
import random
import time
import uuid


# ----------------------------
# Public update event classes
# ----------------------------

@dataclass(frozen=True)
class Queued:
    position: int  # fixed to 1 for this fake


@dataclass(frozen=True)
class InProgress:
    logs: Any  # list | dict


@dataclass(frozen=True)
class Completed:
    pass


# ----------------------------
# Helpers (kept module-local)
# ----------------------------

_SIZE_MAP: Mapping[str, Tuple[int, int]] = {
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
    return uuid.uuid5(_NAMESPACE, name)


def _rand() -> random.Random:
    return random.SystemRandom()


def _maybe_fail() -> None:
    if _rand().random() < _env_error_rate():
        raise RuntimeError("fal_client: simulated transient error (FAL_FAKE_ERROR_RATE)")


def _detect_kind(model_id: str, args: Mapping[str, Any]) -> str:
    """Return 'image' | 'text' | 'video' from env/args/model_id."""
    # 1) Env override
    env_kind = os.getenv("FAL_FAKE_KIND", "").strip().lower()
    if env_kind in {"image", "text", "video"}:
        return env_kind

    # 2) Arguments keys
    t = ""
    if args:
        for key in ("fal_kind", "__mock_kind", "type"):
            v = args.get(key)
            if isinstance(v, str):
                t = v.strip().lower()
                break
    if t in {"image", "img"}:
        return "image"
    if t in {"text", "txt"}:
        return "text"
    if t in {"video", "vid"}:
        return "video"

    # 3) Heuristic from model_id
    m = (model_id or "").lower()
    if any(k in m for k in ("video", "vid", "gen-2", "sora")):
        return "video"
    if any(k in m for k in ("text", "chat", "qa", "llama", "gpt")):
        return "text"
    return "image"


# --- helpers to pack/unpack request info into the request_id (stateless) ---

def _pack_request_token(model_id: str, args: Mapping[str, Any]) -> str:
    """Create a self-contained request_id carrying kind/model/args."""
    kind = _detect_kind(model_id, args)
    payload = {
        "v": 2,  # token schema version
        "kind": kind,
        "model_id": model_id,
        "args": dict(args or {}),
        "uuid": str(_deterministic_uuid(
            f"{model_id}:{args.get('prompt','')}:{args.get('seed','')}:{args.get('image_size','')}:{args.get('num_images',1)}:{kind}"
        )),
        "ts": int(time.time()),
    }
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    token = base64.urlsafe_b64encode(data).decode("ascii")
    return f"ff:{token}"


def _unpack_request_token(request_id: str) -> Optional[Mapping[str, Any]]:
    """Return decoded dict or None if this is a legacy/unknown id."""
    if not isinstance(request_id, str) or not request_id.startswith("ff:"):
        return None
    try:
        token = request_id.split("ff:", 1)[1]
        data = base64.urlsafe_b64decode(token.encode("ascii"))
        payload = json.loads(data.decode("utf-8"))
        if not isinstance(payload, dict) or "kind" not in payload:
            return None
        return payload
    except Exception:
        return None


# ----------------------------
# Public API (fal-like)
# ----------------------------

def upload_file(path: str | os.PathLike[str]) -> str:
    """Return a fal-like media URL for an uploaded file."""
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
    """Synchronous, fal-like subscription flow (now type-aware)."""
    _maybe_fail()

    args = dict(arguments or {})
    prompt: str = str(args.get("prompt", ""))
    num_images: int = int(args.get("num_images", 1)) or 1
    size_key: Optional[str] = args.get("image_size")
    width, height = _pick_size(size_key)

    # Choose/propagate a seed
    if "seed" in args and args["seed"] is not None:
        seed: Optional[int] = int(args["seed"])
    else:
        seed = _rand().randint(0, 2**31 - 1)

    kind = _detect_kind(model_id, args)

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

    # Build type-specific result
    inference = time.perf_counter() - t0
    total = inference

    if kind == "image":
        images: List[Dict[str, Any]] = []
        for i in range(num_images):
            _ = _deterministic_uuid(f"{model_id}:{prompt}:{seed}:{i}:{width}x{height}") if seed is not None else uuid.uuid4()
            image_url = "https://fillthis.io/i/800x600/ddc5a2/523634.webp"
            images.append(
                {
                    "url": image_url,
                    "width": width,
                    "height": height,
                    "content_type": "image/jpeg",
                }
            )
        return {
            "kind": "image",
            "images": images,
            "timings": {
                "started": float(started_wall),
                "inference": float(inference),
                "total": float(total),
            },
            "seed": int(seed if seed is not None else 0),
            "has_nsfw_concepts": [False for _ in range(num_images)],
            "prompt": prompt,
            "first_image_url": images[0]["url"],
            "url": images[0]["url"],  # shorthand
        }

    if kind == "text":
        sample = f"Sample text output for '{prompt}'" if prompt else "Sample text output"
        return {
            "kind": "text",
            "text": sample,
            "timings": {
                "started": float(started_wall),
                "inference": float(inference),
                "total": float(total),
            },
            "prompt": prompt,
        }

    # kind == "video"
    video_url = "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"
    file_name = "output.mp4"
    file_size = 1_048_576  # 1 MB placeholder
    return {
        "kind": "video",
        "video": {
            "url": video_url,
            "content_type": "video/mp4",
            "file_name": file_name,
            "file_size": file_size,
            # "file_data": None,
        },
        "timings": {
            "started": float(started_wall),
            "inference": float(inference),
            "total": float(total),
        },
        "prompt": prompt,

        # optional backward-compat fields (remove if you want strict shape)
        "video_url": video_url,
        "width": 1280,
        "height": 720,
        "content_type": "video/mp4",
    }


def run(model_id: str, *, arguments: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
    """fal-like convenience wrapper that returns the final (type-aware) result."""
    return subscribe(model_id, arguments=arguments, with_logs=False, on_queue_update=None, **kwargs)


async def run_async(
    model_id: str,
    *,
    arguments: Optional[Mapping[str, Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Async variant of `run` using a background thread."""
    return await asyncio.to_thread(run, model_id, arguments=arguments, **kwargs)


def submit(model_id: str, *, arguments: Optional[Mapping[str, Any]] = None, **_: Any) -> Dict[str, Any]:
    """fal-like submit returning a request id only (kind-aware without globals)."""
    args = dict(arguments or {})
    rid = _pack_request_token(model_id, args)
    return {"request_id": rid}


def status(request_id: str, **_: Any) -> Dict[str, Any]:
    """Minimal status endpoint (always completed; includes kind if known)."""
    payload = _unpack_request_token(request_id)
    if payload:
        return {"request_id": request_id, "status": "COMPLETED", "kind": payload["kind"]}
    return {"request_id": request_id, "status": "COMPLETED"}  # legacy fallback


def result(request_id: str, **_: Any) -> Dict[str, Any]:
    """Return a stable result matching the original kind (decoded from request_id).

    Legacy IDs (not generated by this version) fall back to image-shaped output.
    """
    payload = _unpack_request_token(request_id)
    started_wall = time.time()

    if payload:
        kind = payload["kind"]
        model_id = payload.get("model_id", "")
        args = dict(payload.get("args", {}))
        prompt = str(args.get("prompt", ""))

        timings = {"started": float(started_wall), "inference": 0.0, "total": 0.0}

        if kind == "text":
            sample = f"Sample text output for '{prompt}'" if prompt else "Sample text output"
            return {
                "kind": "text",
                "text": sample,
                "timings": timings,
                "prompt": prompt,
            }

        if kind == "video":
            video_url = "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"
            return {
                "kind": "video",
                "video": {
                    "url": video_url,
                    "content_type": "video/mp4",
                    "file_name": "output.mp4",
                    "file_size": 1_048_576,
                },
                "timings": timings,
                "prompt": prompt,

                # optional compatibility fields
                "video_url": video_url,
                "width": 1280,
                "height": 720,
                "content_type": "video/mp4",
            }

        # default: image
        width, height = _pick_size(args.get("image_size"))
        image_url = "https://fillthis.io/i/800x600/ddc5a2/523634.webp"
        return {
            "kind": "image",
            "images": [
                {
                    "url": image_url,
                    "width": width,
                    "height": height,
                    "content_type": "image/jpeg",
                }
            ],
            "timings": timings,
            "seed": int(args.get("seed", 0)),
            "has_nsfw_concepts": [False],
            "prompt": prompt,
            "first_image_url": image_url,
            "url": image_url,
        }

    # ---- legacy fallback (old request_ids) ----
    width, height = _pick_size("square_hd")
    image_url = "https://fillthis.io/i/800x600/ddc5a2/523634.webp"
    return {
        "images": [
            {
                "url": image_url,
                "width": width,
                "height": height,
                "content_type": "image/jpeg",
            }
        ],
        "timings": {"started": float(started_wall), "inference": 0.0, "total": 0.0},
        "seed": 0,
        "has_nsfw_concepts": [False],
        "prompt": "",
        "first_image_url": image_url,
    }


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


