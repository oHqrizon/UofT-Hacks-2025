import argparse
import os
import numpy as np
import speech_recognition as sr
import whisper
import torch
from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform

class TranscriptionService:
    def __init__(self, model="medium", energy_threshold=1000, record_timeout=2, phrase_timeout=3):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.dynamic_energy_threshold = False
        
        # Initialize microphone
        if 'linux' in platform:
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if 'pulse' in name:
                    self.microphone = sr.Microphone(sample_rate=16000, device_index=index)
                    break
        else:
            self.microphone = sr.Microphone(sample_rate=16000)
            
        # Load Whisper model
        model_name = f"{model}.en" if model != "large" else model
        self.audio_model = whisper.load_model(model_name)
        
        self.record_timeout = record_timeout
        self.phrase_timeout = phrase_timeout
        self.is_recording = False
        self.transcription = ['']
        self.data_queue = Queue()
        self.phrase_time = None
        self.last_write_time = datetime.utcnow()
        
    def record_callback(self, _, audio: sr.AudioData) -> None:
        """Callback function to receive audio data when recordings finish."""
        data = audio.get_raw_data()
        self.data_queue.put(data)
        
    def start_recording(self):
        """Start the transcription process"""
        self.is_recording = True
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        
        # Start background listening
        self.recognizer.listen_in_background(
            self.microphone, 
            self.record_callback, 
            phrase_time_limit=self.record_timeout
        )
        
        # Start processing thread
        self.process_audio()
        
    def process_audio(self):
        """Process audio data and update transcription"""
        while self.is_recording:
            try:
                now = datetime.utcnow()
                if not self.data_queue.empty():
                    phrase_complete = False
                    if self.phrase_time and now - self.phrase_time > timedelta(seconds=self.phrase_timeout):
                        phrase_complete = True
                    self.phrase_time = now
                    
                    # Process audio data
                    audio_data = b''.join(self.data_queue.queue)
                    self.data_queue.queue.clear()
                    
                    audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                    
                    # Transcribe using Whisper
                    result = self.audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
                    text = result['text'].strip()
                    
                    # Update transcription
                    if phrase_complete:
                        self.transcription.append(text)
                    else:
                        self.transcription[-1] = text
                    
                    # Write to file every 10 seconds
                    if (now - self.last_write_time).total_seconds() >= 10:
                        os.makedirs("speech", exist_ok=True)
                        with open(os.path.join("speech", "transcription.txt"), "w") as f:
                            for line in self.transcription:
                                f.write(line + "\n")
                        self.last_write_time = now
                        
                else:
                    sleep(0.25)
                    
            except Exception as e:
                print(f"Error in processing audio: {e}")
                continue
                
    def stop_recording(self):
        """Stop the transcription process"""
        self.is_recording = False
        
        # Write final transcription
        os.makedirs("speech", exist_ok=True)
        with open(os.path.join("speech", "transcription.txt"), "w") as f:
            for line in self.transcription:
                f.write(line + "\n")

# Example usage
if __name__ == "__main__":
    service = TranscriptionService()
    service.start_recording()
    
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        service.stop_recording()
        print("\nTranscription stopped") 