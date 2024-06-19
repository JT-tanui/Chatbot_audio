import os
import subprocess
import sys
import nltk
from nltk.chat.util import Chat, reflections
from textblob import TextBlob
import requests
import speech_recognition as sr
from gtts import gTTS
import datetime

# Ensure distutils is available
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import distutils
except ImportError:
    print("distutils is not installed. Attempting to install...")
    install('setuptools')
    try:
        import distutils
        print("distutils installed successfully.")
    except ImportError:
        print("Failed to install distutils. Please install it manually.")

# Define conversation pairs
pairs = [
    ['my name is (.*)', ['Hello %1, how can I help you today?']],
    ['hi|hello|hey', ['Hello!', 'Hey there!']],
    ['what is your name?', ['I am a chatbot created by you.']],
    ['how are you?', ['I am just a bunch of code, but thanks for asking!']],
    ['tell me a joke', ['Why don’t scientists trust atoms? Because they make up everything!']],
    ['quit', ['Bye! Take care.']],
    ['(.*) weather in (.*)', ['Let me check the weather in %2 for you.']],
    ['i am feeling (.*)', ['I am sorry to hear that you are feeling %1.']],
    ['tell me the news', ['Here are the latest headlines:\n%s']],
    ['define (.*)', ['Let me look up the definition of %1 for you.']],
    ['ask me a trivia question', ['Sure, let me get a trivia question for you.']],
    ['give me a quote', ['Here is an inspirational quote for you:\n%s']],
    ['stock price of (.*)', ['Let me check the stock price of %1 for you.']],
    ['convert (.*) to (.*)', ['Let me convert %1 to %2 for you.']],
    ['add to my to-do list (.*)', ['I have added %1 to your to-do list.']],
    ['show my to-do list', ['Here is your to-do list:\n%s']],
    ['set a reminder to (.*) at (.*)', ['I have set a reminder for %1 at %2.']],
    ['show my reminders', ['Here are your reminders:\n%s']],
    ['add event (.*) on (.*)', ['I have added the event %1 on %2 to your calendar.']],
    ['show my calendar', ['Here are your calendar events:\n%s']],
    ['solve (.*)', ['Let me solve the math problem %1 for you.']]
]

chat = Chat(pairs, reflections)

# API keys (use your own API keys here)
weather_api_key = 'a1c3064d665bfa00b550c7ef1d3d8bf6'
news_api_key = 'f8e75d01380648959f8768d1b4191ab8'
words_api_key = '3d565cf76amshae1d1dceaa7e88ep15b1bfjsn58f72f8d22ce'
alpha_vantage_api_key = 'APUMCQKMEKP02X10'
exchange_rate_api_key = 'bb6b43cf23e99db6fd76748a'

base_url = 'http://api.openweathermap.org/data/2.5/weather?'
news_base_url = 'https://newsapi.org/v2/top-headlines?country=us&apiKey='
words_api_url = "https://wordsapiv1.p.rapidapi.com/words/lovely/synonyms"
trivia_url = 'https://opentdb.com/api.php?amount=1&type=multiple'
quotes_url = 'https://api.quotable.io/random'
stock_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol='
currency_url = 'https://v6.exchangerate-api.com/v6/'

# Initialize the speech recognition engine
recognizer = sr.Recognizer()

# Data stores for personalization
user_todo_list = []
user_reminders = {}
user_calendar = {}

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
    complete_url = base_url + 'appid=' + weather_api_key + '&q=' + city
    response = requests.get(complete_url)
    data = response.json()
    if data['cod'] != '404':
        main = data['main']
        weather_desc = data['weather'][0]['description']
        temp = main['temp']
        return f'Temperature: {temp}K\nWeather Description: {weather_desc}'
    else:
        return 'City Not Found'

def get_news():
    complete_url = news_base_url + news_api_key
    response = requests.get(complete_url)
    data = response.json()
    if data['status'] == 'ok':
        articles = data['articles'][:5]  # Get the top 5 headlines
        headlines = [article['title'] for article in articles]
        return '\n'.join(headlines)
    else:
        return 'Unable to fetch news at the moment.'

def get_definition(word):
    headers = {
        'x-rapidapi-key': words_api_key,
        'x-rapidapi-host': 'wordsapiv1.p.rapidapi.com'
    }
    response = requests.get(f"{words_api_url}{word}/definitions", headers=headers)
    data = response.json()
    if 'definitions' in data:
        return data['definitions'][0]['definition']
    else:
        return 'No definition found.'

def get_trivia_question():
    response = requests.get(trivia_url)
    data = response.json()
    if data['response_code'] == 0:
        question = data['results'][0]['question']
        correct_answer = data['results'][0]['correct_answer']
        return f"{question} (Answer: {correct_answer})"
    else:
        return 'Unable to fetch a trivia question at the moment.'

def get_quote():
    response = requests.get(quotes_url)
    data = response.json()
    if 'content' in data:
        return f"{data['content']} - {data['author']}"
    else:
        return 'Unable to fetch a quote at the moment.'

