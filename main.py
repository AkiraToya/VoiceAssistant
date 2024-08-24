from audio import recording, transcribing
from llm import LLMAnswer
import time

llmA = LLMAnswer()

print("Application Start...")

while True:
    if not llmA.isSpeaking:
        live = recording()
        if not live: 
            llmA.setEnd()
            exit()
        result = transcribing()
        llmA.answering(result)
    
    time.sleep(0.5)