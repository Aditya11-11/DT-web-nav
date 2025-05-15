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



Explanation
Setting API Key and Prompts:

/api/set_api_key – Accepts a JSON body with "api_key" and stores it in the global variable.

/api/set_prompt – Accepts a manual prompt via a JSON body and stores it in the system_prompt["manual"] key.

/api/set_navigation_commands – Accepts a JSON object mapping keywords (e.g. "dashboard") to URLs. These are stored in navigation_commands and also used to update system_prompt["url"] (formatted as a list).

Retrieving the Combined Prompt:

/api/get_prompt – Returns the combined prompt (manual prompt and navigation commands) which is later passed to the LLM.

Chat and Voice Assistant Endpoints:

/chat – Accepts a JSON with "human_message", calls the LLM using the combined prompt, and checks for navigation commands to add a redirect URL if found.

/voice_assistant – Accepts an audio file, uses a Whisper model to transcribe it, sends the transcription to the LLM, and converts the LLM response to speech (using Edge‑TTS). It also checks for navigation commands.

Navigation Commands Handling:

When either the text chat or voice assistant endpoint is called, the code checks whether the combined text (human message plus LLM response) contains words like "navigate" or "redirect" along with one of the navigation command keywords. If so, it returns a "redirect_url" in the JSON response.

This design lets you dynamically update both the manual prompt and the navigation command URLs separately. The combined prompt is then used to instruct the LLM, and navigation commands trigger redirection in the chat response.

You can now deploy this app on any cloud hosting platform that supports Python


component was called in navbar.jsxas Chatbot 