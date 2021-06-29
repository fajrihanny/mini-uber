# mini-uber

This is a small Twilio app to demonstrate the ability of Twilio Proxy API.

## Objective
By sending message to a Twilio number, the initial caller/texter (could be driver/customer) can communicate with the second user (could be the driver/customer too) via masked communication

## Workflow
- The first user will initiate the masked conversation by sending sms/call to Twilio number
- The SMS/call will activate the masked conversation between the first and second user by utilizing Twilio Proxy API

## Notes
- This simple app only makes use of one Twilio number. Ideally, there should at least be two of them, but if you are on Twilio trial account, you will only have one.
- The Twilio trial number is only available for US and Canada. This app is assuming that you are going to use different country's phone number (other than US and Canada) for your driver and customer's hence why you will need to pass a proxy identifier when you add participants.
- At the moment, this app can't pick up the ride ID that's supposed to be another identifier when picking up customer-driver pairing. This will be another aspect to be improved in the future.
- Due to the previous reason, the database here only has one pairing (which are your two phone numbers) with hardcoded ride ID=1
- You will have to make a simple database (sqlite3 library recommended) named customerider.db and a table customerrider that's structured like this:

| ride_id | customer_phone | driver_phone |


## How to
1. Install Flask https://flask.palletsprojects.com/en/2.0.x/installation/
2. Install ngrok https://ngrok.com/download
3. Insert your customer phone and driver phone by running insert_number.py. Provide ride_id=1 as one of the parameters. 
4. Set up your environment variables
5. Run make_service.py. Note down the service SID. Save it as another environment variable.
6. Run call_user.py. Flask will run on your localhost.
7. Run your ngrok. Get the public URL for your localhost.
8. Update your Twilio number with the webhook URL to listen to incoming message.
9. Send a message from one of the phone numbers to the Twilio number.


