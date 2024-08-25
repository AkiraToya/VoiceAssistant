import pyaudio
import wave
import subprocess
import keyboard
import re
from tts import speak
import time
import threading

class AudioProcess:
    inputIdx = -1
    outputIdx = -1
    isRecording = False
    isDoneRecordProcess = False
    cancelRecording = False
    exit = False

    def __init__(self):
        self.inputIdx, self.outputIdx = self.getCurrentlyUsedDevices()
        threading.Timer(0, self.recording).start()

    def listAudioInputDevices(self):
        audio = pyaudio.PyAudio()
        deviceCount = audio.get_device_count()
        
        for i in range(deviceCount):
            deviceInfo = audio.get_device_info_by_index(i)
            if deviceInfo['maxInputChannels'] > 0:
                print(f"Device ID {i}: {deviceInfo['name']}")
        
        audio.terminate()

    def getCurrentlyUsedDevices(self):
        audio = pyaudio.PyAudio()
        usedInputIndex = audio.get_default_input_device_info()['index']
        usedOutputIndex = audio.get_default_output_device_info()['index']

        print(f"Default Input ID: {usedInputIndex}, Output ID: {usedOutputIndex}")
        audio.terminate()

        return usedInputIndex, usedOutputIndex

    def recording(self):
        if self.exit:
            return
        
        if not self.isRecording:
            threading.Timer(0.05, self.recording).start()
            return
        
        print("Please speak...")
        self.isDoneRecordProcess = False

        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16, 
            channels=1,
            rate=44100,
            input=True,
            input_device_index=self.inputIdx,
            frames_per_buffer=1024)

        frames = []

        while True:
            data = stream.read(1024)
            frames.append(data)

            if self.cancelRecording:
                print("Cancel recording")
                stream.stop_stream()
                stream.close()
                audio.terminate()
                self.cancelRecording = False
                self.isDoneRecordProcess = True
        
                if not self.exit: threading.Timer(0.05, self.recording).start()
                
                return

            if not self.isRecording:
                break

        print("Recording Finished.")

        stream.stop_stream()
        stream.close()
        audio.terminate()

        with wave.open("output.wav", "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(frames))

        self.isDoneRecordProcess = True
        
        if not self.exit: threading.Timer(0.05, self.recording).start()
        return True

    def transcribing(self):
        process = subprocess.Popen(['whisper/whisper-small.exe','-f','output.wav', '-np', '--gpu', 'auto'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()
        stdoutStr = stdout.decode('utf-8').strip()
        pattern = r'\[.*\]\s*'
        stdoutStr = re.sub(pattern, '', stdoutStr, flags=re.MULTILINE).strip()
        returnCode = process.returncode

        if returnCode == 0:
            print(stdoutStr)

        return stdoutStr