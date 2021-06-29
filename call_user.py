import os
from twilio.rest import Client
from flask import Flask, request, redirect
import sqlite3
import uuid

account_sid = os.environ['TWILIO_ACCOUNT_SID']
api_key = os.environ['TWILIO_API_KEY']
api_secret = os.environ['TWILIO_API_SECRET']
phone_sid = os.environ['TWILIO_PHONE_SID']
proxy_number = os.environ['TWILIO_PROXY_NUMBER']
service_sid = os.environ['PROXY_SERVICE_ID']
client = Client(api_key, api_secret, account_sid)

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def send_back():
    # get the sender number and message body from request payload
    sender = request.values.get('From',None)
    body = request.values.get('Body',None)
    # search the receiver number from the database -- ride ID is hardcoded to 1 due to the simplicity of the use case
    receiver = search_database(sender,1)
    # start the process to create Proxy API between sender and receiver 
    interaction_id = create_proxy(sender,receiver,body)
    return interaction_id

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
    conn.close()

# twilio creates the Proxy using these two numbers and initiate the text send to receiver
def create_proxy(sender_number,receiver_number,message):
    sender = 'sender'
    receiver = 'receiver'

    # add phone number to the service
    phone_number = client.proxy.services(service_sid).phone_numbers.create(sid=phone_sid)

    # make session - ttl=10 minutes
    unique_session = uuid.uuid1()
    session = client.proxy.services(service_sid).sessions.create(unique_name=unique_session,ttl=600)
    session_sid = session.sid

    # add participants to the conversation
    sender_sid = add_participants(sender_number,sender,service_sid,session_sid)
    receiver_sid = add_participants(receiver_number,receiver,service_sid,session_sid)

    # send the initial message to the receiver with the message from the sender
    interaction_sid = send_initial_message(receiver_sid,service_sid,session_sid,message)
    return interaction_sid

def add_participants(phonenumber,name,service,session):
    participant = client.proxy.services(service).sessions(session).participants.create(friendly_name=name, identifier=phonenumber,proxy_identifier=proxy_number)
    print (participant.proxy_identifier)
    return participant.sid

def send_initial_message(participant_sid,service,session,message_to_send):
    message_interaction = client.proxy.services(service).sessions(session).participants(participant_sid).message_interactions.create(body=message_to_send)
    return message_interaction.sid

if __name__ == "__main__":
    app.run(debug=True)

