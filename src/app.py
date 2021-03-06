import requests
import os
import filter as mf
from flask import Flask, render_template, abort, request, redirect, Response
import twilio.twiml
from twilio.rest import TwilioRestClient

app = Flask(__name__)
#TWILIO CREDENTIALS###

# Find these values at https://twilio.com/user/account
account_sid = os.environ.get('TWILIO_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
client = TwilioRestClient(account_sid, auth_token)

###############GLOBAL VARS###########################
# set up buffer for filtering algorithm
mosc_buff = mf.mosc_buffer()

twil_num = "+12566671171"
twil_emer_num = "+18446875686"
twil_msg = "This is the data being sent."


################## Input Sanitization ######################
def sanitize_number(number):
    return ''.join([c for c in number if c.isdigit()]) if number else None

def sanitize_text(text):
    return ''.join([c for c in text if c.isalnum()]) if text else None

################### Routes #####################
@app.route('/api/v1/sms')
def sms_endpoint():
    number = sanitize_number(request.args.get('number'))
    message = sanitize_text(request.args.get('message'))
    #if pass_connection("sms"):
    return try_send_sms(number, message)
    #else:
   #     return reject_sms()

@app.route('/api/v1/call')
def call_endpoint():
    # if pass_connection("call"):
    return try_send_call()
    # else:
        # return reject_call()

@app.route('/api/v1/emergency_call')
def e_call_endpoint():
    #if pass_connection("ecall"):
    return try_send_ecall()
    #else:
    #    return reject_ecall("+12566671171")


@app.route('/api/v1/stats')
def return_stats():
    xml = "<stats>\n"
    # Emergency calls
    xml += "    <ecall>\n"
    xml += "        <received>"
    xml += str(mosc_buff.num_received_ecalls())
    xml += "</received>\n"
    xml += "        <served>"
    xml += str(mosc_buff.num_served_ecalls())
    xml += "</served>\n"
    xml += "    </ecall>\n"

    # Standard calls
    xml += "    <call>\n"
    xml += "        <received>"
    xml += str(mosc_buff.num_received_calls())
    xml += "</received>\n"
    xml += "        <served>"
    xml += str(mosc_buff.num_served_calls())
    xml += "</served>\n"
    xml += "    </call>\n"

    # SMS
    xml += "    <sms>\n"
    xml += "        <received>"
    xml += str(mosc_buff.num_received_sms())
    xml += "</received>\n"
    xml += "        <served>"
    xml += str(mosc_buff.num_served_sms())
    xml += "</served>\n"
    xml += "    </sms>\n"

    xml += "</stats>"
    res = Response(xml, mimetype='text/xml')
    res.headers["Access-Control-Allow-Origin"] = "*"
    res.headers["Access-Control-Allow-Methods"] = "GET"
    res.headers["Access-Control-Allow-Headers"] = "x-requested-with,Content-Type,Origin"
    res.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    res.headers["Pragma"] = "no-cache"
    res.headers["Expires"] = "0"
    return res

################### Responses #####################
# returns true or false whether we can connect
def pass_connection(connection_type):
    if type(connection_type) is not str:
        raise ValueError("conneciton_type must be of type str")
#    packet = Packet(connection_type)
    success = mosc_buff.add(connection_type)
    if success:
        return True
    else:
        return False

def try_send_sms(number, message):
    #resp = twilio.twiml.Response()
    if pass_connection('sms'):
        bod = message
    else:
        bod = "Your SMS has been dropped due to an emergency right now."
    message = client.messages.create(to=number, from_=twil_num,
                                     body=bod)

def try_send_call():
    resp = twilio.twiml.Response()
    text = ""

    if pass_connection('call'):
        #respond with  YES that TWIML understands
        text = "Your call has successfully completed.  Thank you."
    else:
        #respond with NO
        text = "All circuits are busy now; please try again later.  MOSC"
    xml = "<Response>"
    xml += "    <Say>"
    xml += text
    xml += "</Say>\n"
    xml += "</Response>"
    resp.say(xml)
    return str(resp)


def try_send_ecall():

    resp = twilio.twiml.Response()
    text = ""

    if pass_connection('ecall'):
        #respond with  YES that TWIML understands
        text = "Your emergency call has successfully completed; if this were a real emergency, you would be speaking with an operator now.  If this is a real emergency, please hang up and dial 9 1 1"
    else:
        #respond with NO
        text = "All circuits are busy now; please try again later.  MOSC"
    xml = "<Response>"
    xml += "    <Say>"
    xml += text
    xml += "</Say>\n"
    xml += "</Response>"
    resp.say(xml)
    return str(resp)
    # resp.say("This call represents an emergency call.  If you are experiencing\
    #     a real emergency, please hang up now and dial 9-1-1.")


################### Twilio #####################
callers = {
    "+16507769918": "Gavin Chan",
    "+14158675310": "Boots",
    "+14158675311": "Virgil",
    "+12566671171": "MOSC",
}

@app.route("/")
def root_page():
    return 'MOSC Backend Landing Page\nIf you are a user, you should not be seeing this!'
    # Get the caller's phone number from the incoming Twilio request
    from_number = request.values.get('From', None)
    resp = twilio.twiml.Response()
    resp.say("Hi Kelvin")
    # return str(resp)

    # if the caller is someone we know:
    # if from_number in callers:
    #     # Greet the caller by name
    #     resp.say("Hello " + callers[from_number])
    # else:
    #     resp.say("Hello Monkey")

    # return str(resp)

if __name__ == '__main__':
    app.debug = True
    app.run()
