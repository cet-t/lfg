from datetime import time
import os
from typing import Optional
import discord

from utils.dpy_utils import create_error_embed, create_log_embed


class TimeModal(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title="時間指定", custom_id="time_modal")

        self.__start = discord.ui.TextInput(
            label="開始時間",
            placeholder="1:00",
        )
        self.__end = discord.ui.TextInput(
            label="終了時間",
            placeholder="7:00",
        )

        self.add_item(self.__start)
        self.add_item(self.__end)

    @property
    def start(self) -> Optional[time]:
        return self.__parse(self.__start.value)

    @property
    def end(self) -> Optional[time]:
        return self.__parse(self.__end.value)

    def __parse(self, value: str) -> Optional[time]:
        values = None if value is None else value.split(":")
        return (
            None if values is None else time(hour=int(values[0]), minute=int(values[1]))
        )

    def __to_str(self, time: time | None) -> str:
        return (
            f"{time.hour.__str__().zfill(2)}:{time.minute.__str__().zfill(2)}"
            if time is not None
            else ""
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            with open("./data/midnight.yml", "w") as f:
                pass

            await interaction.response.send_message(
                embed=create_log_embed(
                    interaction.guild,  # type: ignore
                    f"{self.__to_str(self.start)}~{self.__to_str(self.end)}",
                ),
                ephemeral=True,
            )
        except:
            await interaction.response.send_message(
                embed=create_error_embed(
                    interaction.guild,  # type: ignore
                    f"error.",
                ),
                ephemeral=True,
            )
