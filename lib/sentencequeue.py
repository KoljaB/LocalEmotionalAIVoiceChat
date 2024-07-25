import threading
from typing import Optional
import uuid

class Sentence:
    def __init__(self, emotion: Optional[str] = None):
        self.text = ""
        self.emotion = emotion
        self.is_finished = False
        self.retrieved = False
        self.popped = False
        self.lock = threading.Lock()
        self.id: str = str(uuid.uuid4())

    def add_text(self, text: str):
        with self.lock:
            self.text += text

    def get_text(self):
        with self.lock:
            return self.text

    def mark_finished(self):
        with self.lock:
            self.is_finished = True

    def get_finished(self):
        with self.lock:
            return self.is_finished

    def __str__(self):
        with self.lock:
            return f"Sentence(text='{self.text}', emotion='{self.emotion}', is_finished={self.is_finished})"

class ThreadSafeSentenceQueue:
    def __init__(self):
        self.queue = []
        self.current_sentence = None
        self.lock = threading.Lock()

    def finish_current_sentence(self):
        with self.lock:
            if self.current_sentence and not self.current_sentence.is_finished:
                self.current_sentence.mark_finished()
                if not self.current_sentence.retrieved:
                    self.queue.append(self.current_sentence)
                self.current_sentence = None

    def add_emotion(self, emotion: str):
        with self.lock:
            if self.current_sentence and self.current_sentence.get_text():
                self.current_sentence.mark_finished()
                if not self.current_sentence.retrieved:
                    self.queue.append(self.current_sentence)
            self.current_sentence = Sentence(emotion)

    def add_text(self, text: str):
        with self.lock:
            # print(f"Text: {text}, not text.strip(): {not text.strip()}, not self.current_sentence: {not self.current_sentence}")
            # if self.current_sentence:
            #     print(f"not self.current_sentence.get_text(): {not self.current_sentence.get_text()}")

            if not text.strip():
                if not self.current_sentence:
                    return
                if not self.current_sentence.get_text():
                    return

            if not self.current_sentence:
                self.current_sentence = Sentence()
            
            #print(f"added {text} to sentence {self.current_sentence.id}")
            self.current_sentence.add_text(text)

    def get_sentence(self) -> Optional[Sentence]:
        with self.lock:
            if self.queue:
                sentence = self.queue.pop(0)
                sentence.popped = True
                return sentence
            elif self.current_sentence:
                self.current_sentence.retrieved = True
                return self.current_sentence
            else:
                return None

    def is_empty(self) -> bool:
        with self.lock:
            return len(self.queue) == 0

    def __len__(self):
        with self.lock:
            return len(self.queue)