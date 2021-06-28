import os
from twilio.rest import Client
from flask import Flask, request, redirect
import sqlite3

account_sid = os.environ['TWILIO_ACCOUNT_SID']
api_key = os.environ['TWILIO_API_KEY']
api_secret = os.environ['TWILIO_API_SECRET']
phone_sid = os.environ['TWILIO_PHONE_SID']
proxy_number = os.environ['TWILIO_PROXY_NUMBER']
client = Client(api_key, api_secret, account_sid)
service_sid = ''

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def send_back():
    service = client.proxy.services.create(unique_name='fanny_mini_uber',default_ttl=3600)
    service_sid = service.sid
    phone_number = client.proxy.services(service_sid).phone_numbers.create(sid=phone_sid)
    # get the sender number
    sender = request.values.get('From',None)
    message = request.values.get('Body',None)
    # search for the correct number in the database
    receiver = search_database(sender,1)
    # use Proxy API to create secure call between customer and driver
    interaction_id = create_proxy(sender,receiver,message)
    return interaction_id

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

# twilio creates the Proxy using these two numbers and initiate the text send to receiver
def create_proxy(sender_number,receiver_number,message):
    sender = 'sender'
    receiver = 'receiver'
    # make session - ttl=10 minutes
    session = client.proxy.services(service_sid).sessions.create(unique_name='fanny_mini_uber',ttl=600)
    session_sid = session.sid
    # add participants
    sender_sid = add_participants(sender_number,sender,service_sid,session_sid)
    receiver_sid = add_participants(receiver_number,receiver,service_sid,session_sid)
    interaction_sid = send_initial_call(receiver_sid,service_sid,session_sid,message)
    return interaction_sid

def add_participants(phonenumber,name,service,session):
    participant = client.proxy.services(service).sessions(session).participants.create(friendly_name=name, identifier=phonenumber,proxy_identifier=proxy_number)
    return participant.sid

def send_initial_call(participant_sid,service,session,message_to_send):
    voice_interaction = client.proxy.services(service).sessions(session).participants(participant_sid).message_interactions.create(body=message_to_send)
    return voice_interaction.sid

if __name__ == "__main__":
    app.run(debug=True)
