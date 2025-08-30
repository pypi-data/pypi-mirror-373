import os
from dotenv import load_dotenv
from openai import OpenAI

from HoloAI.HAIUtils.HAIUtils import (
    parseInstructions,
    isStructured,
    formatJsonInput,
    parseJsonInput,
    getFrames,
    supportsReasoning,
    extractFileInfo,
    extractText
)

from HoloAI.HAIBaseConfig.BaseConfig import BaseConfig

load_dotenv()


class xAIConfig(BaseConfig):
    def __init__(self, apiKey=None):
        super().__init__()
        self._setClient(apiKey)
        self._setModels()

    def _setClient(self, apiKey=None):
        if not apiKey:
            apiKey = os.getenv("XAI_API_KEY")
        if not apiKey:
            raise KeyError("Grok API key not found. Please set XAI_API_KEY in your environment variables.")
        self.client = OpenAI(
            base_url="https://api.x.ai/v1",
            api_key=apiKey
        )

    def _setModels(self):
        self.RModel = os.getenv("GROK_RESPONSE_MODEL", "grok-4")
        self.VModel = os.getenv("GROK_VISION_MODEL", "grok-4")
        self.GModel = os.getenv("GROK_GENERATION_MODEL", "grok-2-image")

    # ---------------------------------------------------------
    # Response
    # ---------------------------------------------------------
    def Response(self, **kwargs) -> str:
        keys = self.getKeys("response")
        params = self.extractKwargs(kwargs, keys)

        messages = []
        messages.append(formatJsonInput("system", params["system"]))
        messages.extend(parseJsonInput(params["user"]))

        try:
            args = self._getArgs(params["model"], messages, params["tokens"])
            if params["creativity"]:
                args["temperature"] = params["creativity"]
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
                print("Using reasoning")
                if params["effort"] == "auto":
                    params["effort"] = "low"
                elif params["effort"] == "medium":
                    params["effort"] = "high"
                args["reasoning_effort"] = params["effort"]
                if params["budget"]:
                    args["max_tokens"] = params["budget"]

            response = self._endPoint(**args)
        except Exception:
            # fallback to default RModel
            args = self._getArgs(self.RModel, messages, params["tokens"])
            response = self._endPoint(**args)

        return response if params["verbose"] else response.choices[0].message.content

    # ---------------------------------------------------------
    # Vision
    # ---------------------------------------------------------
    def Vision(self, **kwargs):
        keys = self.getKeys("vision")
        params = self.extractKwargs(kwargs, keys)

        messages = []
        messages.append(formatJsonInput("system", params["system"]))
        images = self._mediaFiles(params["files"], params["collect"])

        userContent = [{"type": "text", "text": params["user"]}] + images
        payload = messages + [{"role": "user", "content": userContent}]

        try:
            args = self._getArgs(params["model"], payload, params["tokens"])
            if params["creativity"]:
                args["temperature"] = params["creativity"]
            response = self._endPoint(**args)
        except Exception:
            # fallback to default VModel
            args = self._getArgs(self.VModel, payload, params["tokens"])
            response = self._endPoint(**args)

        return response if params["verbose"] else response.choices[0].message.content

    # ---------------------------------------------------------
    # Generation
    # ---------------------------------------------------------
    def Generation(self, **kwargs):
        keys = self.getKeys("generation")
        params = self.extractKwargs(kwargs, keys)

        model = params.get("model")
        user = params["user"]
        output = params.get("output")

        try:
            response = self.client.images.generate(model=model, prompt=user)
        except Exception:
            response = self.client.images.generate(model=self.GModel, prompt=user)

        img = self._normalizeImage(url=response.data[0].url)
        return self._returnImage(img, output)
    
    # ---------------------------------------------------------
    # Skills
    # ---------------------------------------------------------
    def processSkills(self, instructions, user, tokens) -> str:
        messages = []
        messages.append(formatJsonInput("system", instructions))
        intent = self.extractIntent(user)
        messages.append(formatJsonInput("user", intent))
        args = self._getArgs(self.RModel, messages, tokens)
        response = self._endPoint(**args)
        return response.choices[0].message.content

    def _endPoint(self, **args) -> str:
        return self.client.chat.completions.create(**args)

    def _getArgs(self, model, messages, tokens):
        args = {
            "model": model,
            "messages": messages,
            "max_tokens": tokens,
        }
        return args

    def _mapChoice(self, choice):
        mapping = {
            "auto": "auto",
            "required": "required",
            "none": "none"
        }
        return mapping[(choice or "auto").lower()]

    def _mediaFiles(self, files, collect):
        images = []
        for path in files:
            frames = getFrames(path, collect)
            b64, mimeType, _ = frames[0]
            images.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/{mimeType};base64,{b64}"}
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
