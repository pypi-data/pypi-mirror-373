
import requests
from user_agent import generate_user_agent
from hashlib import md5
import random
from bs4 import BeautifulSoup
import pycountry
import time
from datetime import datetime
from secrets import token_hex
from uuid import uuid4
from mnemonic import Mnemonic
from time import sleep

API_RanaGPT = "http://sii3.moayman.top"

MODELS_DEEP_INFRA = [
    "deepseekv3", "innova", "aicode", "Image4o","deepseekv3x", "deepseekr1", "deepseekr1base",
    "deepseekr1turbo", "deepseekr1llama", "deepseekr1qwen",
    "deepseekprover", "qwen235", "qwen30", "qwen32", "qwen14",
    "mav", "scout", "phi-plus", "guard", "qwq", "gemma27",
    "gemma12", "llama31", "llama332", "llama337", "mixtral24",
    "phi4", "phi-multi", "wizard822", "wizard27", "qwen2572",
    "qwen272", "dolphin26", "dolphin29", "airo70", "lzlv70",
    "mixtral822"
]

MODELS_31 = [
    "grok", "grok-2", "grok-2-1212", "grok-2-mini", "openai",
    "evil", "gpt-4o-mini", "gpt-4-1-nano", "gpt-4", "gpt-4o",
    "gpt-4-1", "gpt-4-1-mini", "o4-mini", "command-r-plus",
    "gemini-2-5-flash", "gemini-2-0-flash-thinking",
    "qwen-2-5-coder-32b", "llama-3-3-70b", "llama-4-scout",
    "llama-4-scout-17b", "mistral-small-3-1-24b",
    "deepseek-r1", "deepseek-r1-distill-llama-70b",
    "deepseek-r1-distill-qwen-32b", "phi-4", "qwq-32b",
    "deepseek-v3", "deepseek-v3-0324", "openai-large",
    "openai-reasoning", "searchgpt"
]

MODELS_BLACKBOX = [
    "blackbox", "gpt-4-1", "gpt-4-1-n", "gpt-4", "gpt-4o",
    "gpt-4o-m", "python", "html", "builder", "java", "js",
    "react", "android", "flutter", "nextjs", "angularjs",
    "swift", "mongodb", "pytorch", "xcode", "azure",
    "bitbucket", "digitalocean", "docker", "electron",
    "erlang", "fastapi", "firebase", "flask", "git",
    "gitlab", "go", "godot", "googlecloud", "heroku"
]

VOICES = ["alloy", "coral", "echo", "shimmer", "verse", "onyx"]
STYLES = ["friendly", "calm", "noir_detective", "cowboy"]


class VoiceAi:
    @staticmethod
    def openai(text: str, voice: str = "alloy", style: str = None, method: str = "GET") -> dict:
        if voice not in VOICES:
            return {
                "status": "Error",
                "error": f"This form '{voice}' does not exist. "
                         f"These are the supported forms for the provider: {VOICES}"
            }
        if style and style not in STYLES:
            return {
                "status": "Error",
                "error": f"This form '{style}' does not exist. "
                         f"These are the supported forms for the provider: {STYLES}"
            }

        params = {"text": text, "voice": voice}
        if style:
            params["style"] = style

        url = f"{API_RanaGPT}/Tofey/voice.php"
        resp = requests.post(url, data=params) if method.upper() == "POST" else requests.get(url, params=params)
        body = resp.text
        status = "ok" if "audio_url" in body else "Bad"
        return {"status": status, "result": body, "Tofey": "@qqxqqv"}

    @staticmethod
    def models() -> list:
        return VOICES

    @staticmethod
    def styles() -> list:
        return STYLES


class TextAi:
    @staticmethod
    def DeepInfra(text: str, model: str) -> dict:
        if model not in MODELS_DEEP_INFRA:
            return {
                "status": "Error",
                "error": f"This form '{model}' does not exist. "
                         f"These are the supported forms for the provider: {MODELS_DEEP_INFRA}"
            }
        try:
            resp = requests.get(f"{API_RanaGPT}/api/DeepInfra.php", params={model: text})
            res = resp.json()
            if "response" in res:
                return {"status": "OK", "result": res["response"], "Tofey": "@qqxqqv"}
            else:
                return {"status": "Bad", "result": res, "Tofey": "@qqxqqv"}
        except Exception as e:
            return {"status": "Error", "error": str(e), "Tofey": "@qqxqqv"}

    @staticmethod
    def models() -> list:
        return MODELS_DEEP_INFRA


class WormGpt:
    @staticmethod
    def DarkGPT(text: str) -> dict:
        res = requests.get(f"{API_RanaGPT}/Tofey/api2/Darkgpt.php", params={"text": text}).json()
        return {"status": "OK", "result": res.get("response"), "Tofey": "@qqxqqv"}

    @staticmethod
    def Worm(text: str) -> dict:
        res = requests.get(f"{API_RanaGPT}/Tofey/api/wormgpt.php", params={"text": text}).json()
        return {"status": "OK", "result": res.get("response"), "Tofey": "@qqxqqv"}

    @staticmethod
    def models() -> list:
        return []


class ModelDeepInfra:
    @staticmethod
    def models() -> list:
        return MODELS_DEEP_INFRA


class Model31:
    @staticmethod
    def Modl(text: str, model: str) -> dict:
        if model not in MODELS_31:
            return {
                "status": "Error",
                "error": f"This form '{model}' does not exist. "
                         f"These are the supported forms for the provider: {MODELS_31}"
            }
        return requests.get(f"{API_RanaGPT}/api/gpt.php", params={model: text}).json()

    @staticmethod
    def models() -> list:
        return MODELS_31


