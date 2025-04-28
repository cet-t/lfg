import asyncio
import os
import discord
from discord.ext import commands


class Bot(commands.Bot):
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(__name__)

    def setup_cog(self, cog_dir: str) -> None:
        if not os.path.exists(cog_dir):
            return

        cogs = [
            f"{os.path.dirname(cog_dir)}.{file.split(".")[0]}".split("/")[-1]
            for file in os.listdir(cog_dir)
            if not file.startswith("__")
        ]
        for cog in cogs:
            asyncio.run(self.load_extension(cog))

    def get_token(self, name: str = "TOKEN") -> str:
        try:
            import dotenv

            dotenv.load_dotenv()
            return os.environ[name]
        except:
            import envv

            return envv.environ[name]

    async def setup_hook(self) -> None:
        guilds = [732942987331633202]
        for guild in guilds:
            await self.tree.sync(guild=discord.Object(guild))
        await self.tree.sync()


if __name__ == "__main__":
    bot = Bot(command_prefix="!", intents=discord.Intents.all())
    bot.setup_cog("./src/cogs/")
    bot.run(bot.get_token())
