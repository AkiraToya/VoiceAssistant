import subprocess
from tts import speakWav

import threading
import sounddevice as sd

class LLMAnswer:
    systemMessage = '''You are a helpful conversational friend and English teacher.
You will correct user grammar if wrong even in the middle of conversation, but always speak short.
Remember that user message is a transcription, so it can be wrong and you must guess the right word if something feels wrong.
And remember that your response will be converted to speech, so use words for conversation, not text chat.
'''
    chatHistory = []
    text = []
    tempText = ""
    speak = []
    end = False
    isSpeaking = False

    def chatPrompt(self, userMessage):
        chat = f'''<|system|> {self.systemMessage}<|end|>'''
        self.chatHistory.append({
            "role": "user",
            "content": userMessage
        })

        for chatMsg in self.chatHistory[-4:]:
            chat += f'''<|{chatMsg["role"]}|> {chatMsg["content"]}<|end|>'''

        chat += '''<|assistant|>'''

        return chat

    def answering(self, result):
        chat = self.chatPrompt(result)
        # self.end = False
        process = subprocess.Popen(["llm/llamafile-0.8.13.exe", 
                        "-m", "llm/Phi-3.5-mini-instruct-Q4_K_M.gguf",
                        "-ngl", "999",
                        "--ctx-size", "4096",
                        "--no-display-prompt",
                        "-p", chat],
                        stderr=subprocess.DEVNULL,
                        stdout=subprocess.PIPE)    
        
        completeText = ""
        while process.poll() is None:
            line = process.stdout.read(1)
            if not line: break

            try:
                line = line.decode('utf-8', errors='ignore')
            except UnicodeDecodeError:
                continue

            completeText += line

            if line in ".!?:\n":
                self.tempText += line
                self.tempText = self.tempText.replace("*", "")
                self.tempText = self.tempText.replace("\n", "").strip()
                if(self.tempText != ""): self.text.append(self.tempText)
                self.tempText = ""
            else:
                self.tempText += line

        self.chatHistory.append({
            "role": "assistant",
            "content": completeText
        })

    def checkForText(self):
        if len(self.text) > 0:
            self.isSpeaking = True
            curText = ""
            while(len(curText) < 40):
                if len(self.text) > 0: curText += self.text.pop(0)
                else: break

            wav = speakWav(curText)
            if wav is not None: self.speak.append({
                "text": curText,
                "wav": wav
            })

        if(not self.end or len(self.text) > 0): threading.Timer(0.05, self.checkForText).start()

    def checkForSpeak(self):
        if len(self.speak) > 0:
            curSpeak = self.speak.pop(0)
            print(curSpeak["text"])
            sd.play(curSpeak["wav"], samplerate=24000)
            sd.wait()

        if len(self.speak) == 0 and len(self.text) == 0:
            self.isSpeaking = False

        if not self.end or len(self.speak) > 0:
            threading.Timer(0.05, self.checkForSpeak).start()

    def setStart(self):
        self.isSpqwdeaking = True

    def setEnd(self):
        self.end = True

    def clearJob(self):
        self.text = []
        self.speak = []
    
    def __init__(self):
        threading.Timer(0, self.checkForText).start()
        threading.Timer(0, self.checkForSpeak).start()