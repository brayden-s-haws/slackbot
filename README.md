# Slackbot for Product Management Community

## Description
This Slackbot was built for our Product Management Community's Slack workspace. It helps automate tasks and integrates with OpenAI's GPT-3 model to answer product management-related questions. It also has an integration Google Sheets that can be used for reading data from a sheet and updating a sheet. It has frameworks for interacting with the bot using: / commands, @ mentions, Slack events, and cron jobs.

## Features
This describes how the features work in the context of our slack but could be easily modified to fit other use cases.

- **Ask GPT-3 Questions**: Users can ask questions using the `/ask` command, and the bot generates responses using the OpenAI GPT-3 model.
- **Post YouTube Video**: Users can run the `/who_are_you` command to learn about the bot's background. The bot responds with a YouTube video link.
- **Respond to Mentions**: When the bot is mentioned with a "thanks" or "thank you" message, it responds with a thumbs-up emoji.
- **Post Weekly Conversation Starters**: The bot automatically posts a weekly conversation starter from a Google Sheet to a Slack channel. It also marks the question in the sheet as having been used so that it won't be repeated.
- **Welcome New Users**: When a new user joins the Slack workspace, the bot sends a welcome message to them.

## Setup
This is hosted on an always running instance through Replit. But it could be deployed on almost any machine running python and flask. Flask was used for it ease of creating API endpoints. This ended up using more packages than imagined at the outset, they can be installed using this command:
  <pre><code>pip install flask openai pytz apscheduler google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client slack-sdk slack-bolt</code></pre>

Set up the following environment variables:
   - `SLACK_APP_TOKEN`: Slack App Token (account level)
   - `SLACK_BOT_TOKEN`: Slack Bot Token (bot level)
   - `SLACK_CHANNEL`: Numeric code for the Slack channel where the bot posts
   - `OPENAI_API_KEY`: API key for OpenAI GPT-3

Configure the Google Sheets API credentials by saving the JSON file inside your project and providing its file path in the `GOOGLE_SHEETS_API_KEY_FILE` variable. You can find more details on how to do this here: https://cloud.google.com/iam/docs/keys-create-delete

Update the following variables in the code with appropriate values:
   - `SPREADSHEET_ID`: Spreadsheet ID found in the URL of the Google Sheet workbook
   - `RANGE_NAME`: Range within the sheet (e.g., 'Sheet1')

##Use
The bot has paradigms for interacting with it through multiple methods (links for how to setup each included):
   - '/' Commands: https://api.slack.com/interactivity/slash-commands
   - @ Mentions: https://api.slack.com/tutorials/tracks/responding-to-app-mentions
   - Slack Events: https://api.slack.com/tutorials/tracks/responding-to-app-mentions
   - Cron Jobs: https://apscheduler.readthedocs.io/en/3.x/

You can also integrate with the Google Sheets API so that your bot can read and write from one or multiple workbooks (https://developers.google.com/sheets/api/guides/concepts)

## License

This project is open source and available under the [MIT License](LICENSE).
