import base64
import collections.abc
import io
import os
import sys
import re
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import cv2
from PIL import Image
from google.genai import types
from dotenv import load_dotenv
from gguf_parser import GGUFParser

CREATORS  = ("Tristan McBride Sr.", "Sybil")
CREATED   = "July 4th, 2025"
FRAMEWORK = "HoloAI"
VERSION   = "0.2.1"
CONTRIBUTORS = ()

PROVIDERS = ("xAI", "OpenAI", "Google", "Groq", "Anthropic")

# =========== SAFE STRIP HELPER ==========
# def safeStrip(val):
#     """Strip whitespace from a string, safely handling None."""
#     return (val or "").strip()
def safeStrip(val):
    """Strips whitespace from any value. Returns '' for None. Converts non-string to string safely."""
    if isinstance(val, str):
        return val.strip()
    if val is None:
        return ""
    return str(val).strip()

# HoloAI framework development message
def addNames(items):
    if not items:
        return ""
    return items[0] if len(items) == 1 else ' and '.join(items) if len(items) == 2 else ', '.join(items[:-1]) + ' and ' + items[-1]

HOLOAI_MSG = (
    f"You are currently using the {FRAMEWORK} framework, created and developed by {addNames(CREATORS)} on {CREATED}."
)
if CONTRIBUTORS:
    HOLOAI_MSG += f" Contributors: {addNames(CONTRIBUTORS)}."

ABOUT = (
    "HoloAI is a modular, provider-agnostic AI framework built for both rapid prototyping and "
    "production-grade workloads.\n"
    f"It offers seamless integration with {addNames(PROVIDERS)}, with additional providers on the way.\n"
    "Designed for clarity, extensibility, and safety, HoloAI adapts to diverse workflows while making "
    "deployment straightforward and reliable."
)

LEGAL_NOTICE = (
    "LEGAL NOTICE: HoloAI is a framework for interacting with third-party AI models.\n"
    f"All AI models used with HoloAI (such as those from {addNames(PROVIDERS)}, etc.) are created, trained, and maintained by their respective providers.\n"
    f"{addNames(CREATORS)}, the authors of HoloAI, did not participate in the training, dataset construction, or core development of any AI model used within this framework,\n"
    "and do not claim any ownership of the models' intelligence, data, or outputs.\n"
    "All responsibility, ownership, and credit for model capabilities belong to the respective providers."
)

def getFrameworkInfo():
    print(f"{HOLOAI_MSG}\n\nAbout:\n{ABOUT}\n\n{LEGAL_NOTICE}")
    return f"{HOLOAI_MSG}\n\nAbout:\n{ABOUT}\n\n{LEGAL_NOTICE}"

def makeSystemMsg():
    base = (
        f"You are currently running on the {FRAMEWORK} framework, created and developed by {addNames(CREATORS)} on {CREATED}."
    )
    if CONTRIBUTORS:
        base += f" Contributors: {addNames(CONTRIBUTORS)}."
        base += f"\n\nAbout:\n{ABOUT}\n\n"
    else:
        base += f"\n\nAbout HoloAI:\n{ABOUT}\n\n"
    provider_note = (
        "\nNOTE: You, the model, and your core capabilities are provided by your original creator, not the framework authors. "
        "All credit for your training, data, and core intelligence belongs to the provider and not to the framework authors."
    )
    return base + provider_note

DEV_MSG = makeSystemMsg()

@contextmanager
def suppressSTDERR():
    devnull = open(os.devnull, "w")
    old_stderr = sys.stderr
    sys.stderr = devnull
    try:
        yield
    finally:
        sys.stderr = old_stderr
        devnull.close()

def getDir(*paths):
    return str(Path(*paths).resolve())

def discoverModels(base_path):
    model_map = {}
    alias_to_repo = {}
    repo_root = Path(base_path)
    idx = 1
    for repo_dir in sorted(repo_root.glob('models--*')):
        repo_name = repo_dir.name[8:]
        snapshot_dir = repo_dir / "snapshots"
        if not snapshot_dir.is_dir():
            continue
        snapshots = sorted(snapshot_dir.iterdir())
        if not snapshots:
            continue
        latest_snap = snapshots[-1]
        ggufs = list(latest_snap.glob('*.gguf'))
        if not ggufs:
            continue
        alias = f"omni-{idx}"
        model_map[alias] = str(ggufs[0])
        alias_to_repo[alias] = repo_name
        idx += 1
    return model_map, alias_to_repo

