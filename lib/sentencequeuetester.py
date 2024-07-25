import threading
import time
from typing import Optional
from sentencequeue import ThreadSafeSentenceQueue, Sentence


# Include the updated ThreadSafeSentenceQueue and Sentence classes here

def test_sentence_queue():
    queue = ThreadSafeSentenceQueue()

    # Test 1: Basic functionality and live updates
    queue.add_emotion("happy")
    queue.add_text("Hello, ")
    #sentence = queue.get_sentence()
    #assert sentence is None, f"Test 1a failed. Got: {sentence}"
    queue.add_text("world!")
    queue.finish_current_sentence()
    sentence = queue.get_sentence()
    assert str(sentence) == "Sentence(text='Hello, world!', emotion='happy', is_finished=True)", f"Test 1b failed. Got: {sentence}"
    print("Test 1 passed: Basic functionality and live updates")

    # Test 2: Multiple sentences with emotion changes
    queue.add_emotion("sad")
    queue.add_text("Goodbye, ")
    queue.add_emotion("angry")  # This should finish the previous sentence and start a new one
    queue.add_text("cruel ")
    queue.add_text("world!")
    queue.finish_current_sentence()

    sentence1 = queue.get_sentence()
    sentence2 = queue.get_sentence()
    assert str(sentence1) == "Sentence(text='Goodbye, ', emotion='sad', is_finished=True)", f"Test 2a failed. Got: {sentence1}"
    assert str(sentence2) == "Sentence(text='cruel world!', emotion='angry', is_finished=True)", f"Test 2b failed. Got: {sentence2}"
    print("Test 2 passed: Multiple sentences with emotion changes")

    # Test 3: Empty queue behavior
    empty_sentence = queue.get_sentence()
    assert empty_sentence is None, f"Test 3 failed. Got: {empty_sentence}"
    print("Test 3 passed: Empty queue behavior")

    # Test 4: Thread safety, live updates, and consistent sentence length
    def worker(worker_id):
        for i in range(100):
            queue.add_emotion(f"emotion{worker_id}")
            queue.add_text("This ")
            queue.add_text("is ")
            queue.add_text("test ")
            queue.add_text("sentence ")
            queue.add_text(f"{i}. ")
            queue.finish_current_sentence()

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for thread in threads:
        thread.start()

    # Simulate a TTS thread reading sentences
    tts_sentences = []
    start_time = time.time()
    timeout = 10  # Set a timeout of 10 seconds
    while len(tts_sentences) < 500 and time.time() - start_time < timeout:
        sentence = queue.get_sentence()
        if sentence:
            tts_sentences.append(sentence)
        time.sleep(0.001)  # Simulate some processing time

    for thread in threads:
        thread.join()

    assert len(tts_sentences) == 500, f"Test 4 failed. Expected 500 sentences, got {len(tts_sentences)}"
    assert all(s.is_finished for s in tts_sentences), "Test 4 failed. Not all sentences are marked as finished"
    assert all(len(s.text.split()) == 5 for s in tts_sentences), f"Test 4 failed. Not all sentences have 5 words. Example: {next((s for s in tts_sentences if len(s.text.split()) != 5), None)}"
    print(f"Test 4 passed: Thread safety, live updates, and consistent sentence length. Processed {len(tts_sentences)} sentences.")

    print("All tests passed successfully!")

if __name__ == "__main__":
    test_sentence_queue()


# import threading
# import time
# from typing import Optional
# from sentencequeue import ThreadSafeSentenceQueue, Sentence

# # Include the updated ThreadSafeSentenceQueue and Sentence classes here

# def test_sentence_queue():
#     queue = ThreadSafeSentenceQueue()

#     # Test 1: Basic functionality and live updates
#     queue.add_emotion("happy")
#     queue.add_text("Hello, ")
#     sentence = queue.get_sentence()
#     assert str(sentence) == "Sentence(text='Hello, ', emotion='happy', is_finished=False)", f"Test 1a failed. Got: {sentence}"
#     queue.add_text("world!")
#     assert str(sentence) == "Sentence(text='Hello, world!', emotion='happy', is_finished=False)", f"Test 1b failed. Got: {sentence}"
#     queue.finish_current_sentence()
#     assert str(sentence) == "Sentence(text='Hello, world!', emotion='happy', is_finished=True)", f"Test 1c failed. Got: {sentence}"
#     print("Test 1 passed: Basic functionality and live updates")

#     # Test 2: Multiple sentences with emotion changes
#     queue.add_emotion("sad")
#     queue.add_text("Goodbye, ")
#     queue.add_emotion("angry")  # This should finish the previous sentence and start a new one
#     queue.add_text("cruel ")
#     queue.add_text("world!")
#     queue.finish_current_sentence()

#     sentence1 = queue.get_sentence()
#     sentence2 = queue.get_sentence()
#     assert str(sentence1) == "Sentence(text='Goodbye, ', emotion='sad', is_finished=True)", f"Test 2a failed. Got: {sentence1}"
#     assert str(sentence2) == "Sentence(text='cruel world!', emotion='angry', is_finished=True)", f"Test 2b failed. Got: {sentence2}"
#     print("Test 2 passed: Multiple sentences with emotion changes")

#     # Test 3: Empty queue behavior
#     empty_sentence = queue.get_sentence()
#     assert empty_sentence is None, f"Test 3 failed. Got: {empty_sentence}"
#     print("Test 3 passed: Empty queue behavior")

#     # Test 4: Thread safety and live updates
#     def worker(worker_id):
#         for i in range(100):
#             queue.add_emotion(f"emotion{worker_id}")
#             for j in range(5):
#                 queue.add_text(f"Text {j} ")
#                 time.sleep(0.001)  # Simulate some processing time
#             queue.finish_current_sentence()

#     threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
#     for thread in threads:
#         thread.start()

#     # Simulate a TTS thread reading sentences
#     tts_sentences = []
#     while len(tts_sentences) < 500 or not all(s.is_finished for s in tts_sentences):
#         sentence = queue.get_sentence()
#         if sentence and sentence not in tts_sentences:
#             tts_sentences.append(sentence)
#         time.sleep(0.001)  # Simulate some processing time

#     for thread in threads:
#         thread.join()

#     assert len(tts_sentences) == 500, f"Test 4 failed. Expected 500 sentences, got {len(tts_sentences)}"
#     assert all(s.is_finished for s in tts_sentences), "Test 4 failed. Not all sentences are marked as finished"
#     assert all(len(s.text.split()) == 5 for s in tts_sentences), "Test 4 failed. Not all sentences have 5 words"
#     print(f"Test 4 passed: Thread safety and live updates. Processed {len(tts_sentences)} sentences.")

#     print("All tests passed successfully!")

# if __name__ == "__main__":
#     test_sentence_queue()