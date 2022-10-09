from flask import Flask, request
from deep_translator import GoogleTranslator, single_detection
from xml.dom import minidom
import googlescraper

app = Flask(__name__)

@app.route('/')
def homepage():
    return "Welcome to EduChamp Api"

@app.route('/about')
def index():
    return "This is an api build for EduChamp Chatbot.To have seamless interaction"

#@app.route('/<query>')
#def response(query):
#    result = googlescraper.search(query)
#    return result

@app.route('/query', methods=['POST'])
def response():
    msg = request.form.get('Body')
    lang = single_detection(msg, api_key='bbe1af5f4651c0d5268d420bcfb2b36d')
    translated = GoogleTranslator(source="auto", target="en").translate(msg)
    print(lang, translated)

    resp = googlescraper.search(translated)

    if type(resp) == list:

        root = minidom.Document()
        xml = root.createElement('Response')
        root.appendChild(xml)

        productChild = root.createElement('Message')
        productChild.appendChild(root.createTextNode('Here are a few results I found...')) 
        xml.appendChild(productChild)

        for each in resp:
            
            productChild = root.createElement('Message')
            productChild.appendChild(root.createTextNode(each))
            xml.appendChild(productChild)

        print(root.toprettyxml())
        return root.toprettyxml()
    else:
        result = GoogleTranslator(source="en", target=lang).translate(resp)
        print(result)

        root = minidom.Document()

        xml = root.createElement('Response')
        root.appendChild(xml)

        productChild = root.createElement('Message')
        productChild.appendChild(root.createTextNode(result))
        xml.appendChild(productChild)

        print(root.toprettyxml())
        return root.toprettyxml()
    

if __name__=='__main__':
    app.run(debug=True)

# heroku config:set WEB_CONCURRENCY=1
'''
Step1: Sign in to the twilio account
Step2: Under My First Twilio account > messaging > Try it out > send a whatsapp message > follow the 5 steps to activate
Step3: Under Twilio Sandbox for WhatsApp > add the URL given by ngrok (Ex: https://fb8f8f8f.ngrok.io/query)
Step4: Run python-flask.py
Step5: Go to downloads > ngrok > run the ngrok.exe file
Step6: In the ngrok.exe enter 'ngrok http 5000' to generate the URL
<?xml version="1.0" encoding="UTF-8"?><Response><Message>Hello, how can I help?</Message></Response>
'''

