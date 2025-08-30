
# Pip Package: HoloAI
import asyncio
import inspect
import logging
import os
import re
import threading
from importlib import import_module
from datetime import datetime
from dotenv import load_dotenv
from typing import Iterable, Union, List, Dict, Any
import tempfile, mimetypes, urllib.request

from .HAIUtils.HAIUtils import (
    getFrameworkInfo,
    formatJsonInput,
    formatJsonExtended,
    parseJsonInput,
    formatTypedInput,
    formatTypedExtended,
    parseTypedInput,
    parseInstructions,
    parseModels,
    isStructured,
    safetySettings,
    getFrames
)

load_dotenv()
logger = logging.getLogger(__name__)

# Notice = os.getenv("GOOGLE_API_KEY")
# if Notice:
#     print("[Notice] GOOGLE_API_KEY detected. This will be deprecated in version 5.1. Please switch to GEMINI_API_KEY.")

def setProvider(apiInput=None):
    """
    Sets provider API keys from string, tuple, or list, or env.
    Passes API key directly to config if possible.
    Returns a providerMap of all found providers.
    """

    PROVIDERS = {
        "OPENAI_API_KEY":    ("HoloAI.HAIConfigs.OpenAIConfig",   "OpenAIConfig",   "openai"),
        "ANTHROPIC_API_KEY": ("HoloAI.HAIConfigs.AnthropicConfig","AnthropicConfig","anthropic"),
        "GEMINI_API_KEY":    ("HoloAI.HAIConfigs.GoogleConfig",   "GoogleConfig",   "google"),  # Alias for Google
        "GROQ_API_KEY":      ("HoloAI.HAIConfigs.GroqConfig",     "GroqConfig",     "groq"),
        "XAI_API_KEY":       ("HoloAI.HAIConfigs.xAIConfig",      "xAIConfig",      "xai"),
    }


    # Step 1: Parse keys from apiInput (if given) and always set env too (for backward compat)
    keyMap = {}
    if apiInput is None:
        inputList = []
    elif isinstance(apiInput, str):
        inputList = [apiInput.strip()]
    elif isinstance(apiInput, (list, tuple)):
        inputList = [s.strip() for s in apiInput if isinstance(s, str) and s.strip()]
    else:
        raise ValueError("setProvider input must be a string, list, tuple, or None")

    for assignment in inputList:
        try:
            envKey, apiKey = assignment.split('=', 1)
            envKey = envKey.strip()
            apiKey = apiKey.strip()
            os.environ[envKey] = apiKey  # set for backward compat
            keyMap[envKey] = apiKey      # track for direct pass
        except Exception:
            raise ValueError(f"Each assignment must be 'PROVIDER_KEY=key', got: {assignment}")

    providerMap = {}
    for envKey, (module, clsName, mapKey) in PROVIDERS.items():
        apiKey = keyMap.get(envKey) or os.getenv(envKey)
        if apiKey:
            try:
                mod = import_module(module)
                # Pass apiKey directly if config supports it, else fallback to no-arg
                try:
                    providerMap[mapKey] = getattr(mod, clsName)(apiKey)
                except TypeError:
                    providerMap[mapKey] = getattr(mod, clsName)()
            except ImportError:
                continue

    return providerMap

MODELS = {
    ("gpt", "o", "dall-e-3"): "openai",
    ("claude",): "anthropic",
    ("llama", "meta-llama", "gemma2", "qwen", "deepseek",): "groq",
    ("gemini", "gemma",): "google",
    ("grok"): "xai",
}


