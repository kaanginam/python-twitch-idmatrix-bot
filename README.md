# Python-iDotMatrix Bot

This is a simple bot which aims to use twitch commands to control an iDotMatrix, currently jumbled together using different libraries. The most important libraries are the twitchio library and the idotmatrix library. 

To summarize, the command is supposed to be something like `!idm Pepega 0`. The code then uses the 7tv API, takes the first search result for "Pepega" and saves the image of that emote.

Most of the bot code is the outline of the [Quickstart guide](https://twitchio.dev/en/latest/getting-started/quickstart.html) from the twitchio library - only the component has some custom code regarding the command and the 7tv emote downloading and converting. But more features are planned. 

**WARNING**: This is just my first commit, please only use this with care.

## Requirements

1. Prior setup of a bot account on twitch (helpful script included)
2. Something in your home network to run this with (Raspi, any computer, laptop etc.). IMPORTANT: You need a device with Bluetooth to send messages to the iDotMatrix via Bluetooth. So the device also needs to be in close proximity to the iDotMatrix
3. An iDotMatrix, you can buy them cheap from AliExpress

## Setup 

First, install (example installation for linux but there is currently no reason for it to not work on windows):
```bash
sudo apt install python3 python3-virtualenv
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

Afterwards, decide on where you would like to save the found emotes by entering into a `settings.py` a path. Then you will need to find out the address of your iDotMatrix. 

```bash
source venv/bin/activate
# following command prints the device address, example: "00:11:22:33:44". 
python3 get_idm_address.py
```

Then, you will need to create a new bot account on twitch. Follow these steps:
1. On your usual twitch channel, go into account settings and allow your e-mail and phone number to be used for more than one account
2. Sign up your bot account
3. Enable 2FA for your bot account
4. Go to the [Twitch Dev Console](https://dev.twitch.tv/console), log in as bot
5. Register your app, make sure to use http://localhost:4343/oauth/callback as callback URL
6. Then, there should be a client id after generating it. There is also a button to generate a client secret. Copy both into a local file here, `settings.py`
7. Now, repeat step 4-7 with the non-bot account
8. Execute `python3 get_ids.py` after entering the client ids and secret for both accounts. This will print out the user ids of the bot and the non-bot twitch account. Then add these to the settings file.

The next few steps are directly from the [twitchio guide](https://twitchio.dev/en/latest/getting-started/quickstart.html) and are regarding the file `bot.py`. You will only have to these steps once.: 

9. Comment out everything in `setup_hook`
10. Run the bot
11. Open a new browser (a different one than your usual or in incognito), login as bot, visit [this](http://localhost:4343/oauth?scopes=user:read:chat%20user:write:chat%20user:bot) link
12. In the main browser, where your non-bot account is logged in, open [this](http://localhost:4343/oauth?scopes=channel:bot) link
13. Stop the bot, then uncomment everything in `setup_hook``
14. Start bot 

For any of the settings, refer to the file `example_settings.py` file for what settings you need.

## Running

After setup, just run the code with `source venv/bin/activate && python3 bot.py`. To run as script running in background, you can just do simple linux trick:

`source venv/bin/activate && python3 bot.py &`

To stop the running process, check running processes with `ps aux`, find the python script, then copy the PID. Then run `kill PID`.

You can also use the provided service file for systemd based systems. Requires sudo.
```bash
sudo cp twitchidmbot.service /etc/systemd/system/
sudo systemctl daemon-reload
# ONLY execute this line if you want this script to be executed at system startup! Beware that running a bot in the background may have unwanted effects
sudo systemctl enable twitchidmbot.service
sudo systemctl start twitchidmbot.service
```
If you want to view the logs of the service, then you can find them in the `journalctl` logs.

## Bot outline

Example input: `!idm Pepega 0`

1. Use 7tv api to search for emote `Pepega`
2. Download the emote using the .webp version of the second largest representation (7tv offers 1x.webp to 4x.webp. 1x.webp would be more optimal for small screen resolutions)
3. Convert the webp file to gif using python image library
4. Send the GIF to the IDM

## Some notes/problems

- Can be slow to send the GIF to the IDM, based on proximity + size of GIF
- Can fill up storage quickly theoretically, but only downloads an emote once (this allows for DDoS attacks)
- Needs more cleanup, perhaps automated way of getting bot and user id. 

## TODO List

- Command cooldown, user cooldown
- Extra functions -> sending images using links, sending text
- File cleanups after downloading the webp and converting? Increaes time it takes for displaying same emote multiple times... make it optional perhaps
- Forgot to remove the fixed sizes for IDM screens
- better logging