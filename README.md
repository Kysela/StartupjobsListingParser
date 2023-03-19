# Startup Jobs API to Telegram Bot
This code provides a way to fetch **job listings** from the **Startup Jobs API** and send them to a **Telegram Bot** using **Telegram API**. It is written in **Python** and uses the **requests library** to handle HTTP requests.

**Requirements:**
- Python 3.x
- requests library

**How to use:**
- Clone this repository or download the source code.
- Install the requests library using pip install requests command.
- Obtain a Telegram bot API token from the BotFather and insert it in the TG_API_TOKEN constant.
- Obtain your Telegram chat ID and insert it in the TG_CHAT_ID constant.
- Run the startupjobs.py file.
- The script will fetch the job listings from the Startup Jobs API, process them, and send the relevant ones to your Telegram bot. If the job listings have already been sent, the script will not send them again.

**Configuration:**

The script uses the following constants:

- STARTUPJOBS_API: The URL of the Startup Jobs API.
- TELEGRAM_API: The URL of the Telegram API.
- TG_API_TOKEN: Your Telegram bot API token.
- TG_CHAT_ID: Your Telegram chat ID.
- SETTINGS_PATH: The path to the settings file, which contains a set of job listing IDs that have already been sent.
- TESTING_MODE: A flag that, when set to True, sends only the first job listing to the Telegram bot and exits the script.
- SESSION: A requests.Session() object used to maintain the connection with the Startup Jobs API.

**How it works:**
- The process_startupjobs_api() function is responsible for fetching the job listings from the Startup Jobs API. It takes two parameters: the page number to fetch and the user agent to use for the request. It returns the response as a JSON object.

- The process_resultset() function processes the job listings and sends them to the Telegram bot. It takes the job listings as a parameter and extracts the relevant information, such as the job title, company name, location, and URL. It creates a message string using f-strings and sends the message and the image URL (if it exists) to the Telegram bot using the send_message() function. The send_message() function uses the Telegram API to send the message to the bot.

- The initialize_settings() and save_settings() functions are used to load and save the set of job listing IDs that have already been sent. The save_key() function adds a key (job listing ID) to the set, and the check_key() function checks if the key exists in the set.

- Finally, the get_random_user_agent() function returns a random user agent from a list of user agents to use for the HTTP request to the Startup Jobs API.