def get_stock_price(symbol):
    complete_url = f"{stock_url}{symbol}&interval=1min&apikey={alpha_vantage_api_key}"
    response = requests.get(complete_url)
    data = response.json()
    try:
        time_series = data['Time Series (1min)']
        latest_timestamp = list(time_series.keys())[0]
        closing_price = time_series[latest_timestamp]['4. close']
        return f"The latest closing price of {symbol} is ${closing_price}."
    except KeyError:
        return 'Unable to fetch stock price at the moment.'

def convert_currency(amount, from_currency, to_currency):
    complete_url = f"{currency_url}{exchange_rate_api_key}/pair/{from_currency}/{to_currency}"
    response = requests.get(complete_url)
    data = response.json()
    if data['result'] == 'success':
        conversion_rate = data['conversion_rate']
        converted_amount = amount * conversion_rate
        return f"{amount} {from_currency} is equal to {converted_amount:.2f} {to_currency}."
    else:
        return 'Unable to perform currency conversion at the moment.'

def analyze_sentiment(sentence):
    blob = TextBlob(sentence)
    return blob.sentiment.polarity

def add_to_todo_list(task):
    user_todo_list.append(task)
    return f"Added '{task}' to your to-do list."

def show_todo_list():
    if not user_todo_list:
        return "Your to-do list is empty."
    return '\n'.join(user_todo_list)

def set_reminder(task, time):
    user_reminders[time] = task
    return f"Set a reminder to '{task}' at {time}."

def show_reminders():
    if not user_reminders:
        return "You have no reminders."
    return '\n'.join([f"{time}: {task}" for time, task in user_reminders.items()])

def add_event(event, date):
    user_calendar[date] = event
    return f"Added event '{event}' on {date}."

def show_calendar():
    if not user_calendar:
        return "Your calendar is empty."
    return '\n'.join([f"{date}: {event}" for date, event in user_calendar.items()])

def solve_math_problem(problem):
    try:
        result = eval(problem)
        return f"The result is {result}."
    except Exception as e:
        return f"Unable to solve the problem. Error: {e}"

def chatbot():
    print("Hi, I am your enhanced chatbot. Type 'quit' to exit.\n"
          "For solving say  \"solve **** \" \n"
          "For events say  \"add event **** on ****(date)\" \n"
          "For reminder say  \"set a reminder to **** at ****(time)\"\n"
          "For todo_list say  \"add to my to-do list ****\" \n"
          "For convert say  \"Convvert **** from currency to currency\" \n"
          "For stock say  \"stock of ****(stock)\" \n"
          "For defination say  \"define ****\" \n"
          "For weather say  \"Weather in ****\"")
    speak("Hi, I am an enhanced chatbot, am still experimental but the developer is doing his best ."
          "Type 'quit' if you'd like to exit the conversation with the bot.")
    while True:
        try:
            # Use speech recognition to get user input
            user_input = get_audio()
            if not user_input:
                continue

            if user_input.lower() == 'quit':
                print('Bye! Just remember am here if you need any assistance, Talk to you later.')
                speak('Bye! Just remember am here if you need any assistance, Talk to you later.')
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
            elif 'define' in user_input:
                word = user_input.split('define ')[-1]
                definition = get_definition(word)
                print(definition)
                speak(definition)
            elif 'trivia' in user_input:
                trivia_question = get_trivia_question()
                print(trivia_question)
                speak(trivia_question)
            elif 'quote' in user_input:
                quote = get_quote()
                print(quote)
                speak(quote)
            elif 'stock price of' in user_input:
                symbol = user_input.split('of ')[-1]
                stock_info = get_stock_price(symbol)
                print(stock_info)
                speak(stock_info)
            elif 'convert' in user_input:
                parts = user_input.split(' ')
                amount = float(parts[1])
                from_currency = parts[2].upper()
                to_currency = parts[4].upper()
                conversion_info = convert_currency(amount, from_currency, to_currency)
                print(conversion_info)
                speak(conversion_info)
            elif 'add to my to-do list' in user_input:
                task = user_input.split('list ')[-1]
                response = add_to_todo_list(task)
                print(response)
                speak(response)
            elif 'show my to-do list' in user_input:
                todo_list = show_todo_list()
                print(todo_list)
                speak(todo_list)
            elif 'set a reminder to' in user_input:
                task = user_input.split('to ')[-1]
                time = user_input.split(' at ')[-1]
                response = set_reminder(task, time)
                print(response)
                speak(response)
            elif 'show my reminders' in user_input:
                reminders = show_reminders()
                print(reminders)
                speak(reminders)
            elif 'add event' in user_input:
                event = user_input.split('event ')[-1]
                date = user_input.split(' on ')[-1]
                response = add_event(event, date)
                print(response)
                speak(response)
            elif 'show my calendar' in user_input:
                calendar_events = show_calendar()
                print(calendar_events)
                speak(calendar_events)
            elif 'solve' in user_input:
                problem = user_input.split('solve ')[-1]
                solution = solve_math_problem(problem)
                print(solution)
                speak(solution)
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
