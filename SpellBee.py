import pyttsx3
import requests
import speech_recognition as sr
import random
import winsound  # For bell sound on Windows

engine = pyttsx3.init()
recognizer = sr.Recognizer()

def speak(text, times=1):
    for _ in range(times):
        engine.say(text)
        engine.runAndWait()

def fetch_word_data(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        response = requests.get(url)
        data = response.json()

        if isinstance(data, list):
            meaning_data = data[0]['meanings'][0]
            definition = meaning_data['definitions'][0]['definition']
            part_of_speech = meaning_data['partOfSpeech']
            example = meaning_data['definitions'][0].get('example', "No example available.")

            return {
                "definition": definition,
                "part_of_speech": part_of_speech,
                "sentence": example
            }
        else:
            return {
                "definition": "Definition not found.",
                "part_of_speech": "N/A",
                "sentence": "N/A"
            }

    except Exception as e:
        print(f"❌ Error fetching word data: {e}")
        return {
            "definition": "Error occurred.",
            "part_of_speech": "N/A",
            "sentence": "N/A"
        }

def listen_spelling():
    with sr.Microphone() as source:
        print("🎙️ Please spell the word, letter by letter:")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        spoken_text = recognizer.recognize_google(audio)
        print(f"You said: {spoken_text}")
        # Clean input for comparison
        spelled_word = spoken_text.replace(" ", "").replace("-", "").lower()
        return spelled_word
    except sr.UnknownValueError:
        print("❌ Sorry, could not understand. Please try again.")
        return None
    except sr.RequestError as e:
        print(f"❌ Could not request results; {e}")
        return None

def play_bell():
    duration = 300  # milliseconds
    freq = 1000  # Hz
    winsound.Beep(freq, duration)

def spelling_bee(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ Word list file not found.")
        return
    except UnicodeDecodeError:
        print("❌ File encoding error. Please ensure the file is UTF-8 encoded.")
        return

    random.shuffle(words)  # Randomize words order

    for word in words:
        print(f"\n🔊 Listen to the word: ")
        speak(word, times=3)

        while True:
            print("\nSay 'definition', 'part of speech', 'sentence', 'repeat', 'skip', 'over and out' or spell the word letter by letter.")
            user_input = listen_spelling()
            if user_input is None:
                continue

            if user_input in ("overandout", "over and out"):
                print("📴 Ending the spelling bee. Goodbye!")
                speak("Ending the spelling bee. Goodbye!")
                return

            if user_input == "definition":
                print("📖 Definition:", fetch_word_data(word)['definition'])
            elif user_input in ("partofspeech", "part of speech"):
                print("🔤 Part of Speech:", fetch_word_data(word)['part_of_speech'])
            elif user_input == "sentence":
                print("📝 Sentence:", fetch_word_data(word)['sentence'])
            elif user_input == "repeat":
                print("🔁 Repeating the word...")
                speak(word)
            elif user_input == "skip":
                print(f"⏭️ Skipped. Correct spelling was: {word}")
                break
            elif user_input == word.lower():
                print("✅ Correct!")
                speak("Correct!")
                break
            else:
                print("❌ Incorrect spelling. Listen carefully and try again.")
                play_bell()

if __name__ == "__main__":
    file_path = "wordlist.txt"  # Your text file with one word per line
    spelling_bee(file_path)