def getContextLength(model_path):
    try:
        parser = GGUFParser(model_path)
        parser.parse()
        meta = parser.metadata
        user = 512
        for key, val in meta.items():
            if 'context_length' in key:
                user = int(val)
                break
        return user
    except Exception as e:
        return 512

def parseInstructions(kwargs):
    system = kwargs.pop("system", None)
    instructions = kwargs.pop("instructions", None)
    if system and instructions:
        sections = {
            "Main": system,
            "Sub": instructions
        }
        combined = "\n".join(f"{key} Instructions:\n{safeStrip(value)}" for key, value in sections.items())
        return _systemInstructions(combined)
    if system or instructions:
        return _systemInstructions(system or instructions)
    return None

def _systemInstructions(system):
    devMessage = DEV_MSG
    if not system:
        return devMessage
    if isStructured(system):
        systemContents = "\n".join(safeStrip(item['content']) for item in system)
        return f"{devMessage}\n{systemContents}"
    return f"{devMessage}\n{safeStrip(system)}"

def validateResponseArgs(model, user):
    if not model:
        raise ValueError("Model cannot be None or empty.")
    if not user:
        raise ValueError("User input cannot be None or empty.")

def validateVisionArgs(model, user, files):
    validateResponseArgs(model, user)
    if not files or not isinstance(files, list) or len(files) == 0:
        raise ValueError("paths must be a list with at least one item.")

def validateGenerationArgs(model, user):
    validateResponseArgs(model, user)

# def parseModels(models):
#     if models is None:
#         raise ValueError("You must specify at least one model (string, list/tuple, or dict).")
#     if isinstance(models, str):
#         return {'response': models, 'vision': models}
#     if isinstance(models, (list, tuple)):
#         if not models:
#             raise ValueError("Model list/tuple must have at least one value.")
#         response = models[0]
#         vision = models[1] if len(models) > 1 else response
#         return {'response': response, 'vision': vision}
#     if isinstance(models, dict):
#         models = {k.lower(): v for k, v in models.items()}
#         response = models.get('response') or models.get('vision')
#         vision = models.get('vision') or response
#         if not response or not vision:
#             raise ValueError("Dict must contain at least 'response' or 'vision' key.")
#         return {'response': response, 'vision': vision}
#     raise TypeError("models must be a string, list/tuple, or dict.")
def parseModels(models):
    if models is None:
        raise ValueError("You must specify at least one model (string, list/tuple, or dict).")
    if isinstance(models, str):
        return {'response': models, 'vision': models, 'generation': models}
    if isinstance(models, (list, tuple)):
        if not models:
            raise ValueError("Model list/tuple must have at least one value.")
        response = models[0]
        vision = models[1] if len(models) > 1 else response
        generation = models[2] if len(models) > 2 else response
        return {'response': response, 'vision': vision, 'generation': generation}
    if isinstance(models, dict):
        models = {k.lower(): v for k, v in models.items()}
        response = models.get('response')
        if not response:
            raise ValueError("Dict must contain at least a 'response' key.")
        vision = models.get('vision') or response
        generation = models.get('generation') or response
        return {'response': response, 'vision': vision, 'generation': generation}
    raise TypeError("models must be a string, list/tuple, or dict.")


def isStructured(obj):
    return (
        isinstance(obj, list)
        and all(isinstance(i, dict) and "role" in i and "content" in i for i in obj)
    )

def formatJsonInput(role: str, content: str) -> dict:
    role = "system" if role.lower() == "developer" else role.lower()
    allowed = {"system", "developer", "assistant", "user"}
    if role not in allowed:
        raise ValueError(f"Invalid role '{role}'. Allowed: {', '.join(allowed)}")
    return {"role": role, "content": content}

def formatJsonExtended(role: str, content: str) -> dict:
    roleLower = role.lower()
    roleMap = {
        "assistant": "assistant",
        "developer": "assistant",
        "system": "assistant",
        "model": "assistant"
    }
    finalRole = roleMap.get(roleLower, "user")
    return {"role": finalRole, "content": content}

def _parseJsonFormat(raw: str) -> dict:
    lowered = safeStrip(raw)
    detectedRole = "user"
    detectedContent = lowered
    for prefix in ("user:", "system:", "developer:", "assistant:"):
        if lowered.lower().startswith(prefix):
            detectedRole = prefix[:-1].lower()
            detectedContent = safeStrip(lowered[len(prefix):])
            break
    return formatJsonExtended(detectedRole, detectedContent)

def parseJsonInput(data):
    if isStructured(data):
        return data
    result = []
    if isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict):
                result.append(entry)
            elif isinstance(entry, str):
                result.append(_parseJsonFormat(entry))
            else:
                raise ValueError("Invalid item in list; must be str or dict.")
        return result
    if isinstance(data, str):
        result.append(_parseJsonFormat(data))
        return result
    raise ValueError("Invalid input type; must be string, list, or structured list.")

