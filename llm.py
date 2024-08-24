import subprocess
from tts import speakWav

import threading
import sounddevice as sd

class LLMAnswer:

    text = []
    tempText = ""
    completeText = ""
    speak = []
    end = False
    isSpeaking = False

    def answering(self, result):
        prompt = result

        chat = f'''<|system|> You are Angela, a very helpful business conversation AI.<|end|>
<|user|> Hi! nice to meet you, my name is Daryl.<|end|>
<|assistant|> Hello Daryl, nice to meet you too. How can I help you today?<|end|>
<|user|> {prompt}<|end|>
<|assistant|>'''
        # self.end = False
        process = subprocess.Popen(["llm/llamafile-0.8.13.exe", 
                        "-m", "llm/Phi-3.5-mini-instruct-Q4_K_M.gguf",
                        "-ngl", "999",
                        "--ctx-size", "4096",
                        "--no-display-prompt",
                        "-p", chat],
                        stderr=subprocess.DEVNULL,
                        stdout=subprocess.PIPE)    
        
        while process.poll() is None:
            line = process.stdout.read(1)
            if not line: break

            try:
                line = line.decode('utf-8', errors='ignore')
            except UnicodeDecodeError:
                continue

            self.completeText += line

            if line in ".!?:\n":
                self.tempText += line
                self.tempText = self.tempText.replace("*", "")
                self.tempText = self.tempText.replace("\n", "").strip()
                if(self.tempText != ""): self.text.append(self.tempText)
                self.tempText = ""
            else:
                self.tempText += line

        # self.end = True

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