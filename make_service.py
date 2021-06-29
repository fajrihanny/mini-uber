# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

account_sid = os.environ['TWILIO_ACCOUNT_SID']
api_key = os.environ['TWILIO_API_KEY']
api_secret = os.environ['TWILIO_API_SECRET']
client = Client(api_key, api_secret, account_sid)

def create_service(service_name):
    service = client.proxy.services.create(unique_name=service_name)
    print(service.sid)