def formatTypedInput(role: str, content: str) -> dict:
    role = "system" if role.lower() == "developer" else role.lower()
    role = "model" if role == "assistant" else role.lower()
    allowed = {"system", "developer", "assistant", "model", "user"}
    if role not in allowed:
        raise ValueError(
            f"Invalid role '{role}'. Must be one of {', '.join(allowed)}."
        )
    if role == "system":
        return types.Part.from_text(text=content)
    return types.Content(role=role, parts=[types.Part.from_text(text=content)])

def formatTypedExtended(role: str, content: str) -> dict:
    roleLower = role.lower()
    roleMap = {
        "assistant": "model",
        "model": "model",
        "developer": "model",
        "system": "model"
    }
    finalRole = roleMap.get(roleLower, "user")
    return types.Content(role=finalRole, parts=[types.Part.from_text(text=content)])

def _parseTypedFormat(raw: str):
    lowered = safeStrip(raw)
    detectedRole = "user"
    detectedContent = lowered
    for prefix in ("user:", "system:", "developer:", "assistant:", "model:"):
        if lowered.lower().startswith(prefix):
            detectedRole = prefix[:-1].lower()
            detectedContent = safeStrip(lowered[len(prefix):])
            break
    return formatTypedExtended(detectedRole, detectedContent)

def parseTypedInput(data):
    if isinstance(data, list) and all(
        hasattr(i, "role") or hasattr(i, "text") for i in data
    ):
        return data
    result = []
    if isinstance(data, list):
        for entry in data:
            if isinstance(entry, str):
                result.append(_parseTypedFormat(entry))
            else:
                result.append(entry)
        return result
    if isinstance(data, str):
        result.append(_parseTypedFormat(data))
        return result
    raise ValueError("Invalid input type; must be string, list, or structured list.")

def safetySettings(**kwargs):
    CATEGORY_MAP = {
        "harassment":        "HARM_CATEGORY_HARASSMENT",
        "hateSpeech":        "HARM_CATEGORY_HATE_SPEECH",
        "sexuallyExplicit":  "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "dangerousContent":  "HARM_CATEGORY_DANGEROUS_CONTENT",
    }
    ALLOWED_SETTINGS = {"BLOCK_NONE", "BLOCK_LOW", "BLOCK_MEDIUM", "BLOCK_HIGH", "BLOCK_ALL"}
    DEFAULTS = {k: "BLOCK_NONE" for k in CATEGORY_MAP}
    params = {k: kwargs.get(k, v).upper() for k, v in DEFAULTS.items()}
    for name, val in params.items():
        if val not in ALLOWED_SETTINGS:
            raise ValueError(
                f"Invalid {name} setting: {val}. Must be one of {', '.join(ALLOWED_SETTINGS)}."
            )
    return [
        types.SafetySetting(
            category=CATEGORY_MAP[name], threshold=val
        ) for name, val in params.items()
    ]

def extractMediaInfo(text: str):
    EXT = r'(?:png|jpe?g|gif|webp|bmp|tiff?)'
    PATTERNS = {
        "win": fr'([A-Za-z]:(?:\\|/).*?\.{EXT})',
        "unix": fr'(/[^ ]*?/.*?\.{EXT})'
    }
    matches = re.findall(f"{PATTERNS['win']}|{PATTERNS['unix']}", text, re.IGNORECASE)
    return [p for pair in matches for p in pair if p]

def getFrames(path, collect=5, defaultMime="jpeg"):
    ext = os.path.splitext(path)[1].lower()
    handlerMap = {
        ".gif": lambda p, c: extractFramesPIL(p, c, outFormat="JPEG"),
        ".webp": lambda p, c: extractFramesPIL(p, c, outFormat="WEBP"),
        ".png": lambda p, c: extractFramesPIL(p, c, outFormat="PNG"),
        ".jpg": lambda p, c: extractFramesPIL(p, c, outFormat="JPEG"),
        ".jpeg": lambda p, c: extractFramesPIL(p, c, outFormat="JPEG"),
        ".mp4": extractFramesVideo,
        ".webm": extractFramesVideo,
    }
    if ext in handlerMap:
        return handlerMap[ext](path, collect)
    b64, mimeType = encodeImageFile(path, defaultMime)
    return [(b64, mimeType, 0)]

def encodeImageFile(path, mimeType="jpeg"):
    with open(path, "rb") as imgFile:
        return base64.b64encode(imgFile.read()).decode("utf-8"), mimeType

