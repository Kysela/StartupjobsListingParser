import os
import random
import requests
import pickle

# Constants
STARTUPJOBS_API = 'https://www.startupjobs.cz/api/nabidky'
TELEGRAM_API = 'https://api.telegram.org/bot'
TG_API_TOKEN = 'PLACEHOLDER'
TG_CHAT_ID = 'PLACEHOLDER'
SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.pickle")

# Global variables
SETTINGS = set()
SETTINGS_EXISTS = os.path.isfile(SETTINGS_PATH)
TESTING_MODE = False
SESSION = requests.Session()

def save_key(key):
    """Add the key to the set of saved keys."""
    SETTINGS.add(key)


def check_key(key):
    """Check if the key exists in the set of saved keys."""
    return key in SETTINGS


def initialize_settings():
    """Load the saved settings from disk."""
    global SETTINGS
    if SETTINGS_EXISTS:
        try:
            with open(SETTINGS_PATH, 'rb') as f:
                SETTINGS = pickle.load(f)
        except Exception as e:
            print(f'Error loading settings from disk: {e}')


def save_settings():
    """Save the current settings to disk."""
    try:
        with open(SETTINGS_PATH, 'wb') as f:
            pickle.dump(SETTINGS, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print(f'Error saving settings to disk: {e}')


def get_random_user_agent():
    """Get a random user agent from a list of user agents."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Mozilla/5.0 (Android 12; Mobile; rv:85.0) Gecko/85.0 Firefox/85.0",
        "Mozilla/5.0 (Android 13; Mobile; rv:85.0) Gecko/85.0 Firefox/85.0",
        "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/89.0.4389.82 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/89.0.4389.82 Mobile/16E148 Safari/604.1"
    ]
    return random.choice(user_agents)

def process_startupjobs_api(page_id, user_agent):
    global SESSION
    SESSION.headers.update({
    "Accept": "application/json",
    "User-Agent": user_agent
    })

    if page_id == 1:
        url = STARTUPJOBS_API
    else:
        url = f"{STARTUPJOBS_API}?page={page_id}"

    try:
        response = SESSION.get(url)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            raise ValueError(f"Unexpected content type '{content_type}'")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while making API request: {e}")
    except ValueError as e:
        print(f"Error occurred while processing response: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
    return None

def process_resultset(job_listings):
    for listing in job_listings:
        id = listing.get('id')
        name = listing.get('name')
        if not name:
            continue
        company = listing.get('company')
        image_url = listing.get('imageUrl')
        url = listing.get('url')
        collaborations = listing.get('collaborations')
        locations = listing.get('locations')
        shifts = listing.get('shifts')

        # Create the message string using f-strings
        message = f"<b>{name}</b>\n"
        if company:
            message += f"<b>Společnost</b>: {company}\n"
        if collaborations:
            message += f"<b>Spolupráce</b>: {collaborations}\n"
        if locations:
            message += f"<b>Lokace</b>: {locations}\n"
        if shifts:
            message += f"<b>Úvazek</b>: {shifts}\n"
        if url:
            message += f"<a href=\"https://www.startupjobs.cz{url}\">Více informací zde</a>"

        # Print or send the message with the image URL
        if TESTING_MODE:
            send_message(TG_CHAT_ID, message, image_url)
            exit()
        else:
            if SETTINGS_EXISTS and check_key(id) == False:
                save_key(id)
                send_message(TG_CHAT_ID, message, image_url)
            else:
                save_key(id)



def send_message(chat_id, message, image_url=None):
    params = {
        'chat_id': chat_id,
        'caption': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }

    if image_url:
        files = {
            'photo': requests.get(image_url).content
        }
        response = requests.get(f'{TELEGRAM_API}{TG_API_TOKEN}/sendPhoto', params=params, files=files)
    else:
        response = requests.get(f'{TELEGRAM_API}{TG_API_TOKEN}/sendMessage', params=params)

    return response.json()


def main():
    initialize_settings()
    user_agent = get_random_user_agent()
    
    try:
        # Make the initial API request to get the first page of job listings
        print(f"Processing page 1 of X using user agent {user_agent}")
        data = process_startupjobs_api(1, user_agent)
        job_listings = data['resultSet']
        
        # Process the job listings from the first page
        process_resultset(job_listings)
        
        if (TESTING_MODE):
            exit()
        
        # Process the job listings from subsequent pages, if any
        paginator = data["paginator"]
        current_page = paginator["current"]
        max_page = paginator["max"]
        for page in range(current_page + 1, max_page + 1):
            print(f"Processing page {page} of {max_page}")
            data = process_startupjobs_api(page, user_agent)
            job_listings = data['resultSet']
            process_resultset(job_listings)
    finally:
        save_settings()



main()
