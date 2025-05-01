import asyncio
import os
import discord
from discord.ext import commands


class Bot(commands.Bot):
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.change_presence(
            activity=discord.Game("準備中..."),
            status=discord.Status.idle,
        )
        await self.tree.sync()
        print(__name__)
        await self.change_presence(
            activity=discord.Streaming(
                name="Splatoon 3",
                url="https://twitch.tv/example",
            ),
        )

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

    def __get_token(self, name: str) -> str:
        try:
            import dotenv

            dotenv.load_dotenv()
            return os.environ[name]
        except:
            import envv

            return envv.environ[name]

    async def setup_hook(self) -> None:
        await self.tree.sync()

    def run(self, token_name: str = "TOKEN") -> None:
        super().run(self.__get_token(token_name))


if __name__ == "__main__":
    bot = Bot(command_prefix=["!", "?"], intents=discord.Intents.all())
    bot.setup_cog("./src/cogs/")
    bot.run()
