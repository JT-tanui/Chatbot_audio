import nltk
from nltk.chat.util import Chat, reflections
from textblob import TextBlob
import requests

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
    while True:
        user_input = input("> ")
        if user_input.lower() == 'quit':
            print('Bye! Take care.')
            break
        elif 'weather' in user_input:
            city = user_input.split('in ')[-1]
            print(get_weather(city))
        elif 'feeling' in user_input:
            sentiment = analyze_sentiment(user_input)
            if sentiment < -0.1:
                print("I'm sorry you're feeling down. Can I do anything to help?")
            else:
                print("It's great that you're feeling good!")
        else:
            print(chat.respond(user_input))

if __name__ == "__main__":
    chatbot()
