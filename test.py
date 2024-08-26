from audio import AudioProcess
from llm import LLMAnswer

llmA = LLMAnswer()
AP = AudioProcess()
AP.answerFn = llmA.answering
AP.isRecording = True