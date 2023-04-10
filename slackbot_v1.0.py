#=====================================================
#SETUP ENVIRONMENT
#=====================================================
#(This should be reformatted/cleaned-up. I initially built each of the functions of the bot as a seperate file. When I merged them I dumped in all the needed imports but thet could be better organized)
import os
from flask import Flask, request, jsonify
import openai
import threading
import re
import json
import pytz
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

#=====================================================
#DEFINE GLOBAL VARIABLES
#=====================================================

#SLACK_APP_TOKEN is at the Slack account level
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")

#SLACK_BOT_TOKEN is at the bot level (this can be setup to rotate. Be careful if that is the case on your account because making an update to the bot will refresh the token and invalidate the one you have saved here)
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
#SLACK_CHANNEL is the numeric code for the channel you want the bot to post in, this is found in the URL.
SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
app = App(token=SLACK_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY
slack_client = WebClient(token=SLACK_BOT_TOKEN)

#Configure Google Sheets API credentials. #Save the json inside your project and then put the path to it here.
GOOGLE_SHEETS_API_KEY_FILE = "put your file path here"

#Configure the Google Sheets API client
SHEETS_CREDS = service_account.Credentials.from_service_account_file(GOOGLE_SHEETS_API_KEY_FILE)

#According to the Sheets API docs you don't need to pass in the discovery_service_url but I kept getting an error until I did
SHEETS_API = build('sheets', 'v4', credentials=SHEETS_CREDS, discoveryServiceUrl='https://sheets.googleapis.com/$discovery/rest?version=v4')

#=====================================================
#GENERATE RESPONSE FROM OPENAI API BASED ON / COMMAND
#=====================================================
#This function allows users to ask a question in Slack using a / command. The question is sent to OpenAI via their API where a response is generated.

#This is broken into two pieces. The first captures the request and acknowledges to Slack that the request was recieved.
@app.command("/ask")
def handle_ask_question(ack, respond, command, body):
    #Slack expects a response within 3 seconds of a request. If it does not recieve one by then it will show a timeout error. But then the request will complete and the response is added to slack. To account for that I split the /ask request in 2 pieces. This subroutine is what handles sending the question to openai and returning the response.
    ack()
    #It takes somewhere from 5-7 seconds to get the response from OpenAI. After you hit "Enter" on the / command in Slack it looks like nothing happened because the request is being process. So I added the "Thinking..." text to let users know that something was happening.
    initial_message = {
        "channel": body["channel_id"],
        "text": "🧠 Thinking...",
        "response_type": "in_channel"
    }
    response = app.client.chat_postMessage(**initial_message)

    #Record the timestamp of the "Thinking..." message. This is so we can delete it later
    thinking_ts = response["ts"]

    #Start a new thread that uses the generate_and_respond to generate the response through OpenAI, post it, and delete the initial message
    threading.Thread(target=generate_and_respond, args=(command, respond, body["channel_id"], thinking_ts)).start()

def generate_and_respond(command, respond, channel_id, thinking_ts):
    question_org = command["text"]
    question = "In the context of product management and technology, " + question_org
    #Had to add a question mark here because in the case where one wasn't included in the request, the response would get formatted oddly with a question mark on a new line between the question and response. There is probably a cleaner way to do this in the response but I couldn't get it working.
    if not question_org.strip().endswith("?"):
        question += "?"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
      #In our case we only want product management centric responses so this system message seeks to prevent OpenAI from returning a response that is not related to product management.  
      messages=[
            {"role": "system", "content": "You are the world's best product manager. You know everything about the topic and have learned from all other experts in the field. It is your job to teach others about product management. When possible you should include links to the sources you use in your answers. If someone asks something unrelated to product management tell them that what they are asking isnt connected to product management"},
            {"role": "user", "content": question}
        ],
        #you can adjust this token value to limit or expand the response. At this level of max_tokens, assuming there we 1000 questions a week that used all the tokens, the API cost would be about $1.20.
        max_tokens=1000,
        temperature=0.5,
    )
    summary = response["choices"][0]["message"]["content"].strip()
    final_response = f"*Question: {question_org}*\n{summary}"

    #Post the final response to the channel
    respond({
        "text": final_response,
        "response_type": "in_channel"
    })

    #Delete the "Thinking..." message using the timestamp we recorded earlier in handle_ask_question
    app.client.chat_delete(channel=channel_id, ts=thinking_ts)

#=====================================================
#POST YOUTUBE VIDEO BASED ON / COMMAND
#=====================================================
#This / command allows users to ask the bot for details on its background and it responds with a YouTube video on its origins.
  
