from typing import Final
import discord

from data import Playing
from uis.lfg.vc_view import NawabariVCView


class PlayingView(discord.ui.View):
    playing_options: Final = [
        discord.SelectOption(label="ナワバリ", value="ナワバリ"),
        discord.SelectOption(label="バンカラ", value="バンカラ"),
        discord.SelectOption(label="プラベ", value="プラベ"),
        discord.SelectOption(label="バイト", value="バイト"),
        discord.SelectOption(label="なんでも", value="なんでも"),
    ]

    def __init__(self) -> None:
        super().__init__(timeout=120)
        self.__playing: Playing

    async def on_timeout(self) -> None:
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

    @discord.ui.select(
        placeholder="遊び方",
        min_values=1,
        max_values=1,
        options=playing_options,
    )
    async def playing_select(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select,
    ) -> None:
        self.__playing = Playing(select.values[0])
        match self.__playing:
            case Playing.ナワバリ:
                await interaction.response.send_message(
                    view=NawabariVCView(self.__playing)
                )
            case Playing.バンカラ:
                await interaction.response.send_message("")
            case Playing.プラベ:
                await interaction.response.send_message("")
            case Playing.バイト:
                await interaction.response.send_message("")
            case Playing.なんでも:
                await interaction.response.send_message("")
