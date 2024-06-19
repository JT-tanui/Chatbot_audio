import requests
import nltk
from nltk.chat.util import Chat, reflections
from textblob import TextBlob
import requests
import speech_recognition as sr
from gtts import gTTS
import os

# Define conversation pairs
pairs = [
    ['my name is (.*)', ['Hello %1, how can I help you today?']],
    ['hi|hello|hey', ['Hello!', 'Hey there!']],
    ['what is your name?', ['I am a chatbot created by you.']],
    ['how are you?', ['I am just a bunch of code, but thanks for asking!']],
    ['tell me a joke', ['Why don’t scientists trust atoms? Because they make up everything!']],
    ['quit', ['Bye! Take care.']],
    ['(.*) weather in (.*)', ['Let me check the weather in %2 for you.']],
    ['i am feeling (.*)', ['I am sorry to hear that you are feeling %1.']]
]

chat = Chat(pairs, reflections)

# Weather API key (use your own API key here)
api_key = 'a1c3064d665bfa00b550c7ef1d3d8bf6'
base_url = 'http://api.openweathermap.org/data/2.5/weather?'

# Initialize the speech recognition engine
recognizer = sr.Recognizer()

def get_audio():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")
    os.system("afplay output.mp3")  # macOS
    # os.system("start output.mp3")  # Windows
    # os.system("mpg123 output.mp3")  # Linux

def get_weather(city):
    complete_url = base_url + 'appid=' + api_key + '&q=' + city
    response = requests.get(complete_url)
    data = response.json()
    if data['cod'] != '404':
        main = data['main']
        weather_desc = data['weather'][0]['description']
        temp = main['temp']
        return f'Temperature: {temp}K\nWeather Description: {weather_desc}'
    else:
        return 'City Not Found'

def analyze_sentiment(sentence):
    blob = TextBlob(sentence)
    return blob.sentiment.polarity

def chatbot():
    print("Hi, I am your enhanced chatbot. Type 'quit' to exit.")
    speak("Hi, I am an enhanced chatbot, am still experimental so just hold on. Type 'quit' to exit.")
    while True:
        try:
            # Use speech recognition to get user input
            user_input = get_audio()
            if not user_input:
                continue

            if user_input.lower() == 'quit':
                print('Bye! Take care.')
                speak('Bye! Take care.')
                break
            elif 'weather' in user_input:
                city = user_input.split('in ')[-1]
                weather_info = get_weather(city)
                print(weather_info)
                speak(weather_info)
            elif 'feeling' in user_input:
                sentiment = analyze_sentiment(user_input)
                if sentiment < -0.1:
                    print("I'm sorry you're feeling down. Can I do anything to help?")
                    speak("I'm sorry you're feeling down. Can I do anything to help?")
                else:
                    print("It's great that you're feeling good!")
                    speak("It's great that you're feeling good!")
            else:
                bot_response = chat.respond(user_input)
                print(bot_response)
                speak(bot_response)
        except Exception as e:
            print(f"An error occurred: {e}")
# Add this function to fetch news headlines
def get_news():
    api_key = 'YOUR_NEWS_API_KEY'
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()
    if news_data['status'] == 'ok':
        articles = news_data['articles'][:5]  # Get the top 5 headlines
        headlines = [article['title'] for article in articles]
        return '\n'.join(headlines)
    else:
        return 'Unable to fetch news at the moment.'

# Add a new pair to the chatbot pairs for news
pairs.append(['tell me the news', ['Here are the latest headlines:\n%s' % get_news()]])

# Update the chatbot function to handle the news request
def chatbot():
    print("Hi, I am your enhanced chatbot. Type 'quit' to exit.")
    speak("Hi, I am an enhanced chatbot, am still experimental so just hold on. Type 'quit' to exit.")
    while True:
        try:
            # Use speech recognition to get user input
            user_input = get_audio()
            if not user_input:
                continue

            if user_input.lower() == 'quit':
                print('Bye! Take care.')
                speak('Bye! Take care.')
                break
            elif 'weather' in user_input:
                city = user_input.split('in ')[-1]
                weather_info = get_weather(city)
                print(weather_info)
                speak(weather_info)
            elif 'news' in user_input:
                news_headlines = get_news()
                print(news_headlines)
                speak(news_headlines)
            elif 'feeling' in user_input:
                sentiment = analyze_sentiment(user_input)
                if sentiment < -0.1:
                    print("I'm sorry you're feeling down. Can I do anything to help?")
                    speak("I'm sorry you're feeling down. Can I do anything to help?")
                else:
                    print("It's great that you're feeling good!")
                    speak("It's great that you're feeling good!")
            else:
                bot_response = chat.respond(user_input)
                print(bot_response)
                speak(bot_response)
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    chatbot()
