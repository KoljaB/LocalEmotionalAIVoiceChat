import json
import threading
import queue
import time
import os
import pyaudio
from RealtimeTTS import TextToAudioStream, CoquiEngine
from lib.sentencequeue import ThreadSafeSentenceQueue, Sentence
from lib.bufferstream import BufferStream

class TTSHandler:
    def __init__(self, config_file='tts_config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.references_folder = self.config['references_folder']
        self.dbg_log = self.config['dbg_log']
        self.stop_event = threading.Event()
        self.sentence_queue = ThreadSafeSentenceQueue()
        self.chunk_queue = queue.Queue()
        self.chunk_lock = threading.Lock()
        
        self.pyFormat = pyaudio.paInt16
        self.pyChannels = 1
        self.pySampleRate = 24000
        self.pyOutput_device_index = None

        print("Loading TTS")
        if self.config['use_local_model']:
            self.engine = CoquiEngine(
                specific_model=self.config['specific_model'],
                local_models_path=self.config['local_models_path']
            )
        else:
            self.engine = CoquiEngine()
        
        self.stream = TextToAudioStream(self.engine, muted=True)

        if self.dbg_log:
            print("Test Play TTS")

        self.stream.feed("hi!")  # only small warmup
        self.stream.play(log_synthesized_text=True, muted=True)

    def initialize_pyaudio(self):
        self.stop_event = threading.Event()
        self.sentence_queue = ThreadSafeSentenceQueue()
        self.chunk_queue = queue.Queue()

        self.pyaudio_instance = pyaudio.PyAudio()
        self.pystream = self.pyaudio_instance.open(
            format=self.pyFormat,
            channels=self.pyChannels,
            rate=self.pySampleRate,
            output_device_index=self.pyOutput_device_index,
            output=True)
        self.pystream.start_stream()

    def tts_play_worker_thread(self):
        while not self.stop_event.is_set():
            if self.chunk_queue.empty():
                time.sleep(0.001)
                continue
            with self.chunk_lock:
                chunk = self.chunk_queue.get()
            self.pystream.write(chunk)

    def start_tts(self):
        def on_audio_chunk(chunk):
            with self.chunk_lock:
                self.chunk_queue.put(chunk)

        self.stream.play_async(
            fast_sentence_fragment=True,
            log_synthesized_text=True,
            muted=True,
            on_audio_chunk=on_audio_chunk,
            minimum_sentence_length=10,
            minimum_first_fragment_length=10,
            context_size=5,
            sentence_fragment_delimiters=".?!;:,\n…)]}。",
            force_first_fragment_after_words=999999,
        )

    def tts_play_sentence(self, sentence: Sentence):
        if sentence.get_finished():
            sentence_text = sentence.get_text()
            if self.dbg_log:
                print(f"tts_play_sentence complete sentence found, playing {sentence_text}")
            self.stream.feed(sentence_text)
            if self.dbg_log:
                print("tts_play_sentence [STARTPLAY]")
            if not self.stream.is_playing():
                self.start_tts()
        else:
            if self.dbg_log:
                print(f"tts_play_sentence running sentence found, realtime playing")
            buffer = BufferStream()
            last_text = ""
            if self.dbg_log:
                print(f"ID: {sentence.id}")
                print(f"EMOTION: {sentence.emotion}")

            while not sentence.get_finished():
                current_text = sentence.get_text()
                if len(current_text) > len(last_text):
                    new_text = current_text[len(last_text):]
                    buffer.add(new_text)
                    if not self.stream.is_playing():
                        self.stream.feed(buffer.gen())
                        self.start_tts()
                last_text = current_text
                time.sleep(0.01)
            if self.dbg_log:
                print(" - feed finished")
            buffer.stop()
        while self.stream.is_playing():
            time.sleep(0.01)

    def tts_sentence_worker_thread(self):
        while not self.stop_event.is_set():
            sentence = self.sentence_queue.get_sentence()

            if sentence:
                emotion = sentence.emotion
                if not emotion or emotion == "None":
                    emotion = "neutral"
                emotion_file = emotion + ".wav"
                path = os.path.join(self.references_folder, emotion_file)
                if os.path.exists(path):
                    if self.dbg_log:
                        print(f"Setting TTS Emotion path: {path}")
                    self.engine.set_cloning_reference(path)
                else:
                    if self.dbg_log:
                        print(f"No emotion found for path: {path}")
                    path = os.path.join(self.references_folder, "neutral.wav")
                    if os.path.exists(path):
                        if self.dbg_log:
                            print(f"Setting neutral: {path}")
                        self.engine.set_cloning_reference(path)
                    else:
                        if self.dbg_log:
                            print(f"CANT FIND EMOTIONS")

                if self.dbg_log:
                    print(f"TTS found a sentence, running: {sentence.get_finished()}")
                    print(f" - finished: {sentence.get_finished()}")
                    print(f" - retrieved: {sentence.retrieved}")
                    print(f" - popped: {sentence.popped}")
                    print(f" - id: {sentence.id}")
                self.tts_play_sentence(sentence)
            
            time.sleep(0.01)

    def start_threads(self):
        self.tts_sentence_thread = threading.Thread(target=self.tts_sentence_worker_thread)
        self.tts_sentence_thread.daemon = True
        self.tts_sentence_thread.start()

        self.tts_play_thread = threading.Thread(target=self.tts_play_worker_thread)
        self.tts_play_thread.daemon = True
        self.tts_play_thread.start()

    def add_text(self, text):
        self.sentence_queue.add_text(text)

    def add_emotion(self, emotion):
        self.sentence_queue.add_emotion(emotion)

    def finish_current_sentence(self):
        self.sentence_queue.finish_current_sentence()

    def is_empty(self):
        return self.sentence_queue.is_empty()

    def is_playing(self):
        return self.stream.is_playing()
    
    def shutdown_pyaudio(self):
        if self.pystream is not None:
            self.pystream.stop_stream()
            self.pystream.close()
        if self.pyaudio_instance is not None:
            self.pyaudio_instance.terminate()

    def shutdown(self):
        self.stop_event.set()
        print("Waiting for sentence thread finished")
        self.tts_sentence_thread.join()
        print("Waiting for play thread finished")
        self.tts_play_thread.join()
        self.engine.shutdown()
