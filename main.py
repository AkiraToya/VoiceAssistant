from audio import AudioProcess
from llm import LLMAnswer
import time
from pynput import keyboard

AP = AudioProcess()
llmA = LLMAnswer()

print("Application Start...")
print("s: speak, esc: cancel speak / exit")

def on_press(key):
    keyType = "normal"
    try:
        key.char
        # print('alphanumeric key {0} pressed'.format(
        #     key.char))
    except AttributeError:
        keyType = "special"
        # print('special key {0} pressed'.format(
        #     key))
        
    if keyType == "normal":
        if key.char == "s":
            AP.isRecording = not AP.isRecording
            # print("Is Recording Status: ",AP.isRecording)
            if AP.isRecording:
                llmA.clearJob()
                # print("Currently Recording...")
                return

            # print("Waiting for processing")
            while not AP.isDoneRecordProcess:
                time.sleep(0.1)

            result = AP.transcribing()
            llmA.answering(result)

    if key == keyboard.Key.esc:
        if AP.isRecording:
            AP.cancelRecording = True
            AP.isRecording = not AP.isRecording
            return
            
        llmA.clearJob()
        llmA.setEnd()
        AP.exit = True
        return False
        
with keyboard.Listener(
        on_press=on_press) as listener:
    listener.join()