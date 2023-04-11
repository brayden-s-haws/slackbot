# Slackbot for Product Management Community

## Description
This Slackbot was built for our Product Management Community's Slack workspace. It helps automate tasks and integrates with OpenAI's GPT-3 model to answer product management-related questions. It also has an integration Google Sheets that can be used for reading data from a sheet and updating a sheet. It has frameworks for interacting with the bot using: / commands, @ mentions, Slack events, and cron jobs.

## Features
This describes how the features work in the context of our slack but could easily to modified to fit other use cases.

- **Ask GPT-3 Questions**: Users can ask questions using the `/ask` command, and the bot generates responses using the OpenAI GPT-3 model.
- **Post YouTube Video**: Users can run the `/who_are_you` command to learn about the bot's background. The bot responds with a YouTube video link.
- **Respond to Mentions**: When the bot is mentioned with a "thanks" or "thank you" message, it responds with a thumbs-up emoji.
- **Post Weekly Conversation Starters**: The bot automatically posts a weekly conversation starter from a Google Sheet to a Slack channel. It also marks the question in the sheet as having been used so that it won't be repeated.
- **Welcome New Users**: When a new user joins the Slack workspace, the bot sends a welcome message to them.

## Setup
I am hosting this on an always running instance through Replit but you can deploy this on any machine running python and flask. I am running this as a flask app so I could easily create API endpoints but you could probably also run it in python. This ended up using more packages than I imagined at the outset, you can install them using this command:
pip install flask openai pytz apscheduler google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client slack-sdk slack-bolt
