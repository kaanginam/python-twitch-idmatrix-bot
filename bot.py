import asyncio
import logging
import sqlite3
from settings import BOT_CLIENT_ID, BOT_CLIENT_SECRET, BOT_ID, OWNER_ID, ADDR, IMGPATH, SIZE
import asqlite
import twitchio
from twitchio.ext import commands
from twitchio import eventsub
from idotmatrix import ConnectionManager
from idotmatrix import Gif
import seventv
import urllib.request
import os
from PIL import Image
LOGGER: logging.Logger = logging.getLogger("Bot")

class Bot(commands.Bot):
    def __init__(self, *, imgpath: str, address: str, size: str, token_database: asqlite.Pool) -> None:
        self.token_database = token_database
        self.imgpath = imgpath
        self.address = address
        self.idmconnection = ConnectionManager()
        self.size = size
        self.gif = Gif()
        super().__init__(
            client_id=BOT_CLIENT_ID,
            client_secret=BOT_CLIENT_SECRET,
            bot_id=BOT_ID,
            owner_id=OWNER_ID,
            prefix="!",
        )

    async def setup_hook(self) -> None:
        # Add our component which contains our commands...
        await self.add_component(IDMComponent(self))

        # Subscribe to read chat (event_message) from our channel as the bot...
        # This creates and opens a websocket to Twitch EventSub...
        subscription = eventsub.ChatMessageSubscription(broadcaster_user_id=OWNER_ID, user_id=BOT_ID)
        await self.subscribe_websocket(payload=subscription)

        # Subscribe and listen to when a stream goes live..
        # For this example listen to our own stream...
        subscription = eventsub.StreamOnlineSubscription(broadcaster_user_id=OWNER_ID)
        await self.subscribe_websocket(payload=subscription)

    async def add_token(self, token: str, refresh: str) -> twitchio.authentication.ValidateTokenPayload:
        # Make sure to call super() as it will add the tokens interally and return us some data...
        resp: twitchio.authentication.ValidateTokenPayload = await super().add_token(token, refresh)

        # Store our tokens in a simple SQLite Database when they are authorized...
        query = """
        INSERT INTO tokens (user_id, token, refresh)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            token = excluded.token,
            refresh = excluded.refresh;
        """

        async with self.token_database.acquire() as connection:
            await connection.execute(query, (resp.user_id, token, refresh))

        LOGGER.info("Added token to the database for user: %s", resp.user_id)
        return resp

    async def load_tokens(self, path: str | None = None) -> None:
        # We don't need to call this manually, it is called in .login() from .start() internally...

        async with self.token_database.acquire() as connection:
            rows: list[sqlite3.Row] = await connection.fetchall("""SELECT * from tokens""")

        for row in rows:
            await self.add_token(row["token"], row["refresh"])

    async def setup_database(self) -> None:
        # Create our token table, if it doesn't exist..
        query = """CREATE TABLE IF NOT EXISTS tokens(user_id TEXT PRIMARY KEY, token TEXT NOT NULL, refresh TEXT NOT NULL)"""
        async with self.token_database.acquire() as connection:
            await connection.execute(query)

    async def event_ready(self) -> None:
        LOGGER.info("Successfully logged in as: %s", self.bot_id)
        await self.idmconnection.connectByAddress(self.address)

class IDMComponent(commands.Component):
    def __init__(self, bot: Bot):
        # Passing args is not required...
        # We pass bot here as an example...
        self.bot = bot
    # TODO: find out how cooldown works
    async def event_command_error(self, ctx, error: Exception) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply("Your chosen command is on cooldown right now!")
    # listens to every chat message
    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        print(f"[{payload.broadcaster.name}] - {payload.chatter.name}: {payload.text}")
    # All viable commands: !show, !idm, !display
    @commands.command(aliases=["show", "idm"], cooldowns_before_guards=True)
    async def display(self, ctx: commands.Context) -> None:
        if ctx.chatter.mention in ['StreamElements', 'Streamlabs']:
            return
        splitted = ctx.message.text.split(" ")
        if len(splitted) < 3:
            await ctx.reply("This command allows you to send any emote from 7tv to " \
            "the iDotMatrix (the screen you can see). " \
            "Please provide an emote name and a number! The number represents the how many-th emote " \
            "to show (starts counting from zero). This search is case-sensitive. Example: '!idm floppaJAM 0'")
            return
        emote_num = splitted[2]
        target = splitted[1] 
        filename_orig = self.bot.imgpath + target + ".webp"
        filename_new = self.bot.imgpath + target + '.gif'
        if not os.path.isfile(filename_new):
            seventvobj = seventv.seventv()
            emotes = await seventvobj.emote_search(target, case_sensitive=True)
            myEmote = emotes[int(emote_num)] 
            full_url = 'https:' + myEmote.host_url + '/2x.webp'
            await seventvobj.close()
            urllib.request.urlretrieve(full_url, filename_orig)
            im = Image.open(filename_orig)
            im.save(filename_new, 'gif', save_all=True)
        await self.bot.gif.uploadProcessed(file_path=filename_new,pixel_size=int(self.bot.size),)

def main() -> None:
    twitchio.utils.setup_logging(level=logging.INFO)

    async def runner() -> None:
        async with asqlite.create_pool("tokens.db") as tdb, Bot(imgpath=IMGPATH, address=ADDR, size=SIZE, token_database=tdb) as bot:
            await bot.setup_database()
            await bot.start()

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        LOGGER.warning("Shutting down due to KeyboardInterrupt...")


if __name__ == "__main__":
    main()