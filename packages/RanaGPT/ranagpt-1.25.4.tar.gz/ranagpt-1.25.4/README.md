RanaGPT

RanaGPT is a free, powerful Python library designed to provide easy access to a variety of advanced AI models and tools. It offers a unified and straightforward interface to interact with multiple AI-powered features such as text generation, voice AI, chatbots, image generation, code assistance, and more — all available for free without complex setup.


---

Installation

Install RanaGPT quickly using pip:

```bash
pip install RanaGPT
```


---

Features and Modules

RanaGPT provides a rich set of AI modules to cover many use cases:

VoiceAi

Generate human-like speech from text using OpenAI-powered voices.

Supported voices: alloy, coral, echo, shimmer, verse, onyx.

Supported styles: friendly, calm, noir_detective, cowboy.

Example:

from RanaGPT import VoiceAi

# Default voice (alloy)
response = VoiceAi.openai("Welcome to the service RanaGPT")
print(response.get("result"))

# Custom voice and style
response = VoiceAi.openai(
    text="hello",
    voice="echo",       # alloy, coral, echo, shimmer, verse, onyx
    style="calm"        # friendly, calm, noir_detective, cowboy
)
print(response.get("result"))


TextAi

DeepInfra models: deepseekv3, deepseekv3x, deepseekr1, deepseekr1base, deepseekr1turbo, deepseekr1llama, deepseekr1qwen, deepseekprover, qwen235, qwen30, qwen32, qwen14, mav, scout, phi-plus, guard, qwq, gemma27, gemma12, llama31, llama332, llama337, mixtral24, phi4, phi-multi, wizard822, wizard27, qwen2572, qwen272, dolphin26, dolphin29, airo70, lzlv70, mixtral822.

Example:

from RanaGPT import TextAi
response = TextAi.DeepInfra("Write a poem about nature.", "deepseekv3")
print(response.get("result"))


WormGpt

TofeyGPT and Worm: conversational AI models with special endpoints.


Model31

Access popular LLMs such as grok, gpt-4, gpt-4o, gpt-4-1, gpt-4-1-mini, o4-mini, command-r-plus, gemini-2-5-flash, gemini-2-0-flash-thinking, qwen-2-5-coder-32b, llama-3-3-70b, llama-4-scout, llama-4-scout-17b, mistral-small-3-1-24b, phi-4, and others.


BlackBox

Specialized models for programming and software development tasks.


ModelDeepInfra

Returns the full list of DeepInfra models for dynamic usage.


Developers

Utility functions and info, including developer contacts and quotes.


ImageAi

Supported models: fluex-pro, flux, schnell, imger-12, deepseek, gemini-2-5-pro, blackbox, redux, RanaGPT-7-i, r1, gpt-4-1.

Generate images from text prompts.


ChatAi

Lightweight chat interface using GPT-3.5.


AzkarApi

Daily Islamic supplications and prayers.


DeepSeekT1

Code generation and understanding assistance.


GeminiApi

Access to Gemini conversational models.



---

How to Use

Basic usage with TextAi module:

from RanaGPT import TextAi

prompt = "Write a short story about friendship."
response = TextAi.DeepInfra(prompt, "deepseekv3")
print(response.get("result", "No response received."))

Listing available models:

from RanaGPT import TextAi
models = TextAi.models()
print("Available TextAi models:", models)


---

Response Handling

Most functions return a dict with at least:

status: "OK", "Error", or "Bad".

result: main output or raw response.

error: error message if applicable.


if response.get("status") == "OK":
    print(response.get("result"))
else:
    print("Error:", response.get("error", "Unknown error"))


---

Telegram Bot Integration

Easily integrate RanaGPT into Telegram bots:

Let users select modules and models.

Respond with AI-generated text, voice, or images.

Customize bot behavior dynamically.



---

Advantages

Free to use: No cost barriers for advanced AI.

Unified library: Multiple AI modules in one package.

Simple API: Start quickly without complex setup.

Multilingual: Supports Arabic and English out of the box.



---

Requirements

Python 3.7+

requests, beautifulsoup4, mnemonic, pycountry, user_agent



---

Contributing & Support

Contributions, bug reports, and feature requests are welcome! Open issues on GitHub or contact the maintainer.


---

Owner's Telegram: https://t.me/qqxqqv
Owner's Telegram Channel: https://t.me/RanaGPT
Owner's Instagram: https://www.instagram.com/f8__x# RanaGPT
