import requests
from settings import USERNAME, USERNAME_BOT, CLIENT_ID, CLIENT_SECRET, BOT_CLIENT_ID, BOT_CLIENT_SECRET, OWNER_ID, BOT_ID
def get_id_of_user(cid, csecret, username):
    url = "https://id.twitch.tv/oauth2/token"
    json = {'client_id': cid, 'client_secret': csecret, 'grant_type': 'client_credentials'}
    # Uncomment these lines to get a token
    x = requests.post(url, json=json)
    if x.status_code != 200:
        print("Error with API request!")
        return
    access_token = x.json()['access_token']
    json = {'Authorization': 'Bearer '+ access_token, 'Client-Id': cid}
    url = "https://api.twitch.tv/helix/users"
    # The result of this request contains the needed user ids
    with requests.Session() as s:
        s.params = {'login': username}
        r = s.get(url, headers=json)
        r.raise_for_status()
        data = r.json()
        # TODO: What to do with output??
        return data['data'][0]['id']

def insert_id(strname, id):
    with open('settings.py', 'r') as f:
        text = f.read()
        

def main():
    bot_id = get_id_of_user(BOT_CLIENT_ID, BOT_CLIENT_SECRET, USERNAME_BOT)
    print(f'Add the following to your settings file: BOT_ID {bot_id}')
    user_id = get_id_of_user(CLIENT_ID, CLIENT_SECRET, USERNAME)
    print(f'Add the following to your settings file: USER_ID {user_id}')

if __name__ == "__main__":
    main()