#Handle the slash command /who_are_you
@app.command("/who_are_you")
def handle_who_are_you(ack, body, logger):
    #Acknowledge the command (again Slack expects this within 3 seconds or it will throw an error message)
    ack()

    #Respond with the YouTube video link
    message = {
        "response_type": "in_channel",
        "text": "Here's a YouTube video that explains who I am: https://www.youtube.com/watch?v=y8OnoxKotPQ",
    }
    app.client.chat_postMessage(channel=body["channel_id"], **message)

#=====================================================
#POST RESPONSE BASED ON @ MENTION
#=====================================================
#This is an easter egg in our bot. If you @mention it and say thanks it will respond with a thumbs up emoji. No real utility but it is fun.
  
#Event listener for app_mention event
@app.event("app_mention")
def respond_to_mention(event, say):
    #Convert the message text to lowercase for case-insensitive comparison
    message_text = event["text"].lower()

    #Define a regular expression pattern to match "thanks", "thank you", and variations
    thanks_pattern = r'\b(?:thanks|thank you)\b'

    #Check if the message contains the word "thanks" or "thank you" (case-insensitive)
    if re.search(thanks_pattern, message_text):
        # Respond with a thumbs up emoji
        say(":thumbsup:")

#=====================================================
#POST QUESTION FROM A GOOGLE SHEET
#=====================================================
#We post a weekly conversation starter to one of our channels. This was previously done manually. Now the bot grabs a question from the sheet, posts it to slack, and marks the question as used so that it wont be used again.
      
#The spreadsheet_id is found in the url of the google sheet workbook. If you are using more than one sheet you will need to better name these variables
SPREADSHEET_ID = "put your spreadsheet id here"

#range_name is the sheet you want to ue, you can also pass in specific cells if you only want a range within the sheet
RANGE_NAME = "put your range here (ex 'Sheet1')"

#Grab the question from the Google Sheet and update the date column to indicate the question was used
def get_question_and_update_date():
    result = SHEETS_API.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get("values", [])
    if not rows:
        print("No data found in the Google Sheet.")
        return None
    for index, row in enumerate(rows):
        if index == 0:  #Skip the header row, it was updating the header for the date column and not posting a question before adding this
            continue
        row += [''] * (3 - len(row))
        if not row[2]:
            question = row[1]
            row_number = index + 1
            break
    else:
        print("No available questions found.")
        return None
    current_date = datetime.datetime.now(pytz.timezone("America/Denver")).strftime("%Y-%m-%d")
    update_body = {"values": [[current_date]]}
    update_range = f"{RANGE_NAME}!C{row_number}"
    update_result = SHEETS_API.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=update_range,
        valueInputOption="RAW",
        body=update_body
    ).execute()
    print("Update response:")
    print(update_result)
    return question

#Post the question to the Slack channel
def post_question_to_slack_channel(question):
    client = WebClient(token=SLACK_BOT_TOKEN)
    try:
        response = client.chat_postMessage(channel=SLACK_CHANNEL, text=f"❓*Question of the Week*❓\n {question}")
    except SlackApiError as e:
        print(f"Error posting message: {e}")

#Indicate that this function should be scheduled
def scheduled_post_question():
    question = get_question_and_update_date()
    if question:
        post_question_to_slack_channel(question)

#Start APScheduler, this is needed to run a cron on Flask
scheduler = BackgroundScheduler(timezone=timezone("America/Denver"))
#Add a scheduled job to run every Monday at 9:00 AM
scheduler.add_job(scheduled_post_question, "cron", day_of_week="mon", hour=9, minute=0)
#Start the scheduler
scheduler.start()

#Allow for defining of Flask endpoints and allow for handling of Slack requests. There is sometning similar below for other requests. These can likely be combined but I had built two versions of the bot and then combined into one and didnt want to unwind that code yet.
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

#Define an endpoint for manual posting
#Hit this url to test manually: https://galactus-main.braydenhaws.repl.co/post_question
@flask_app.route('/post_question', methods=['GET'])
def post_question():
    question = get_question_and_update_date()
    if question:
        post_question_to_slack_channel(question)
        return jsonify(success=True, message="Question posted to Slack channel")
    else:
        return jsonify(success=False, message="No available question")

#=====================================================
#POST WELCOME MESSAGE TO USER CHANNEL
#=====================================================
#For when a user is added to our Slack workspace we send them a welcome message that orients them to the Slack

@app.event("team_join")
def welcome_user(body, logger):
    user_id = body["event"]["user"]["id"]

    try:
        client = WebClient(token=SLACK_BOT_TOKEN)
        client.chat_postMessage(
            channel=user_id,
            text="Welcome to Utah Product Guild! I'm here to help you get up to speed..."
        )
        logger.info(f"Sent a welcome message to user {user_id}")
    except SlackApiError as e:
        logger.error(f"Error sending message: {e}")
   
#Define route for Slack event request
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

#Start the Flask app, your port is likely different, this is what is used to host on Replit
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=3000)