class BlackBox:
    @staticmethod
    def Models(text: str, model: str) -> dict:
        if model not in MODELS_BLACKBOX:
            return {
                "status": "Error",
                "error": f"This form '{model}' does not exist. "
                         f"These are the supported forms for the provider: {MODELS_BLACKBOX}"
            }
        data = requests.get(f"{API_RanaGPT}/api/black.php", params={model: text}).json()
        return {"status": "OK", "result": data.get("response"), "Tofey": "@qqxqqv"}

    @staticmethod
    def models() -> list:
        return MODELS_BLACKBOX


class Developers:
    @staticmethod
    def Tofey() -> str:
        return (
            "Name ➝ ➞ #Tofey\n\n"
            "My user = @qqxqqv\n\n"
            "ʀᴀɴᴅᴏᴍ ǫᴜᴏᴛᴇ ➛ ➜ ➝\n"
            "    ˛ I have you, that's all I need 𓍲 ."
        )

    @staticmethod
    def models() -> list:
        return []


class ImageAi:
    SUPPORTED_MODELS = [
        "fluex-pro", "flux", "schnell", "imger-12", "deepseek",
        "gemini-2-5-pro", "blackbox", "redux", "RanaGPT-7-i",
        "r1", "gpt-4-1"
    ]

    @staticmethod
    def generate(prompt: str, model: str = "RanaGPT-7-i") -> dict:
        if model not in ImageAi.SUPPORTED_MODELS:
            return {
                "status": "Error",
                "error": f"This form '{model}' does not exist. "
                         f"These are the supported forms for the provider: {ImageAi.SUPPORTED_MODELS}"
            }
        resp = requests.get(f"{API_RanaGPT}/api/img.php", params={model: prompt})
        try:
            return resp.json()
        except:
            return {"status": "OK", "result": resp.text}

    @staticmethod
    def models() -> list:
        return ImageAi.SUPPORTED_MODELS


class ChatAi:
    @staticmethod
    def ask(prompt: str) -> dict:
        return requests.get(f"{API_RanaGPT}/api/chat/gpt-3.5.php", params={"ai": prompt}).json()

    @staticmethod
    def models() -> list:
        return []


class AzkarApi:
    @staticmethod
    def today() -> dict:
        try:
            return requests.get(f"{API_RanaGPT}/api/azkar.php").json()
        except:
            return {"status": "OK", "result": ""}

    @staticmethod
    def models() -> list:
        return []


class DeepSeekT1:
    @staticmethod
    def codeify(text: str) -> dict:
        url = f"{API_RanaGPT}/api/DeepSeek/DeepSeek.php"
        resp = requests.get(url, params={"text": text})
        body = resp.text
        try:
            data = resp.json()

            if isinstance(data, dict):
                if "result" in data:
                    return {"status": "OK", "result": data["result"]}
                if "response" in data:
                    return {"status": "OK", "result": data["response"]}

            return {"status": "OK", "result": str(data)}
        except ValueError:

            return {"status": "OK", "result": body}

    @staticmethod
    def models() -> list:
        return []


class GeminiApi:
    @staticmethod
    def ask(prompt: str) -> dict:
        try:
            return requests.get(f"{API_RanaGPT}/Tofey/gemini.php", params={"text": prompt}).json()
        except:
            return {"status": "OK", "result": ""}

    @staticmethod
    def models() -> list:
        return []


def innova(prompt):
    url = "https://tofey.serv00.net/api/chatgpt3.5.php"
    params = {"text": prompt}  # API ينتظر 'text' وليس 'prompt'
    try:
        response = requests.get(url, params=params)  # استخدم GET لأن API يستقبل GET
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response found.")
    except Exception as e:
        return f"Error: {e}"
        
        
def aicode(prompt):
    url = "https://tofey.serv00.net/api/aicode.php"
    params = {"text": prompt}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error: {e}"
        

import requests

class Image4o:
    @staticmethod
    def generate(prompt: str):
        try:
            url = "http://185.158.132.66:2010/api/tnt/tnt-black-image"
            params = {"text": prompt}
            resp = requests.get(url, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            
            print("Raw API response:", data)  # يطبع الرد كامل
            # نحاول استخراج الصور بأي مفتاح موجود
            if "الصور" in data:
                return data["الصور"]
            elif "images" in data:
                return data["images"]
            else:
                # إذا مافي صور نرجع الرد كامل
                return data
        except Exception as e:
            return {"status": "Error", "message": str(e)}


import requests

class simongpt:
    @staticmethod
    def generate(prompt: str):
        try:
            url = "https://tofey.serv00.net/ai.php"
            params = {"text": prompt}
            resp = requests.get(url, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            
            print("Raw API response:", data)  # يطبع الرد كامل
            # نحاول استخراج الصور بأي مفتاح موجود
            if "الصور" in data:
                return data["الصور"]
            elif "images" in data:
                return data["images"]
            else:
                # إذا مافي صور نرجع الرد كامل
                return data
        except Exception as e:
            return {"status": "Error", "message": str(e)}
            
            
import requests

class SusanGPT:
    @staticmethod
    def edit(txt: str, url: str):
        try:
            api = f"https://api.x7m.site/apis/v2/gemini-img.php?text={requests.utils.quote(txt)}&link={requests.utils.quote(url)}"
            res = requests.get(api, timeout=100).json()
            
            # إذا يحتوي على رابط صورة
            if "image" in res:
                return {"status": "OK", "result": res["image"]}
            elif "url" in res:
                return {"status": "OK", "result": res["url"]}
            else:
                return {"status": "OK", "result": res}
        except Exception as e:
            return {"status": "Error", "message": str(e)}