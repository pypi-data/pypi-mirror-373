#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2025.08.30 06:00:00                  #
# ================================================== #

from typing import Optional, Dict, Any

from google.genai import types as gtypes
from google import genai

from pygpt_net.core.types import (
    MODE_ASSISTANT,
    MODE_AUDIO,
    MODE_CHAT,
    MODE_COMPLETION,
    MODE_IMAGE,
    MODE_RESEARCH,
)
from pygpt_net.core.bridge.context import BridgeContext
from pygpt_net.item.model import ModelItem

from .chat import Chat
from .vision import Vision
from .tools import Tools
from .audio import Audio
from .image import Image
from .realtime import Realtime

class ApiGoogle:
    def __init__(self, window=None):
        """
        Google GenAI API SDK wrapper

        :param window: Window instance
        """
        self.window = window
        self.chat = Chat(window)
        self.vision = Vision(window)
        self.tools = Tools(window)
        self.audio = Audio(window)
        self.image = Image(window)
        self.realtime = Realtime(window)
        self.client: Optional[genai.Client] = None
        self.locked = False
        self.last_client_args: Optional[Dict[str, Any]] = None

    def get_client(
            self,
            mode: str = MODE_CHAT,
            model: ModelItem = None
    ) -> genai.Client:
        """
        Get or create Google GenAI client

        :param mode: Mode (chat, completion, image, etc.)
        :param model: ModelItem
        :return: genai.Client instance
        """
        if not model:
            model = ModelItem()
            model.provider = "google"
        args = self.window.core.models.prepare_client_args(mode, model)
        filtered = {}
        if args.get("api_key"):
            filtered["api_key"] = args["api_key"]
        if self.client is None or self.last_client_args != filtered:
            self.client = genai.Client(**filtered)
        self.last_client_args = filtered
        return self.client

    def call(
            self,
            context: BridgeContext,
            extra: dict = None,
            rt_signals = None
    ) -> bool:
        """
        Make an API call to Google GenAI

        :param context: BridgeContext
        :param extra: Extra parameters
        :param rt_signals: Realtime signals for audio streaming
        :return: True if successful, False otherwise
        """
        mode = context.mode
        model = context.model
        stream = context.stream
        ctx = context.ctx
        ai_name = ctx.output_name if ctx else "assistant"

        # No Responses API in google-genai
        if ctx:
            ctx.use_responses_api = False

        used_tokens = 0
        response = None

        if mode in [MODE_COMPLETION, MODE_CHAT, MODE_AUDIO, MODE_RESEARCH]:

            # Live API for audio streaming
            if mode == MODE_AUDIO and stream:
                is_realtime = self.realtime.begin(
                    context=context,
                    model=model,
                    extra=extra or {},
                    rt_signals=rt_signals
                )
                if is_realtime:
                    return True

            response = self.chat.send(context=context, extra=extra)
            used_tokens = self.chat.get_used_tokens()
            if ctx:
                self.vision.append_images(ctx)

        elif mode == MODE_IMAGE:
            return self.image.generate(context=context, extra=extra)

        elif mode == MODE_ASSISTANT:
            return False  # not implemented for Google

        if stream:
            if ctx:
                ctx.stream = response
                ctx.set_output("", ai_name)
                ctx.input_tokens = used_tokens
            return True

        if response is None:
            return False

        if isinstance(response, dict) and "error" in response:
            return False

        if ctx:
            ctx.ai_name = ai_name
            self.chat.unpack_response(mode, response, ctx)
            try:
                import json
                for tc in getattr(ctx, "tool_calls", []) or []:
                    fn = tc.get("function") or {}
                    args = fn.get("arguments")
                    if isinstance(args, str):
                        try:
                            fn["arguments"] = json.loads(args)
                        except Exception:
                            fn["arguments"] = {}
            except Exception:
                pass
        return True

    def quick_call(
            self,
            context: BridgeContext,
            extra: dict = None
    ) -> str:
        """
        Make a quick API call to Google GenAI and return the output text

        :param context: BridgeContext
        :param extra: Extra parameters
        :return: Output text
        """
        if context.request:
            context.stream = False
            context.mode = MODE_CHAT
            self.locked = True
            self.call(context, extra)
            self.locked = False
            return context.ctx.output

        self.locked = True
        try:
            ctx = context.ctx
            prompt = context.prompt
            system_prompt = context.system_prompt
            temperature = context.temperature
            history = context.history
            functions = context.external_functions
            model = context.model or self.window.core.models.from_defaults()

            client = self.get_client(MODE_CHAT, model)
            tools = self.tools.prepare(model, functions)

            """
            # with remote tools
            base_tools = self.tools.prepare(model, functions)
            remote_tools = self.build_remote_tools(model)
            tools = (base_tools or []) + (remote_tools or [])
            """

            inputs = self.chat.build_input(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
                history=history,
                attachments=context.attachments,
                multimodal_ctx=context.multimodal_ctx,
            )
            cfg = genai.types.GenerateContentConfig(
                temperature=temperature if temperature is not None else self.window.core.config.get('temperature'),
                top_p=self.window.core.config.get('top_p'),
                max_output_tokens=context.max_tokens if context.max_tokens else None,
                system_instruction=system_prompt if system_prompt else None,
                tools=tools if tools else None,
            )
            resp = client.models.generate_content(
                model=model.id,
                contents=inputs,
                config=cfg,
            )

            if ctx:
                calls = self.chat.extract_tool_calls(resp)
                if calls:
                    ctx.tool_calls = calls
            return self.chat.extract_text(resp)
        except Exception as e:
            self.window.core.debug.log(e)
            return ""
        finally:
            self.locked = False

    def build_remote_tools(self, model: ModelItem = None) -> list:
        """
        Build Google GenAI remote tools based on config flags.
        - remote_tools.google.web_search: enables grounding via Google Search (Gemini 2.x)
          or GoogleSearchRetrieval (Gemini 1.5 fallback).
        - remote_tools.google.code_interpreter: enables code execution tool.

        Returns a list of gtypes.Tool objects (can be empty).

        :param model: ModelItem
        :return: list of gtypes.Tool
        """
        tools: list = []
        cfg = self.window.core.config
        model_id = (model.id if model and getattr(model, "id", None) else "").lower()

        # Google Search tool
        if cfg.get("remote_tools.google.web_search") and "image" not in model.id:
            try:
                if not model_id.startswith("gemini-1.5") and not model_id.startswith("models/gemini-1.5"):
                    # Gemini 2.x uses GoogleSearch
                    tools.append(gtypes.Tool(google_search=gtypes.GoogleSearch()))
                else:
                    # Gemini 1.5 fallback uses GoogleSearchRetrieval
                    # Note: Supported only for 1.5 models.
                    tools.append(gtypes.Tool(
                        google_search_retrieval=gtypes.GoogleSearchRetrieval()
                    ))
            except Exception as e:
                # Do not break the request if tool construction fails
                self.window.core.debug.log(e)

        # Code Execution tool
        if cfg.get("remote_tools.google.code_interpreter") and "image" not in model.id:
            try:
                tools.append(gtypes.Tool(code_execution=gtypes.ToolCodeExecution))
            except Exception as e:
                self.window.core.debug.log(e)

        # URL Context tool
        if cfg.get("remote_tools.google.url_ctx") and "image" not in model.id:
            try:
                # Supported on Gemini 2.x+ models (not on 1.5)
                if not model_id.startswith("gemini-1.5") and not model_id.startswith("models/gemini-1.5"):
                    tools.append(gtypes.Tool(url_context=gtypes.UrlContext))
            except Exception as e:
                self.window.core.debug.log(e)

        return tools


    def stop(self):
        """On global event stop"""
        pass

    def close(self):
        """Close Google client"""
        if self.locked:
            return
        if self.client is not None:
            try:
                pass
                # self.client.close()
            except Exception as e:
                self.window.core.debug.log(e)
                print("Error closing Google client:", e)