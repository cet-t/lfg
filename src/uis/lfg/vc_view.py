import discord

from data import Playing


class NawabariVCView(discord.ui.View):
    def __init__(self, playing: Playing) -> None:
        super().__init__(timeout=120)
        self.__playing: Playing = playing
        self.__vc_id: int

    @discord.ui.select(
        placeholder="使用VC",
        min_values=1,
        max_values=1,
        channel_types=[discord.ChannelType.voice],
        options=[
            discord.SelectOption(
                label="VC1",
                value="https://discord.com/channels/732942987331633202/882616446302187580",
            ),
            discord.SelectOption(label="VC2", value="VC2"),
            discord.SelectOption(label="VC3", value="VC3"),
            discord.SelectOption(label="VC4", value="VC4"),
        ],
    )
    async def select(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select,
    ):
        await interaction.response.defer()
        print(select.values[0])
        await interaction.response.send_message(f"{select.values[0]}, {self.__playing}")

    async def on_timeout(self) -> None:
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
