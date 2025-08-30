import os
import threading
from dotenv import load_dotenv
import anthropic

from HoloAI.HAIUtils.HAIUtils import (
    isStructured,
    formatJsonInput,
    formatJsonExtended,
    parseJsonInput,
    getFrames,
    supportsReasoning,
    extractFileInfo,
    extractText
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig

load_dotenv()


class AnthropicConfig(BaseConfig):
    def __init__(self, apiKey=None):
        super().__init__()
        self._setClient(apiKey)
        self._setModels()

    def _setClient(self, apiKey=None):
        if not apiKey:
            apiKey = os.getenv("ANTHROPIC_API_KEY")
        if not apiKey:
            raise KeyError("Anthropic API key not found. Please set ANTHROPIC_API_KEY in your environment variables.")
        self.client = anthropic.Anthropic(api_key=apiKey)
        # self.client = OpenAI(
        #     base_url="https://api.anthropic.com/v1/",
        #     api_key=apiKey
        # )
    def _setModels(self):
        self.RModel = os.getenv("ANTHROPIC_RESPONSE_MODEL", "claude-3-5-haiku-latest")
        self.VModel = os.getenv("ANTHROPIC_VISION_MODEL", "claude-opus-4-20250514")

    # ---------------------------------------------------------
    # Response
    # ---------------------------------------------------------
    def Response(self, **kwargs) -> str:
        keys = self.getKeys("response")
        params = self.extractKwargs(kwargs, keys)

        messages = parseJsonInput(params["user"])

        try:
            args = self._getArgs(params["model"], params["system"], messages, params["tokens"])
            if params["tools"]:
                args["tools"] = params["tools"]
                args["tool_choice"] = self._mapChoice(params.get("choice"))

            if params["skills"]:
                additionalInfo = self.executeSkills(
                    params["skills"], params["user"], params["tokens"], params["verbose"]
                )
                if additionalInfo:
                    messages.append(formatJsonInput("user", additionalInfo))

            messages += self._docFiles(params)

            if supportsReasoning(params["model"]):
                #args["temperature"] = 1
                if params["creativity"]:
                    args["temperature"] = params["creativity"] + 1
                if params["effort"] == "auto":
                    params["budget"] = 1024
                if params["budget"] < 1024:
                    params["budget"] = 1024
                if params["tokens"] and params["tokens"] < params["budget"]:
                    params["tokens"] = params["tokens"] + params["budget"]
                    args["max_tokens"] = params["tokens"]
                args["thinking"] = {"type": "enabled", "budget_tokens": params["budget"]}
            else:
                if params["creativity"]:
                    args["temperature"] = params["creativity"]

            response = self._endPoint(**args)

        except Exception:
            # fallback to default RModel
            args = self._getArgs(self.RModel, params["system"], messages, params["tokens"])
            response = self._endPoint(**args)

        if supportsReasoning(params.get("model", self.RModel)):
            return response if params["verbose"] else next(
                (block.text for block in response.content if getattr(block, "type", None) == "text"), ""
            )
        return response if params["verbose"] else response.content[0].text

    # ---------------------------------------------------------
    # Vision
    # ---------------------------------------------------------
    def Vision(self, **kwargs):
        keys = self.getKeys("vision")
        params = self.extractKwargs(kwargs, keys)

        images = self._mediaFiles(params["files"], params["collect"])
        userContent = images.copy()
        if params["user"]:
            userContent.append({"type": "text", "text": params["user"]})

        messages = [{"role": "user", "content": userContent}]

        try:
            args = self._getArgs(params["model"], params["system"], messages, params["tokens"])
            if params["creativity"]:
                args["temperature"] = params["creativity"]
            response = self._endPoint(**args)

        except Exception:
            # fallback to default VModel
            args = self._getArgs(self.VModel, params["system"], messages, params["tokens"])
            if params["creativity"]:
                args["temperature"] = params["creativity"]
            response = self._endPoint(**args)

        return response if params["verbose"] else response.content[0].text

    # ---------------------------------------------------------
    # Generation
    # ---------------------------------------------------------
    def Generation(self, **kwargs):
        keys = self.getKeys("generation")
        params = self.extractKwargs(kwargs, keys)

        model = params.get("model")
        user = params["user"]

        return "Anthropic image generation not support yet."

    # ---------------------------------------------------------
    # Skills
    # ---------------------------------------------------------
    def processSkills(self, instructions, user, tokens) -> str:
        messages = []
        intent = self.extractIntent(user)
        messages.append(formatJsonInput("user", intent))
        args = self._getArgs(self.RModel, instructions, messages, tokens)
        response = self._endPoint(**args)
        return response.content[0].text

    def _endPoint(self, **args):
        return self.client.messages.create(**args)

    def _getArgs(self, model, system, messages, tokens):
        args = {
            "model": model,
            "system": system,
            "messages": messages,
            "max_tokens": tokens,
        }
        return args

    def _mapChoice(self, choice):
        mapping = {
            "auto": "auto",
            "required": "any",
            "none": "none"
        }
        return mapping[(choice or "auto").lower()]

    def _mediaFiles(self, files, collect):
        images = []
        for path in files:
            frames = getFrames(path, collect)
            b64, mimeType, _ = frames[0]
            images.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": f"image/{mimeType}",
                    "data": b64
                }
            })
        return images

    def _docFiles(self, params):
        messages = []
        # intent = self.extractIntent(params["user"])
        # fileInfo = extractFileInfo(intent)
        # if fileInfo:
        #     messages.append(formatJsonInput("user", fileInfo))
        files = params["files"]
        if files:
            fileInfo = str(extractText(files))
            if fileInfo:
                messages.append(formatJsonInput("user", fileInfo))
        return messages
