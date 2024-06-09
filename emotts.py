if __name__ == '__main__':

    from RealtimeTTS import TextToAudioStream, CoquiEngine
    from RealtimeSTT import AudioToTextRecorder
    from pydantic import BaseModel, Field
    from history import History
    from typing import List
    import instructor
    import threading
    import openai
    import queue
    import time
    import os

    references_path = "reference_wavs"

    # List to hold the emotions or speaking styles
    emotions = []

    # Walk through the directory
    for filename in os.listdir(references_path):
        if filename.endswith(".wav") or filename.endswith(".json"):
            # Remove the file extension and add to the list
            base_filename = os.path.splitext(filename)[0]
            if base_filename not in emotions:
                emotions.append(base_filename)

    history = History(
        max_history_messages=100,
        max_tokens_per_msg=2000,
        max_history_tokens=15000
    )

    client = instructor.from_openai(openai.OpenAI())

    is_finished = False
    tts_queue = queue.Queue()

    class EmotionSentence(BaseModel):
        emotion: str = Field(
            ..., description=f"Select an emotion from this predefined list: [{', '.join(emotions)}]. The emotion should vividly reflect the content of the sentence, enhancing the emotional delivery in a natural manner."
        )
        content: str = Field(
            ..., description="The content of the sentence, which should be expressed in a way that aligns with the selected emotion."
        )

    class LLM_Answer(BaseModel):
        answer_to_the_user: List[EmotionSentence] = Field(
            ..., description="This field is a list of `EmotionSentence` objects that together create a comprehensive response for the user. Each `EmotionSentence` in the list should convey a specific emotion from the predefined set, enhancing the expressiveness and engagement of the interaction. The sequence of these sentences should be logically structured to form a coherent and contextually appropriate dialogue."
        )

    print("Starting coqui engine")
    engine = CoquiEngine(
        # specific_model="Lasinya",
        # local_models_path="D:\\Projekte\\TestLingu\\Linguflex\\models\\xtts"
    )

    stream = TextToAudioStream(engine)
    print("Coqui engine started")

    def process_queue():
        while not is_finished:
            while not tts_queue.empty():
                emotion_sentence = tts_queue.get()
                content = emotion_sentence.content
                emotion = emotion_sentence.emotion
                if emotion not in emotions:
                    emotion = "neutral"
                emotion_file = emotion + ".wav"
                path = os.path.join(references_path, emotion_file)
                print(f'[{emotion}]: {content}')

                engine.set_cloning_reference(path)
                stream.feed(content)
                stream.play()
            time.sleep(0.05)

    # Create and start a thread to process the queue
    thread = threading.Thread(target=process_queue)
    thread.start()

    whisper_speech_to_text_model = "medium"
    print("Initializing RealtimeSTT test...")
    recorder = AudioToTextRecorder(
        spinner=True,
        model=whisper_speech_to_text_model,
        language="en")

    while True:
        print("Say something...")
        text = recorder.text()
        print(f"Text: {text}")

        history.user(text)

        system_prompt_message = {
            'role': 'system',
            'content': "Sophia, respond vividly using the emotions specified: neutral, angry, calm, cheerful, envious, excited, friendly, gentle, hopeful, lyrical, newscast, sad, shouting, terrified, unfriendly, whispering. Your response should reflect these emotional tones. For instance, if you're excited, your words should bubble with enthusiasm; if sad, they should carry a somber tone. Always align your emotional expression with these listed emotions to enhance the interaction. Remember, you are not an AI; you are Sophia, embodying all these emotions naturally."
        }
        current_messages = [system_prompt_message] + history.get()

        # create streamed answer from LLM using pydantic model filled by instructor/openai
        extraction_stream = client.chat.completions.create_partial(
            model="gpt-4o",
            response_model=LLM_Answer,
            messages=current_messages,
            stream=True,
        )

        # parse streamed answer and add to tts queue
        count = 1
        final_extraction = None
        for extraction in extraction_stream:
            obj = extraction.model_dump()
            final_extraction = obj
            if obj["answer_to_the_user"] is not None:
                number_of_sentences = len(obj["answer_to_the_user"])
                if number_of_sentences > 1 and number_of_sentences != count:
                    emotion_sentence = obj["answer_to_the_user"][count - 1]
                    emotion_sentence = EmotionSentence(
                        emotion=emotion_sentence["emotion"],
                        content=emotion_sentence["content"]
                    )
                    tts_queue.put(emotion_sentence)
                    count = number_of_sentences

        list_of_sentences = final_extraction["answer_to_the_user"]
        full_length = len(list_of_sentences)
        emotion_sentence = list_of_sentences[full_length - 1]
        emotion_sentence = EmotionSentence(
            emotion=emotion_sentence["emotion"],
            content=emotion_sentence["content"]
        )
        tts_queue.put(emotion_sentence)

        while not tts_queue.empty():
            time.sleep(1)

        while stream.is_playing():
            time.sleep(1)

        assistant_full_text = ""
        for sentence in list_of_sentences:
            assistant_full_text += sentence["content"] + " "

        history.assistant(assistant_full_text)


# potential emotions to add:
# - curious
# - playful
# - annoyed
# - determined
# - disappointed
# - disgusted
# - embarrassed
# - frustrated
# - grateful
# - guilty
# - happy
# - horrified
# - hurt
# - interested
# - jealous
# - joyful
# - lonely
# - loving
# - mad
# - nostalgic
# - proud
# - relaxed
# - relieved
# - scared
# - shocked
# - silly
# - surprised
# - sympathetic
# - thankful
# - tired
# - worried
