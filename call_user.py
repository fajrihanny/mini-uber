from twilio.twiml.messaging_response import MessagingResponse
import os
from twilio.rest import Client
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3

account_sid = os.environ['TWILIO_ACCOUNT_SID']
api_key = os.environ['TWILIO_API_KEY']
api_secret = os.environ['TWILIO_API_SECRET']
phone_sid = os.environ['TWILIO_PHONE_SID']
proxy_number = os.environ['TWILIO_PROXY_NUMBER']
client = Client(api_key, api_secret, account_sid)

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def send_back():
    # get the sender number
    sender = request.values.get('From',None)
    message = request.values.get('Body',None)
    # search for the correct number in the database
    who_to_call = search_database(sender,1)
    # use Proxy API to create secure call between customer and driver
    create_proxy(sender,who_to_call,message)
    return who_to_call

# server searches in the database, matching the user A with user B
def search_database(number,rideID):
    conn = sqlite3.connect('./customerider.db')
    c = conn.cursor()
    c.execute("select * from customerrider where driver_phone = ? and ride_id = ?",(number,rideID))
    if (len(c.fetchall()) == 0):
        # search for matching driver, index 2
        c.execute("select * from customerrider where customer_phone = ? and ride_id = ?",(number,rideID)) 
        for row in c.fetchall():
            number_returned = str(row[2])
            number_returned = '+'+number_returned
            return number_returned
    else:
        c.execute("select * from customerrider where driver_phone = ? and ride_id = ?",(number,rideID))
        for row in c.fetchall():
            number_returned = str(row[1])
            number_returned = '+'+number_returned
            return number_returned

# listens to the incoming webhook and sends back response to Twilio in a form of TwiML with the details of two users


# twilio creates the Proxy using these two numbers and initiate the conversation
def create_proxy(user1,user2,message):
    # make service
    service = client.proxy.services.create(unique_name='fanny_hello5')
    service_sid = service.sid
    customer = 'customer'
    driver = 'driver'
    # make session
    session = client.proxy.services(service_sid).sessions.create(unique_name='fanny_hello5')
    session_sid = session.sid
    # add phone
    phone_number = client.proxy.services(service_sid).phone_numbers.create(sid=phone_sid)
    # add participants
    customer_sid = add_participants(user1,customer,service_sid,session_sid,)
    driver_sid = add_participants(user2,driver,service_sid,session_sid)

def add_participants(phonenumber,name,service,session):
    participant = client.proxy.services(service).sessions(session).participants.create(friendly_name=name, identifier=phonenumber,proxy_identifier=proxy_number)
    return participant.sid

def send_initial_message(participant_sid,service,session,message_to_send):
    message_interaction = client.proxy.services(service).sessions(session).participants(participant_sid).message_interactions.create(body=message_to_send)
    print(message_interaction.sid)

if __name__ == "__main__":
    app.run(debug=True)