class HoloAI:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(HoloAI, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, 'initialized', False):
            return

        self.providerMap = setProvider()
        self.initialized = True

    def getFrameworkInfo(self):
        return getFrameworkInfo()

    def listProviders(self):
        return list(self.providerMap.keys())

    def _inferModelProvider(self, model: str):
        return next(
            (provider for prefixes, provider in MODELS.items()
             if any(model.startswith(prefix) for prefix in prefixes)),
            None
        )

    def setProvider(self, apiInput=None):
        """
        Sets provider API keys from:
        - a single string:      'PROVIDER_KEY=api_key'
        - a tuple of strings:   ('PROVIDER_KEY=api_key', ...)
        - a list of strings:    ['PROVIDER_KEY=api_key', ...]
        - or uses environment if nothing passed.

        Returns a providerMap of all found providers.
        """
        self.providerMap = setProvider(apiInput)

    def _getProviderConfig(self, model: str):
        """
        Returns the provider configuration for a given model.
        :param model: (str) The model name to infer the provider from.
        :return: The provider configuration object.
        :raises ValueError: If the provider cannot be inferred from the model.
        """
        provider = self._inferModelProvider(model)
        if provider and provider in self.providerMap:
            return self.providerMap[provider]
        raise ValueError(f"Cannot infer provider from model '{model}'. Valid providers: {list(self.providerMap.keys())}")

    def HoloCompletion(self, **kwargs):
        """
        HoloCompletion requests.
        Handles both text and vision requests.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use for both response and vision (Not Required if 'models' is set).
            - models: (str, list, or dict) Per-task models (Optional):
                - str: Used for both response and vision.
                - list/tuple: [response_model, vision_model].
                - dict: {'response': ..., 'vision': ...}.
            - system/instructions: (str) System prompt or additional instructions (Optional).
                system = "You are a helpful assistant."
                instructions = "You can answer questions and provide information."
            - user/input: (str or list) The main user input (Required).
                Accepts a single prompt string or a message history (list of messages).
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: Skills and Actions to use (Optional).
                Skills and actions will be executed if the model chooses to call them.
                Valid options:
                    - capabilities=[skills, actions]
                    - skills=skills, 
                      actions=actions
                If only actions is provided (without skills), this is not allowed and will result in an error.
            - tools: (list) Tools to use (Optional) [tools].
            - choice/tool_choice: (str) Controls model tool-calling behavior.
                Valid values:
                    - 'auto': Model decides when to call tools (default)
                    - 'required': Model must call a tool (forces function/tool call)
                    - 'none': Tool/function calling is disabled
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - creativity/temperature: (float) Creativity level (0.0 to 1.0, default: 0.5).
            - effort: (str) Effort level ('auto', 'low', 'medium', 'high') (Optional (default: 'auto')).
            - budget/max_budget: (int) Budget for the response (Optional (default: 1369)).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object, or a Vision object or both depending on input.
        """
        return self._routeCompletion(**kwargs)

    def HoloAgent(self, **kwargs):
        """
        HoloAgent requests.
        Handles both text and vision requests.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use for both response and vision (Not Required if 'models' is set).
            - models: (str, list, or dict) Per-task models (Optional):
                - str: Used for both response and vision.
                - list/tuple: [response_model, vision_model].
                - dict: {'response': ..., 'vision': ...}.
            - system/instructions: (str) System prompt or additional instructions (Optional).
                system = "You are a helpful assistant."
                instructions = "You can answer questions and provide information."
            - user/input: (str or list) The main user input (Required).
                Accepts a single prompt string or a message history (list of messages).
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: Skills and Actions to use (Optional).
                Skills and actions will be executed if the model chooses to call them.
                Valid options:
                    - capabilities=[skills, actions]
                    - skills=skills, 
                      actions=actions
                If only actions is provided (without skills), this is not allowed and will result in an error.
            - tools: (list) Tools to use (Optional) [tools].
            - choice/tool_choice: (str) Controls model tool-calling behavior.
                Valid values:
                    - 'auto': Model decides when to call tools (default)
                    - 'required': Model must call a tool (forces function/tool call)
                    - 'none': Tool/function calling is disabled
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - creativity/temperature: (float) Creativity level (0.0 to 1.0, default: 0.5).
            - effort: (str) Effort level ('auto', 'low', 'medium', 'high') (Optional (default: 'auto')).
            - budget/max_budget: (int) Budget for the response (Optional (default: 1369)).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object, or a Vision or both depending on input.
        """
        return self._routeCompletion(**kwargs)

    def HoloAssist(self, **kwargs):
        """
        HoloAssist requests.
        Handles text, vision, and generation requests.
        This feature is still in beta and may change in future releases.
        The goal is to assist complete beginners in using HoloAI and AI in general more effectively.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use for both response and vision (Not Required if 'models' is set).
            - models: (str, list, or dict) Per-task models (Optional):
                - str: Used for both response, vision, and generation if the model supports it.
                - list/tuple: [response_model, vision_model, generation_model].
                - dict: {'response': ..., 'vision': ..., 'generation': ...}.
            - system/instructions: (str) System prompt or additional instructions (Optional).
                system = "You are a helpful assistant."
                instructions = "You can answer questions and provide information."
            - user/input: (str or list) The main user input (Required).
                Accepts a single prompt string or a message history (list of messages).
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: Skills and Actions to use (Optional).
                Skills and actions will be executed if the model chooses to call them.
                Valid options:
                    - capabilities=[skills, actions]
                    - skills=skills, 
                      actions=actions
                If only actions is provided (without skills), this is not allowed and will result in an error.
            - tools: (list) Tools to use (Optional) [tools].
            - choice/tool_choice: (str) Controls model tool-calling behavior.
                Valid values:
                    - 'auto': Model decides when to call tools (default)
                    - 'required': Model must call a tool (forces function/tool call)
                    - 'none': Tool/function calling is disabled
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - creativity/temperature: (float) Creativity level (0.0 to 1.0, default: 0.5).
            - effort: (str) Effort level ('auto', 'low', 'medium', 'high') (Optional (default: 'auto')).
            - budget/max_budget: (int) Budget for the response (Optional (default: 1369)).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - output: (str) Path to a directory.
                A PNG file will be created automatically
                inside your directory (e.g. your_path/Image.png). Existing files are protected
                by auto-incrementing: Image1.png, Image2.png, etc.
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object, Vision object or a generated image depending on input.
        """
        kwargs["beta"] = True
        return self._routeCompletion(**kwargs)

    def Reasoning(self, **kwargs):
        """
        Get a Response from the Response model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
                system = "You are a helpful assistant."
                instructions = "You can answer questions and provide information."
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: Skills and Actions to use (Optional).
                Skills and actions will be executed if the model chooses to call them.
                Valid options:
                    - capabilities=[skills, actions]
                    - skills=skills, 
                      actions=actions
                If only actions is provided (without skills), this is not allowed and will result in an error.
            - tools: (list) Tools to use (Optional) [tools].
            - choice/tool_choice: (str) Controls model tool-calling behavior.
                Valid values:
                    - 'auto': Model decides when to call tools (default)
                    - 'required': Model must call a tool (forces function/tool call)
                    - 'none': Tool/function calling is disabled
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - creativity/temperature: (float) Creativity level (0.0 to 1.0, default: 0.5).
            - effort: (str) Effort level ('auto', 'low', 'medium', 'high') (Optional (default: 'auto')).
            - budget/max_budget: (int) Budget for the response (Optional (default: 1369)).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object.
        """
        return self._routeResponse(**kwargs)

    def Response(self, **kwargs):
        """
        Get a Response from the Response model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
                system = "You are a helpful assistant."
                instructions = "You can answer questions and provide information."
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: Skills and Actions to use (Optional).
                Skills and actions will be executed if the model chooses to call them.
                Valid options:
                    - capabilities=[skills, actions]
                    - skills=skills, 
                      actions=actions
                If only actions is provided (without skills), this is not allowed and will result in an error.
            - tools: (list) Tools to use (Optional) [tools].
            - choice/tool_choice: (str) Controls model tool-calling behavior.
                Valid values:
                    - 'auto': Model decides when to call tools (default)
                    - 'required': Model must call a tool (forces function/tool call)
                    - 'none': Tool/function calling is disabled
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - creativity/temperature: (float) Creativity level (0.0 to 1.0, default: 0.5).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Response object.
        """
        return self._routeResponse(**kwargs)

    def Vision(self, **kwargs):
        """
        Get a Vision response from the Vision model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
                system = "You are a helpful assistant."
                instructions = "You can answer questions and provide information."
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - creativity/temperature: (float) Creativity level (0.0 to 1.0, default: 0.5).
            - files: (list) List of image file paths can be past in manually or during runtime (default: empty list).
            - collect: (int) Number of frames to collect (default: 10).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return: A Vision response object.
        """
        return self._routeVision(**kwargs)

    def Generation(self, **kwargs):
        """
        Get a Generation response from the Generation model.
        :param kwargs: Keyword arguments to customize the request.
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
                system = "You are a helpful assistant."
                instructions = "You can answer questions and provide information."
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - output: (str) Path to a file or directory (Optional).
                If a file path is provided, the generated image is saved at that exact path.
                If a directory is provided, a PNG file will be created automatically
                inside it (e.g. your_path/Image.png). Existing files are protected
                by auto-incrementing: Image1.png, Image2.png, etc.
        Returns:
            PIL.Image.Image: The generated image. If a `output` is provided, the image
            is also saved to that location before being returned.
        """
        return self._routeGeneration(**kwargs)

    def Agent(self, **kwargs):
        """
        Get a Response from the Agent model.
        :param kwargs: Keyword arguments to customize the request.
            - task: (str) Task type ('response', 'reasoning', 'vision', 'generation') (Optional (default: 'response')).
            - model: (str) The model to use (Required).
            - system/instructions: (str) System prompt or additional instructions (Optional).
                system = "You are a helpful assistant."
                instructions = "You can answer questions and provide information."
            - user/input: (str or list) The main user input (Required). 
                Accepts a single prompt string or a message history (list of messages). 
                Both 'user' and 'input' are interchangeable; use either (Preferred: input).
            - skills: Skills and Actions to use (Optional).
                Skills and actions will be executed if the model chooses to call them.
                Valid options:
                    - capabilities=[skills, actions]
                    - skills=skills, 
                      actions=actions
                If only actions is provided (without skills), this is not allowed and will result in an error.
            - tools: (list) Tools to use (Optional) [tools].
            - choice/tool_choice: (str) Controls model tool-calling behavior.
                Valid values:
                    - 'auto': Model decides when to call tools (default)
                    - 'required': Model must call a tool (forces function/tool call)
                    - 'none': Tool/function calling is disabled
            - tokens/max_tokens: (int) Max tokens to use (Optional (default: 3369)).
            - creativity/temperature: (float) Creativity level (0.0 to 1.0, default: 0.5).
            - effort: (str) Effort level ('auto', 'low', 'medium', 'high') (Optional (default: 'auto')).
            - budget/max_budget: (int) Budget for the response (Optional (default: 1369)).
            - files: (list) List of file paths can be past in manually or during runtime (default: empty list).
            - output: (str) Path to a file or directory (Optional).
                If a file path is provided, the generated image is saved at that exact path.
                If a directory is provided, a PNG file will be created automatically
                inside it (e.g. your_path/Image.png). Existing files are protected
                by auto-incrementing: Image1.png, Image2.png, etc.
            - collect: (int) Number of frames to collect (default: 10).
            - verbose: (bool) Return verbose output (Optional (default: False)).
        :return:
            - If 'task' is 'reasoning' or 'response', returns a Response object.
            - If 'task' is 'vision', returns a Vision object.
            - If 'task' is 'generation', returns a Generation object.
                PIL.Image.Image: The generated image. If a `output` is provided, the image
                is also saved to that location before being returned.
        """
        task = kwargs.get('task', 'response').lower()
        taskMap = {
            'reasoning':  self._routeResponse,
            'response':   self._routeResponse,
            'vision':     self._routeVision,
            'generation': self._routeGeneration,
        }
        if task not in taskMap:
            raise ValueError(f"Unknown task: '{task}'. Supported tasks: {list(taskMap.keys())}")
        return taskMap[task](**kwargs)

    #------------- Utility Methods -------------#
    def _routeCompletion(self, **kwargs):
        kwargs  = {k.lower(): v for k, v in kwargs.items()}
        models  = kwargs.pop("model", None) or kwargs.pop("models", None)
        system  = parseInstructions(kwargs)  # popped in parseInstructions
        raw     = kwargs.pop("input", None) or kwargs.pop("user", None)
        files   = kwargs.pop("files", None)
        output  = kwargs.get("output", None)
        beta    = kwargs.get("beta", False)
        meta    = kwargs.get("meta", False)
        debug   = kwargs.get("debug", False)

        models = parseModels(models)

        # if isinstance(raw, list):
        #     last = raw[-1]
        #     if isinstance(last, dict) and "content" in last:
        #         text = str(last["content"])
        #     else:
        #         text = str(last)
        # else:
        #     text = str(raw)
        text = self._resolveText(raw)

        # # Detect
        # passedImages = self._extractMediaInfo(files)
        # inlineImages = self._extractMediaInfo(text)
        # passedFiles  = self._extractFileInfo(files)
        # inlineFiles  = self._extractFileInfo(text)

        # # Normalize paths
        # passedImages = self._normalizePaths(passedImages)
        # inlineImages = self._normalizePaths(inlineImages)
        # passedFiles  = self._normalizePaths(passedFiles)
        # inlineFiles  = self._normalizePaths(inlineFiles)
        
        # allImages = list(dict.fromkeys([*passedImages, *inlineImages]))
        # allFiles  = list(dict.fromkeys([*passedFiles, *inlineFiles]))
        allImages = self._extractAllMedia(files, text)
        allFiles  = self._extractAllFiles(files, text)

        # Build prompt without any paths
        cleanedInput = self._cleanInput(text)
        #print(f"\nCleaned input: {cleanedInput}\n")

        output = self._resolveOutputPath(output)

        def detectIntent():
            system = (
                "Your task is to determine the user's intent and respond ONLY with one of the following:"
                "\n- 'documentAnalysis' for document analysis and handling different types of doc files"
                "\n- 'imageAnalysis' for image analysis and handling different types of image files"
                "\n- 'imageGeneration' for image generation tasks"
                "\n- 'dualCompletion' for a combination of image analysis and document analysis tasks"
                "\n- 'triCompletion' for a combination of image analysis, document analysis, and image generation tasks"
                "\n- 'holoCompletion' for general purpose tasks"
            )
            model  = models['response']
            config = self._getProviderConfig(model)
            return config.getResponse(
                model  = model,
                system = system,
                input  = text,
            )

        def holoCompletion():
            model  = models['response']
            config = self._getProviderConfig(model)
            return config.getResponse(
                model  = model,
                system = system,
                input  = raw,
                **kwargs,
            )

        def documentAnalysis():
            model  = models['response']
            config = self._getProviderConfig(model)
            # skills  = kwargs.pop('skills', None)
            # actions = kwargs.pop('actions', None)
            capabilities, skills, actions = self._popCapabilities(kwargs)
            #localFiles = [self._downloadUrlToTemp(p) if p.startswith(("http://", "https://")) else p for p in allFiles]
            localFiles = self._localizePaths(allFiles)
            # Decide singular vs plural replacement
            # if len(localFiles) == 1:
            #     responseInput = re.sub(r"\bthese files\b", "this file", cleanedInput, flags=re.IGNORECASE)
            # else:
            #     responseInput = cleanedInput
            responseInput = self._adjustInputForFiles(cleanedInput, count=len(localFiles), kind="file")
            #print(f"Response input: {responseInput}\n")
            return config.getResponse(
                model  = model,
                system = system,
                input  = responseInput,
                files  = localFiles, # allFiles,
                **kwargs,
            )

        def imageAnalysis():
            model  = models['vision']
            config = self._getProviderConfig(model)
            # skills  = kwargs.pop('skills', None)
            # actions = kwargs.pop('actions', None)
            capabilities, skills, actions = self._popCapabilities(kwargs)
            #localFiles = [self._downloadUrlToTemp(p) if p.startswith(("http://", "https://")) else p for p in allImages]
            localFiles = self._localizePaths(allImages)
            # Decide singular vs plural replacement
            # if len(localFiles) == 1:
            #     visionInput = re.sub(r"\bthese files\b", "this image", cleanedInput, flags=re.IGNORECASE)
            # else:
            #     visionInput = re.sub(r"\bfiles\b", "images", cleanedInput)
            visionInput = self._adjustInputForFiles(cleanedInput, count=len(localFiles), kind="image")
            #print(f"Vision input: {visionInput}\n")
            return config.getVision(
                model   = model,
                system  = system,
                input   = visionInput,
                files   = localFiles, # allImages,
                **kwargs,
            )

        def imageGeneration():
            # skills  = kwargs.pop('skills', None)
            # actions = kwargs.pop('actions', None)
            capabilities, skills, actions = self._popCapabilities(kwargs)
            model  = models['generation']
            config = self._getProviderConfig(model)
            user = cleanedInput
            if output:
                config.getGeneration(model=model, user=user, output=output)
                #return "Image saved to: " + output
                model = models['vision']
                return config.getVision(
                    model  = model,
                    system = system,
                    input  = "Describe the created image.",
                    files  = [output],
                    **kwargs,
                )
            else:
                return config.getGeneration(model=model, user=user, **kwargs)

        async def dualCompletion():
            # skills  = kwargs.pop('skills', None)
            # actions = kwargs.pop('actions', None)
            model  = models['response']
            config = self._getProviderConfig(model)
            capabilities, skills, actions = self._popCapabilities(kwargs)
            # Run vision and response concurrently in threads
            imageTask   = asyncio.to_thread(imageAnalysis)
            documentTask = asyncio.to_thread(documentAnalysis)
            imgResult, docResult = await asyncio.gather(imageTask, documentTask)

            additional = (
                f"[Media Files]:\n{imgResult}\n"
                f"[Doc Files]:\n{docResult}"
            )

            #print(f"dual text: {text}\n")
            msgs       = f"{cleanedInput}[Media Files]:\n[Doc Files]:\n"

            return config.getResponse(
                model        = model,
                system       = system,
                instructions = additional,
                input        = msgs,
                **kwargs,
            )

        async def triCompletion():
            # skills  = kwargs.pop('skills', None)
            # actions = kwargs.pop('actions', None)
            model  = models['response']
            config = self._getProviderConfig(model)
            capabilities, skills, actions = self._popCapabilities(kwargs)
            # Run vision, response, and generation concurrently in threads
            imageTask    = asyncio.to_thread(imageAnalysis)
            documentTask = asyncio.to_thread(documentAnalysis)
            genTask      = asyncio.to_thread(imageGeneration)

            imgResult, docResult, genResult = await asyncio.gather(
                imageTask, documentTask, genTask
            )

            additional = (
                f"[Media Files]:\n{imgResult}\n"
                f"[Doc Files]:\n{docResult}\n"
                f"[Generated]:\n{genResult}\n"
                "\nIMPORTANT: Do NOT output or invent external image URLs just provide the [Generated]:. "
            )

            msgs = f"{cleanedInput}\n[Media Files]:\n[Doc Files]:\n[Generated]:\n"
            # normalizedInput = re.sub(r"(this file).*", r"\1", cleanedInput, flags=re.IGNORECASE)
            # normalizedInput = re.sub(r"(these files).*", r"\1", normalizedInput, flags=re.IGNORECASE)

            # msgs = f"{normalizedInput}\n[Media Files]:\n[Doc Files]:\n[Generated]:\n"
            #print(f"Tri text: {msgs}\n")

            return config.getResponse(
                model        = model,
                system       = system,
                instructions = additional,
                input        = msgs,
                **kwargs,
            )

        # FUTURE: DO NOT DELETE
        # if meta:
        #     intent = detectIntent()
        #     if intent == "imageGeneration":
        #         return imageGeneration()
        if beta:
            intent = detectIntent()
            # if debug:
            #    print(f"\n[Debug] Detected Intent: {intent}\n")
            #print(f"Detected Intent: {intent}\n")

            # # pick function objects (no calls here) with guards that fall back to holoCompletion
            # intentMap = {
            #     "imageGeneration":   imageGeneration,
            #     "documentAnalysis":  documentAnalysis if allFiles else holoCompletion,
            #     "imageAnalysis":     imageAnalysis    if allImages else holoCompletion,
            #     "dualCompletion":  dualCompletion if (allImages and allFiles) else holoCompletion,
            #     "holoCompletion":    holoCompletion,
            # }
            # intentFunc = intentMap.get(intent, holoCompletion)

            # # Handle both sync and async seamlessly (same pattern as modeFunc)
            # if inspect.iscoroutinefunction(intentFunc):
            #     try:
            #         loop = asyncio.get_running_loop()
            #     except RuntimeError:
            #         loop = None

            #     if loop and loop.is_running():
            #         # Already in an event loop -> return coroutine for caller to await
            #         #print("[Notice] Running in an existing event loop, returning coroutine.")
            #         return intentFunc()
            #     else:
            #         # No event loop running -> safe to use asyncio.run
            #         #print("[Notice] No event loop running, using asyncio.run.")
            #         return asyncio.run(intentFunc())

            # return intentFunc()
            return self._dispatchIntent(
                intent=intent,
                debug=debug,
                allFiles=allFiles,
                allImages=allImages,
                output=output,
                holoCompletion=holoCompletion,
                documentAnalysis=documentAnalysis,
                imageAnalysis=imageAnalysis,
                imageGeneration=imageGeneration,
                dualCompletion=dualCompletion,
                triCompletion=triCompletion,
            )

        # modeMap = {
        #     "holoCompletion":   holoCompletion,
        #     "imageAnalysis":    imageAnalysis,
        #     "documentAnalysis": documentAnalysis,
        #     "dualCompletion": dualCompletion,
        # }

        # mode = (
        #     "dualCompletion" if (allImages and allFiles) else
        #     "imageAnalysis"    if allImages                else
        #     "documentAnalysis" if allFiles                 else
        #     "holoCompletion"
        # )
        # #print(f"Using mode: {mode}\n")

        # modeFunc = modeMap[mode]

        # # Handle both sync and async seamlessly
        # if inspect.iscoroutinefunction(modeFunc):
        #     try:
        #         loop = asyncio.get_running_loop()
        #     except RuntimeError:
        #         loop = None

        #     if loop and loop.is_running():
        #         # Already in an event loop -> return coroutine for caller to await
        #         #print("[Notice] Running in an existing event loop, returning coroutine.")
        #         return modeFunc()
        #     else:
        #         # No event loop running -> safe to use asyncio.run
        #         #print("[Notice] No event loop running, using asyncio.run.")
        #         return asyncio.run(modeFunc())

        # return modeFunc()
        return self._dispatchMode(
            allFiles=allFiles,
            allImages=allImages,
            holoCompletion=holoCompletion,
            documentAnalysis=documentAnalysis,
            imageAnalysis=imageAnalysis,
            dualCompletion=dualCompletion,
        )

    def _dispatchMode(self, **kwargs):
        kwargs    = {k.lower(): v for k, v in kwargs.items()}
        allFiles  = kwargs.get("allfiles", [])
        allImages = kwargs.get("allimages", [])

        holoCompletion   = kwargs["holocompletion"]
        documentAnalysis = kwargs["documentanalysis"]
        imageAnalysis    = kwargs["imageanalysis"]
        dualCompletion   = kwargs["dualcompletion"]

        modeMap = {
            "holocompletion":   holoCompletion,
            "imageanalysis":    imageAnalysis,
            "documentanalysis": documentAnalysis,
            "dualcompletion":   dualCompletion,
        }

        mode = (
            "dualcompletion"   if (allImages and allFiles) else
            "imageanalysis"    if allImages                else
            "documentanalysis" if allFiles                 else
            "holocompletion"
        )

        modeFunc = modeMap[mode]

        if inspect.iscoroutinefunction(modeFunc):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop and loop.is_running():
                return modeFunc()
            else:
                return asyncio.run(modeFunc())

        return modeFunc()

    def _dispatchIntent(self, **kwargs):
        kwargs    = {k.lower(): v for k, v in kwargs.items()}
        intent    = kwargs.get("intent")
        debug     = kwargs.get("debug", False)

        allFiles  = kwargs.get("allfiles", [])
        allImages = kwargs.get("allimages", [])
        output    = kwargs.get("output", None)

        holoCompletion   = kwargs["holocompletion"]
        documentAnalysis = kwargs["documentanalysis"]
        imageAnalysis    = kwargs["imageanalysis"]
        imageGeneration  = kwargs["imagegeneration"]
        dualCompletion   = kwargs["dualcompletion"]
        triCompletion    = kwargs["tricompletion"]

        intentMap = {
            "imagegeneration":  imageGeneration,
            "documentanalysis": documentAnalysis if allFiles else holoCompletion,
            "imageanalysis":    imageAnalysis    if allImages else holoCompletion,
            "dualcompletion":   dualCompletion if (allImages and allFiles) else holoCompletion,
            "tricompletion":    triCompletion if (allImages and allFiles and output) else holoCompletion,
            "holocompletion":   holoCompletion,
        }

        intentFunc = intentMap.get(intent.lower() if intent else "holocompletion", holoCompletion)

        if debug:
            print(f"[Debug] Dispatching intent: {intent} to {intentFunc.__name__}")

        # Handle sync/async seamlessly
        if inspect.iscoroutinefunction(intentFunc):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                return intentFunc()
            else:
                return asyncio.run(intentFunc())

        return intentFunc()

    # def _routeResponse(self, **kwargs):
    #     kwargs = {k.lower(): v for k, v in kwargs.items()}
    #     model  = kwargs.get('model')
    #     config = self._getProviderConfig(model)
    #     return config.getResponse(**kwargs)

    def _routeResponse(self, **kwargs):
        kwargs  = {k.lower(): v for k, v in kwargs.items()}
        model   = kwargs.pop('model', None)
        config  = self._getProviderConfig(model)
        system  = parseInstructions(kwargs)  # popped in parseInstructions
        raw     = kwargs.pop("input", None) or kwargs.pop("user", None)
        files   = kwargs.pop("files", None)

        # if isinstance(raw, list):
        #     last = raw[-1]
        #     if isinstance(last, dict) and "content" in last:
        #         text = str(last["content"])
        #     else:
        #         text = str(last)
        # else:
        #     text = str(raw)
        text = self._resolveText(raw)

        # # Detect
        # passedFiles  = self._extractFileInfo(files)
        # inlineFiles  = self._extractFileInfo(text)

        # # Normalize paths
        # passedFiles  = self._normalizePaths(passedFiles)
        # inlineFiles  = self._normalizePaths(inlineFiles)
        
        # allFiles  = list(dict.fromkeys([*passedFiles, *inlineFiles]))
        allFiles  = self._extractAllFiles(files, text)

        # Build prompt without any paths
        cleanedInput = self._cleanInput(raw)
        #localFiles = [self._downloadUrlToTemp(p) if p.startswith(("http://", "https://")) else p for p in allFiles]
        localFiles = self._localizePaths(allFiles)
        # if localFiles:
        #     capabilities, skills, actions = self._popCapabilities(kwargs)
        # if localFiles:
        #     user = cleanedInput
        # else:
        #     user = raw
        return config.getResponse(
            model   = model,
            system  = system,
            input   = cleanedInput,
            files   = localFiles, # allFiles,
            **kwargs,
        )

    # def _routeVision(self, **kwargs):
    #     kwargs = {k.lower(): v for k, v in kwargs.items()}
    #     model  = kwargs.get('model')
    #     config = self._getProviderConfig(model)
    #     return config.getVision(**kwargs)

    def _routeVision(self, **kwargs):
        kwargs  = {k.lower(): v for k, v in kwargs.items()}
        model   = kwargs.pop('model', None)
        config  = self._getProviderConfig(model)
        system  = parseInstructions(kwargs)  # popped in parseInstructions
        raw     = kwargs.pop("input", None) or kwargs.pop("user", None)
        files   = kwargs.pop("files", None)

        # if isinstance(raw, list):
        #     last = raw[-1]
        #     if isinstance(last, dict) and "content" in last:
        #         text = str(last["content"])
        #     else:
        #         text = str(last)
        # else:
        #     text = str(raw)
        text = self._resolveText(raw)

        # # Detect
        # passedImages = self._extractMediaInfo(files)
        # inlineImages = self._extractMediaInfo(text)

        # # Normalize paths
        # passedImages = self._normalizePaths(passedImages)
        # inlineImages = self._normalizePaths(inlineImages)
        
        # allImages = list(dict.fromkeys([*passedImages, *inlineImages]))
        allImages = self._extractAllMedia(files, text)

        # Build prompt without any paths
        cleanedInput = self._cleanInput(raw)
        #localFiles = [self._downloadUrlToTemp(p) if p.startswith(("http://", "https://")) else p for p in allImages]
        localFiles = self._localizePaths(allImages)
        # if localFiles:
        #     capabilities, skills, actions = self._popCapabilities(kwargs)
        return config.getVision(
            model   = model,
            system  = system,
            input   = cleanedInput,
            files   = localFiles, # allImages,
            **kwargs,
        )

    # def _routeGeneration(self, **kwargs):
    #     kwargs = {k.lower(): v for k, v in kwargs.items()}
    #     model  = kwargs.get('model')
    #     config = self._getProviderConfig(model)
    #     return config.getGeneration(**kwargs)
    def _routeGeneration(self, **kwargs):
        kwargs = {k.lower(): v for k, v in kwargs.items()}
        model  = kwargs.pop('model')
        config = self._getProviderConfig(model)
        output = kwargs.pop("output", None)
        output = self._resolveOutputPath(output)
        return config.getGeneration(model=model, output=output, **kwargs)

    def _routeIntent(self, **kwargs):
        kwargs  = {k.lower(): v for k, v in kwargs.items()}
        model   = kwargs.pop('model', None)
        config  = self._getProviderConfig(model)
        #system  = parseInstructions(kwargs)  # popped in parseInstructions
        user     = kwargs.pop("input", None) or kwargs.pop("user", None)
        # system = (
        #     "Your task is to determine the user's intent and respond ONLY with one of the following:"
        #     "\n- 'response' for text generation"
        #     "\n- 'vision' for vision tasks"
        #     "\n- 'generation' for image generation tasks"
        # )
        system = (
            "Your task is to determine the user's intent and respond ONLY with one of the following:"
            "\n- 'documentAnalysis' for document analysis and handling different types of doc files"
            "\n- 'imageAnalysis' for image analysis and handling different types of image files"
            "\n- 'imageGeneration' for image generation tasks"
            "\n- 'hybridCompletion' for a combination of image analysis and document analysis tasks"
            "\n- 'holoCompletion' for general purpose tasks"
        )
        config = self._getProviderConfig(model)
        return config.getResponse(model=model, system=system, input=user)

    def _popCapabilities(self, kwargs):
        return kwargs.pop("capabilities", None), kwargs.pop("skills", None), kwargs.pop("actions", None)

    def _resolveText(self, raw):
        if isinstance(raw, list):
            last = raw[-1]
            return str(last["content"]) if isinstance(last, dict) and "content" in last else str(last)
        return str(raw)

    def _extractAllMedia(self, text, files):
        # Detect
        passedImages = self._extractMediaInfo(files)
        inlineImages = self._extractMediaInfo(text)

        # Normalize paths
        passedImages = self._normalizePaths(passedImages)
        inlineImages = self._normalizePaths(inlineImages)

        allImages = list(dict.fromkeys([*passedImages, *inlineImages]))
        return allImages

    def _extractAllFiles(self, text, files):
        # Detect
        passedFiles  = self._extractFileInfo(files)
        inlineFiles  = self._extractFileInfo(text)

        # Normalize paths
        passedFiles  = self._normalizePaths(passedFiles)
        inlineFiles  = self._normalizePaths(inlineFiles)

        allFiles  = list(dict.fromkeys([*passedFiles, *inlineFiles]))
        return allFiles

    def _resolveOutputPath(self, output):
        if output and os.path.isdir(output):
            base = os.path.join(output, "Image")
            ext = ".png"
            counter = 1
            candidate = f"{base}{ext}"
            while os.path.exists(candidate):
                candidate = f"{base}{counter}{ext}"
                counter += 1
            return candidate
        return output

    def _localizePaths(self, paths):
        if not paths:
            return []
        http = ("http://", "https://")
        return [self._downloadUrlToTemp(p) if isinstance(p, str) and p.startswith(http) else p for p in paths]

    def _adjustInputForFiles(self, text, count, kind):
        # kind in {"file","image"}; adjust common phrases without overfitting
        if count == 1:
            if kind == "file":
                return re.sub(r"\bthese files\b", "this file", text, flags=re.IGNORECASE)
            if kind == "image":
                t = re.sub(r"\bthese files\b", "this image", text, flags=re.IGNORECASE)
                return re.sub(r"\bfiles\b", "image", t, flags=re.IGNORECASE)
        else:
            if kind == "image":
                return re.sub(r"\bfiles\b", "images", text, flags=re.IGNORECASE)
        return text

    def _normalizePaths(self, paths):
        out = []
        for p in paths:
            if isinstance(p, str) and p.startswith(("http://", "https://")):
                out.append(p)  # leave URL untouched
            else:
                out.append(os.path.normpath(p))
        return out

    def _extractPaths(self, text: Union[str, Iterable[str]], includePatterns: dict, excludePatterns: dict):
        texts = text if isinstance(text, (list, tuple, set)) else [text]

        # Join all include/exclude patterns into one regex each
        includeRegex = re.compile("|".join(includePatterns.values()), re.IGNORECASE)
        excludeRegex = re.compile("|".join(fr"^{p}$" for p in excludePatterns.values()), re.IGNORECASE)

        results = []
        for t in texts:
            if not t:
                continue
            matches = includeRegex.findall(t)
            # findall with capturing groups returns tuples; flatten and filter
            results.extend(
                p for pair in matches for p in (pair if isinstance(pair, tuple) else (pair,))
                if p and not excludeRegex.fullmatch(p)
            )
        return results

    def _extractMediaInfo(self, text: Union[str, Iterable[str]]):
        return self._extractPaths(text, self._mediaPatterns(), self._filePatterns())

    def _extractFileInfo(self, text: Union[str, Iterable[str]]):
        return self._extractPaths(text, self._filePatterns(), self._mediaPatterns())

    def _downloadUrlToTemp(self, url: str) -> str:
        try:
            # Guess extension from URL or MIME
            _, ext = os.path.splitext(url)
            if not ext:
                mime, _ = mimetypes.guess_type(url)
                ext = mimetypes.guess_extension(mime) or ".bin"

            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                urllib.request.urlretrieve(url, tmp.name)
                return tmp.name
        except Exception as e:
            print(f"[Warning] Failed to fetch {url}: {e}")
            return None

    def _mediaPatterns(self):
        EXT = r'(?:png|jpe?g|gif|webp|bmp|tiff?)'
        return {
            "win":  fr'([A-Za-z]:(?:\\|/)[^,\n]*?\.{EXT})',
            "unix": fr'(/[^ ,\n]*?/[^,\n]*?\.{EXT})',
            "url":  fr'(https?://[^\s,;()]+?\.{EXT}(?:\?[^\s,;()]*)?)',
        }

    def _filePatterns(self):
        EXT = r'(?:docx?|pdf|txt|odt|rtf|xlsx?|pptx?)'
        return {
            "win":  fr'([A-Za-z]:(?:\\|/)[^,\n]*?\.{EXT})',
            "unix": fr'(/[^ ,\n]*?/[^,\n]*?\.{EXT})',
            "url":  fr'(https?://[^\s,;()]+?\.{EXT}(?:\?[^\s,;()]*)?)',
        }

    def _cleanInput(self, text: Union[str, List[str]]) -> Union[str, List[str]]:
        allExts = r'(?:png|jpe?g|gif|webp|bmp|tiff?|docx?|pdf|txt|odt|rtf|xlsx?|pptx?)'

        # Local paths (allow spaces until extension)
        win  = rf'[A-Za-z]:(?:\\|/)[^,\n]*?\.{allExts}'
        unix = rf'/[^ ,\n]*?/[^,\n]*?\.{allExts}'

        # URLs ending with target extensions (optional querystring)
        url  = rf'https?://[^\s,;()]+?\.{allExts}(?:\?[^\s,;()]*)?'

        pathOrUrl = rf'(?:{win}|{unix}|{url})'

        def cleanSingle(s: str) -> str:
            # Remove matches with optional nearby separators
            s = re.sub(rf'(?:\s*[,;]?\s*){pathOrUrl}(?=(\s|[,;.)]|$))',
                       '', s, flags=re.IGNORECASE)
            # Collapse leftover punctuation/whitespace artifacts
            s = re.sub(r'\s*[,;]\s*', ' ', s)
            return ' '.join(s.split())

        if isinstance(text, str):
            return cleanSingle(text)
        return [cleanSingle(s) for s in text]

    def isStructured(self, obj):
        """
        Check if the input is a structured list of message dicts.
        A structured list is defined as a list of dictionaries where each dictionary
        contains both "role" and "content" keys.
        Returns True if the input is a structured list, False otherwise.
        """
        return isStructured(obj)

    def formatInput(self, value):
        """
        Formats the input value into a list.
        - If `value` is a string, returns a list containing that string.
        - If `value` is already a list, returns it as is.
        - If `value` is None, returns an empty list.
        """
        return [value] if isinstance(value, str) else value

    def formatConversation(self, convo, user):
        """
        Returns a flat list representing the full conversation:
        - If `convo` is a list, appends the user input (str or list) to it.
        - If `convo` is a string, creates a new list with convo and user input.
        """
        if isinstance(convo, str):
            convo = [convo]
        if isinstance(user, str):
            return convo + [user]
        elif isinstance(user, list):
            return convo + user
        else:
            raise TypeError("User input must be a string or list of strings.")


    def formatJsonInput(self, role: str, content: str) -> dict:
        """
        Format content for JSON-based APIs like OpenAI, Groq, etc.
        Converts role to lowercase and ensures it is one of the allowed roles.
        """
        return formatJsonInput(role=role, content=content)

    def formatJsonExtended(self, role: str, content: str) -> dict:
        """
        Extended JSON format for APIs like OpenAI, Groq, etc.
        Maps 'assistant', 'developer', 'model' and 'system' to 'assistant'.
        All other roles (including 'user') map to 'user'.
        """
        return formatJsonExtended(role=role, content=content)

    def parseJsonInput(self, data):
        """
        Accepts a string, a list of strings, or a list of message dicts/typed objects.
        Parses a single raw string with optional role prefix (user:, system:, developer:, assistant:)
        Returns a list of normalized message objects using formatJsonExtended.
        """
        return parseJsonInput(data)

    def formatTypedInput(self, role: str, content: str) -> dict:
        """
        Format content for typed APIs like Google GenAI.
        Converts role to lowercase and ensures it is one of the allowed roles.
        """
        return formatTypedInput(role=role, content=content)

    def formatTypedExtended(self, role: str, content: str) -> dict:
        """
        Extended typed format for Google GenAI APIs.
        Maps 'assistant', 'developer', 'system' and 'model' to 'model'.
        All other roles (including 'user') map to 'user'.
        """
        return formatTypedExtended(role=role, content=content)

    def parseTypedInput(self, data):
        """
        Accepts a string, a list of strings, or a list of message dicts/typed objects.
        Parses a single raw string with optional role prefix (user:, system:, developer:, assistant:)
        Returns a list of normalized Google GenAI message objects using formatTypedExtended.
        """
        return parseTypedInput(data)

    def safetySettings(self, **kwargs):
        """
        Construct a list of Google GenAI SafetySetting objects.

        Accepts thresholds as keyword arguments:
            harassment, hateSpeech, sexuallyExplicit, dangerousContent

        Example:
            safetySettings(harassment="block_high", hateSpeech="block_low")
        """
        return safetySettings(**kwargs)

