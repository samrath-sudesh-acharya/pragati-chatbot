from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


import time
import os

import numpy as np
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout
import random
import nltk


from nltk.tokenize import word_tokenize

from nltk.corpus import stopwords
stop_words = stopwords.words('english')

from nltk.stem import WordNetLemmatizer

def clean_corpus(corpus):
  corpus = [ doc.lower() for doc in corpus]
  cleaned_corpus = []
  
  stop_words = stopwords.words('english')
  wordnet_lemmatizer = WordNetLemmatizer()

  for doc in corpus:
    tokens = word_tokenize(doc)
    cleaned_sentence = [] 
    for token in tokens: 
      if token not in stop_words and token.isalpha(): 
        cleaned_sentence.append(wordnet_lemmatizer.lemmatize(token)) 
    cleaned_corpus.append(' '.join(cleaned_sentence))
  return cleaned_corpus

with open('intents.json', 'r',encoding='utf-8') as file:
  intents = json.load(file)

corpus = []
tags = []

for intent in intents['intents']:
    for pattern in intent['patterns']:
        corpus.append(pattern)
        tags.append(intent['tag'])

cleaned_corpus = clean_corpus(corpus)

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(cleaned_corpus)
encoder = OneHotEncoder()
y = encoder.fit_transform(np.array(tags).reshape(-1,1))

model = Sequential([
                    Dense(128, input_shape=(X.shape[1],), activation='relu'),
                    Dropout(0.2), 
                    Dense(64, activation='relu'),
                    Dropout(0.2),
                    Dense(y.shape[1], activation='softmax')
])

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()

history = model.fit(X.toarray(), y.toarray(), epochs=32, batch_size=1)

INTENT_NOT_FOUND_THRESHOLD = 0.92

def predict_intent_tag(message):
  message = clean_corpus([message])
  X_test = vectorizer.transform(message)
  
  y = model.predict(X_test.toarray()) 

  if y.max() < INTENT_NOT_FOUND_THRESHOLD:
    return 'noanswer'
  
  prediction = np.zeros_like(y[0])
  prediction[y.argmax()] = 1
  tag = encoder.inverse_transform([prediction])[0][0]
  return tag

def get_intent(tag):
  
  for intent in intents['intents']:
    if intent['tag'] == tag:
      return intent

def window_opener():
  GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
  CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
  chrome_options = webdriver.ChromeOptions()
  chrome_options.add_argument("--start-maximized")
  chrome_options.add_argument("--incognito")
  chrome_options.add_argument("--disable-dev-shm-usage")
  chrome_options.add_argument('--disable-gpu')
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument('--headless')
  chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
  #chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
  #driver = webdriver.Chrome(ChromeDriverManager().install(), options = chrome_options)
  #driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
  #driver = webdriver.Chrome('C:\chromedriver.exe', options = chrome_options)
  driver = webdriver.Chrome(service=Service('C:\chromedriver.exe'), options = chrome_options)
  return driver

driver = window_opener()
def search(query):
    global driver
    tag = predict_intent_tag(query)
    intent = get_intent(tag)
    if intent != None:
      if intent['tag'] == 'goodbye':
        response = random.choice(intent['responses'])
        return response
      elif intent['tag'] == 'greeting' or intent['tag'] == 'thanks' or intent['tag'] == 'options' or intent['tag'] == 'name' or intent['tag'] == 'creator':
        response = random.choice(intent['responses'])
        return response
    
    driver.get('https://www.google.com/')
    time.sleep(0.25)
    driver.find_element_by_xpath('/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input').send_keys(query)
    time.sleep(0.25)
    driver.find_element_by_xpath('/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input').send_keys(Keys.ENTER)
    time.sleep(0.5)
    page_source = driver.page_source.encode('utf-8')

    soup = BeautifulSoup(page_source, features = 'lxml')
    soup.encode('utf-8')
    data = soup.find(class_ = 'wxAfhc')

    links = []

    try:
        text1 = data.find_all(class_ = 'bjV81b')
        text2 = data.find_all(class_ = 'JDfRZb')
        for a, b in zip(text1, text2):
            return (a.get_text(), b.get_text())
    except AttributeError:
        try:
            data = soup.find(class_ = 'hgKElc').get_text().strip()
            return data
        except AttributeError:
            try:
                response = random.choice(intent['responses'])
                return response
            except TypeError:
                try:
                    link = soup.find_all("div", class_ = 'yuRUbf', limit=3)
                    for each in link:
                        href = each.find('a')['href']
                        links.append(href)
                    return links
                except AttributeError:
                     return "Sorry couldn't find anything. I am still learning" 