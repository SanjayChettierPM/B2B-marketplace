import streamlit as st
import openai
# import pyttsx3
import speech_recognition as sr
import time, base64
import os
import anthropic
from gtts import gTTS

openai.api_key = os.environ.get("OPENAI_API_KEY", "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")
anthropic.api_key = os.environ.get("ANTHROPIC_API_KEY", "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")

# engine = pyttsx3.init()

def transcribe_audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        return None

def generate_response(prompt, model):
    if model == "gpt-3.5-turbo-0125":
        client = openai
        temperature = 1
        max_tokens = 500
        input_cost_per_token = 0.000042
        output_cost_per_token = 0.00013
    elif model == "gpt-4-turbo":
        client = openai
        temperature = 1
        max_tokens = 500
        input_cost_per_token = 0.00083
        output_cost_per_token = 0.0025
    elif model == "claude-3-haiku-20240307":
        client = anthropic.Anthropic(api_key=anthropic.api_key)
        temperature = 1
        max_tokens = 1000
        input_cost_per_token = 0.000021
        output_cost_per_token = 0.00010
    else:
        return "Error: Invalid model selected."

    start_time = time.time()

    if model.startswith("gpt"):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        response_text = response.choices[0].message.content
    else:
        # For non-GPT models, directly return the response
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = message.content[0].text

    elapsed_time = time.time() - start_time
    input_tokens_consumed = len(prompt.split())
    output_tokens_consumed = len(response_text.split()) if response_text else 0
    total_tokens_consumed = input_tokens_consumed + output_tokens_consumed
    input_cost = input_tokens_consumed * input_cost_per_token
    output_cost = output_tokens_consumed * output_cost_per_token
    total_cost = input_cost + output_cost

    return response_text, elapsed_time, total_tokens_consumed, total_cost

# def speak_text(text):
#     engine.say(text)
#     engine.runAndWait()
    
    
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )
        
    
def speak_test(text):
    tts = gTTS(text)
    tts.save('test.mp3')
    autoplay_audio('test.mp3')
    

def main():
    st.title("AI Chat Interface")

    input_type = st.selectbox("Input Type:", ["Text", "Voice"])

    model_text = st.selectbox("Model:", ["gpt-3.5-turbo-0125", "gpt-4-turbo", "claude-3-haiku-20240307"])
    if input_type == "Text":
        question = st.text_area("Question:")
        if st.button("Submit"):
            response_data = generate_response(question, model_text)
            if isinstance(response_data, str):
                st.error(response_data)
            else:
                response, elapsed_time, total_tokens_consumed, total_cost = response_data
                st.markdown("## Response:")
                
                st.write(response)
                st.markdown("## Details:")
                st.write(f"- Elapsed Time: {elapsed_time}")
                st.write(f"- Tokens Consumed: {total_tokens_consumed}")
                st.write(f"- Cost: {total_cost}")
                st.markdown("---")
                speak_test(response)
                follow_up_question = st.text_input("Follow-up Question:")
                if follow_up_question:
                    st.markdown("## Follow-up Question:")
                    st.write(follow_up_question)

    elif input_type == "Voice":
        st.warning("Click 'Start Recording' to begin speaking.")
        if st.button("Start Recording"):
            with st.spinner("Recording..."):
                filename = "input.wav"
                with sr.Microphone() as source:
                    recognizer = sr.Recognizer()
                    audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
                    with open(filename, "wb") as f:
                        f.write(audio.get_wav_data())
                question = transcribe_audio_to_text(filename)
                if not question:
                    st.error("Error: Kindly speak more clearly")
                    return
                else:
                    response_data = generate_response(question, model_text)
                    if isinstance(response_data, str):
                        st.error(response_data)
                    else:
                        response, elapsed_time, total_tokens_consumed, total_cost = response_data
                        st.markdown("## Response:")
                        st.write(response)
                        st.markdown("## Details:")
                        st.write(f"- Elapsed Time: {elapsed_time}")
                        st.write(f"- Tokens Consumed: {total_tokens_consumed}")
                        st.write(f"- Cost: {total_cost}")
                        st.markdown("---")
                        follow_up_question = st.text_input("Follow-up Question:")
                        if follow_up_question:
                            st.markdown("## Follow-up Question:")
                            st.write(follow_up_question)

                            # Generate follow-up question suggestions
                            if "document" in question.lower():
                                st.markdown("### Suggested Follow-up Question:")
                                st.write("What do you want me to do with this document? Summarize it, analyze it, or something else?")
                            elif "weather" in question.lower():
                                st.markdown("### Suggested Follow-up Question:")
                                st.write("Would you like to know the weather in your location?")
                            # Add more conditions and suggestions as needed

if __name__ == "__main__":
    main()