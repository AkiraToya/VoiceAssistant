import pyaudio
import wave
import subprocess
import keyboard
import re
from tts import speak

def listAudioInputDevices():
    audio = pyaudio.PyAudio()
    deviceCount = audio.get_device_count()
    
    for i in range(deviceCount):
        deviceInfo = audio.get_device_info_by_index(i)
        if deviceInfo['maxInputChannels'] > 0:
            print(f"Device ID {i}: {deviceInfo['name']}")
    
    audio.terminate()

def getCurrentlyUsedDevices():
    audio = pyaudio.PyAudio()
    usedInputIndex = audio.get_default_input_device_info()['index']
    usedOutputIndex = audio.get_default_output_device_info()['index']

    print(f"Default Input ID: {usedInputIndex}, Output ID: {usedOutputIndex}")
    audio.terminate()

    return usedInputIndex, usedOutputIndex

# listAudioInputDevices()
inputIdx, outputIdx = getCurrentlyUsedDevices()

def recording():
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16, 
        channels=1,
        rate=44100,
        input=True,
        input_device_index=inputIdx,
        frames_per_buffer=1024)

    print("Recording... press 's' to stop recording, 'x' to exit")

    frames = []
    exit = False

    while True:
        data = stream.read(1024)
        frames.append(data)
        if keyboard.is_pressed('s'):
            break
        if keyboard.is_pressed('x'):
            exit = True
            break

    if exit: return False
    print("Recording Finished.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open("output.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
    
    return True

def transcribing():
    process = subprocess.Popen(['whisper/whisper-tiny.en.exe','-f','output.wav', '-np'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()
    stdoutStr = stdout.decode('utf-8').strip()
    pattern = r'\[.*\]\s*'
    stdoutStr = re.sub(pattern, '', stdoutStr, flags=re.MULTILINE).strip()
    returnCode = process.returncode

    if returnCode == 0:
        print(stdoutStr)

    return stdoutStr

def answering(result):
    chat = f'''<|im_start|>system
You are QA bot, answer short.<|im_end|>
<|im_start|>user
{result}<|im_end|>
<|im_start|>assistant'''

    process = subprocess.Popen(['chat/TinyLlama-1.1B-Chat-v1.0.Q4_1.exe', '-e', '-p', chat, '-n', '4096'],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdoutStr = stdout.decode('utf-8').strip()
    returnCode = process.returncode

    stdoutStr = stdoutStr.replace(chat, '').replace('<|im_end|>', '').strip()

    if returnCode == 0:
        print(stdoutStr)

    return stdoutStr

# recording()
# result = transcribing()
# answer = answering(result)
# speak(answer)
