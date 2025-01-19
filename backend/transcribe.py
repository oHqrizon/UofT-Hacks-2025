import argparse
import os
import numpy as np
import speech_recognition as sr
import whisper
import torch
import threading
from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform

class TranscriptionService:
    def __init__(self, model="medium", energy_threshold=1000, record_timeout=2, phrase_timeout=3):
        print("Initializing TranscriptionService...")
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.dynamic_energy_threshold = False
        
        # Initialize microphone
        print("Initializing microphone...")
        if 'linux' in platform:
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if 'pulse' in name:
                    self.microphone = sr.Microphone(sample_rate=16000, device_index=index)
                    break
        else:
            self.microphone = sr.Microphone(sample_rate=16000)
        print("Microphone initialized")
            
        # Load Whisper model
        print("Loading Whisper model...")
        model_name = f"{model}.en" if model != "large" else model
        self.audio_model = whisper.load_model(model_name)
        print("Whisper model loaded")
        
        self.record_timeout = record_timeout
        self.phrase_timeout = phrase_timeout
        self.is_recording = False
        self.transcription = ['']
        self.data_queue = Queue()
        self.phrase_time = None
        self.last_write_time = datetime.utcnow()
        print("TranscriptionService initialization complete")
        
    def record_callback(self, _, audio: sr.AudioData) -> None:
        """Callback function to receive audio data when recordings finish."""
        try:
            data = audio.get_raw_data()
            self.data_queue.put(data)
            print("Audio data received")
        except Exception as e:
            print(f"Error in record_callback: {e}")
        
    def start_recording(self):
        """Start the transcription process"""
        try:
            print("Starting recording...")
            self.is_recording = True
            
            # Adjust for ambient noise
            print("Adjusting for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
            
            # Start background listening
            print("Starting background listening...")
            self.stop_listening = self.recognizer.listen_in_background(
                self.microphone, 
                self.record_callback, 
                phrase_time_limit=self.record_timeout
            )
            
            # Start processing in a separate thread
            print("Starting audio processing thread...")
            thread = threading.Thread(target=self.process_audio)
            thread.daemon = True
            thread.start()
            print("Recording started successfully")
        except Exception as e:
            print(f"Error in start_recording: {e}")
            raise
        
    def process_audio(self):
        """Process audio data and update transcription"""
        print("Audio processing started")
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
                    print(f"Transcribed text: {text}")
                    
                    # Update transcription
                    if phrase_complete:
                        self.transcription.append(text)
                    else:
                        self.transcription[-1] = text
                    
                    # Write to file every 10 seconds
                    if (now - self.last_write_time).total_seconds() >= 10:
                        os.makedirs("transcripts", exist_ok=True)
                        with open(os.path.join("transcripts", "transcription.txt"), "w") as f:
                            for line in self.transcription:
                                f.write(line + "\n")
                        print("Transcription saved to file")
                        self.last_write_time = now
                        
                else:
                    sleep(0.25)
                    
            except Exception as e:
                print(f"Error in processing audio: {e}")
                continue
                
    def stop_recording(self):
        """Stop the transcription process"""
        try:
            print("Stopping recording...")
            if hasattr(self, 'stop_listening'):
                self.stop_listening(wait_for_stop=False)  # Stop the background listener
            self.is_recording = False
            
            # Write final transcription
            os.makedirs("transcripts", exist_ok=True)
            with open(os.path.join("transcripts", "transcription.txt"), "w") as f:
                for line in self.transcription:
                    f.write(line + "\n")
            print("Final transcription saved")
        except Exception as e:
            print(f"Error in stop_recording: {e}")
            raise 