def extractFramesPIL(path, collect=5, outFormat="PNG"):
    outFormat = outFormat.upper()
    formatToMime = {"PNG": "png", "JPEG": "jpeg", "JPG": "jpeg", "WEBP": "webp"}
    mimeType = formatToMime.get(outFormat, "png")
    with Image.open(path) as img:
        frameCount = getattr(img, "n_frames", 1)
        indices = sorted(idx for idx in ({0, frameCount - 1} | set(range(0, frameCount, collect))) if idx < frameCount)
        frames = []
        for idx in indices:
            try:
                img.seek(idx)
            except EOFError:
                continue
            with io.BytesIO() as buffer:
                img.convert("RGB").save(buffer, format=outFormat)
                b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                frames.append((b64, mimeType, idx))
        return frames

def extractFramesVideo(path, collect=5):
    cap = cv2.VideoCapture(path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = sorted(idx for idx in ({0, total - 1} | set(range(0, total, collect))) if idx < total)
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        success, image = cap.read()
        if not success:
            continue
        success, buffer = cv2.imencode(".jpg", image)
        if not success:
            continue
        b64 = base64.b64encode(buffer.tobytes()).decode("utf-8")
        frames.append((b64, "jpeg", idx))
    cap.release()
    return frames

def unsupportedFormat(ext):
    raise ValueError(f"File format '{ext}' is not supported for Vision frame extraction")

def extractFileInfo(text):
    filePaths = extractDocPaths(text)
    extracted = extractText(filePaths)
    return "\n\n".join(
        f"File {i+1}:\n{safeStrip(extracted[path])}" for i, path in enumerate(filePaths)
    )

def extractDocPaths(text: str):
    EXT = r'(?:docx?|pdf|txt|odt|rtf|xlsx?|pptx?)'
    PATTERNS = {
        "win": fr'([A-Za-z]:(?:\\|/).*?\.{EXT})',
        "unix": fr'(/[^ ]*?/.*?\.{EXT})'
    }
    matches = re.findall(f"{PATTERNS['win']}|{PATTERNS['unix']}", text, re.IGNORECASE)
    return [p for pair in matches for p in pair if p]

def extractText(filePaths):
    extractorMap = {
        "pdf": _extractTextFromPdf,
        "txt": _extractTextFromTxt,
        "docx": _extractTextFromDocx
    }
    def extract(filePath):
        ext = filePath.lower().split('.')[-1]
        if ext not in extractorMap:
            raise ValueError(f"Unsupported file type: {ext}")
        return extractorMap[ext](filePath)
    if isinstance(filePaths, (list, tuple)):
        return {path: extract(path) for path in filePaths}
    elif isinstance(filePaths, str):
        return extract(filePaths)
    else:
        raise TypeError("filePaths must be a str, list, or tuple")

import pdfplumber

def _extractTextFromPdf(filePath):
    with pdfplumber.open(filePath) as pdf:
        return "\n".join(safeStrip(page.extract_text()) for page in pdf.pages)

def _extractTextFromTxt(filePath):
    with open(filePath, "r", encoding="utf-8", errors="ignore") as file:
        return safeStrip(file.read())

from docx import Document

def _extractTextFromDocx(filePath):
    doc = Document(filePath)
    return "\n".join(safeStrip(para.text) for para in doc.paragraphs)

#------------------------ Reasoning Models ------------------------
ANTHROPIC_MODELS = (
    "claude-3-7",
    "claude-sonnet-4",
    "claude-opus-4",
)

GOOGLE_MODELS = (
    "gemini-2.5",
)

OPENAI_MODELS = (
    "o",
)

GROQ_MODELS = (
    "qwen/qwen3-32b",
    "deepseek-r1-distill-llama-70b",
)

XAI_MODELS = (
    "grok-3-mini",
    "grok-4",
)

REASONING_MODELS = (
    *ANTHROPIC_MODELS,
    *GOOGLE_MODELS,
    *OPENAI_MODELS,
    *GROQ_MODELS,
    *XAI_MODELS,
)

def supportsReasoning(model: str) -> bool:
    return model.lower().startswith(REASONING_MODELS)

OPENAI_EFFORT_MAP = {
    "low":    "low",
    "medium": "medium",
    "high":   "high",
    "auto":   None,
}

GOOGLE_EFFORT_MAP = {
    "low":    512,
    "medium": 1024,
    "high":   4096,
    "auto":   -1,
}

ANTHROPIC_EFFORT_MAP = {
    "low": 1024,
    "medium": 2048,
    "high": 4096,
    "auto": None
}
