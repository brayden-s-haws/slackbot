# Slackbot for Product Management Community

#### Current status: Complete

___

### Personal Progress
* What I learned: How to work with the Slack and Google Sheets APIs. How to implement different endpoints for different functions and purposes. How to have different types of triggers live within the same server (API calls, cron jobs, etc.)
* What I wish I had done differently: Spent more time on logging and tests. I mostly relied on print statements when there were errors and did not have programtic fallbacks for when there were issues.
* What I am most proud of: [Lines 55-70](https://github.com/brayden-s-haws/slackbot/blob/1a07f5742284a005de59a6da1b255803923c4903/slackbot_v1.0.py#L55) in slackbot_v1.0.py. The response from OpenAI can take several seconds leaving users wondering if anything is happening. I thought this was a clear way to acknowledge to the user that something was in fact happening.
* What I want to learn next: This was my first experience using Flask. I had a good experience with it but it made curious to try out Django and FastAPI.

## Description
This Slackbot was built for our Product Management Community's Slack workspace. It helps automate tasks and integrates with OpenAI's GPT-3.5 model to answer product management-related questions. It also has an integration Google Sheets that can be used for reading data from a sheet and updating a sheet. It has frameworks for interacting with the bot using: / commands, @ mentions, Slack events, and cron jobs.

https://user-images.githubusercontent.com/58832489/231047594-d14ab121-beb9-472b-8fe1-6231d6f40f97.mp4

## Features
This describes how the features work in the context of our slack but could be easily modified to fit other use cases.

- **Ask GPT-3.5 Questions**: Users can ask questions using the `/ask` command, and the bot generates responses using the OpenAI GPT-3.5 model.
- **Post YouTube Video**: Users can run the `/who_are_you` command to learn about the bot's background. The bot responds with a YouTube video link.
- **Respond to Mentions**: When the bot is mentioned with a "thanks" or "thank you" message, it responds with a thumbs-up emoji.
- **Post Weekly Conversation Starters**: The bot automatically posts a weekly conversation starter from a Google Sheet to a Slack channel. It also marks the question in the sheet as having been used so that it won't be repeated.
- **Welcome New Users**: When a new user joins the Slack workspace, the bot sends a welcome message to them.

## Setup
This is hosted on an always running instance through Replit. But it could be deployed on almost any machine running python and flask. Flask was used for it ease of creating endpoints. This ended up using more packages than imagined at the outset, they can be installed using this command:
  <pre><code>pip install flask openai pytz apscheduler google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client slack-sdk slack-bolt</code></pre>

Set up the following environment variables:
   - `SLACK_APP_TOKEN`: Slack App Token (account level)
   - `SLACK_BOT_TOKEN`: Slack Bot Token (bot level)
   - `SLACK_CHANNEL`: Numeric code for the Slack channel where the bot posts
   - `OPENAI_API_KEY`: API key for OpenAI GPT-3.5

Configure the Google Sheets API credentials by saving the JSON file inside your project and providing its file path in the `GOOGLE_SHEETS_API_KEY_FILE` variable. You can find more details on how to do this here: https://cloud.google.com/iam/docs/keys-create-delete

Update the following variables in the code with appropriate values:
   - `SPREADSHEET_ID`: Spreadsheet ID found in the URL of the Google Sheet workbook
   - `RANGE_NAME`: Range within the sheet (e.g., 'Sheet1')

## Functionality
The bot has paradigms for interacting with it through multiple methods (links for how to setup each included):
   - '/' Commands: https://api.slack.com/interactivity/slash-commands
   - @ Mentions: https://api.slack.com/tutorials/tracks/responding-to-app-mentions
   - Slack Events: https://api.slack.com/tutorials/tracks/responding-to-app-mentions
   - Cron Jobs: https://apscheduler.readthedocs.io/en/3.x/

You can also integrate with the Google Sheets API so that your bot can read and write from one or multiple workbooks (https://developers.google.com/sheets/api/guides/concepts)

## License

This project is open source and available under the [MIT License](LICENSE).

