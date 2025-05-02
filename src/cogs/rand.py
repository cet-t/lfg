import random
import discord
from discord.ext import commands
from discord import app_commands
import requests

import utils.dpy_utils
from utils.values import api_url


class RandCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(__name__)

    @app_commands.command(name="武器ルーレット")
    @app_commands.describe(all="【VCのみ】一括抽選")
    async def random_weapon(
        self,
        interaction: discord.Interaction,
        all: bool = False,
    ):
        if all:
            if (guild := interaction.guild) is not None:
                weapon = await guild.fetch_member(interaction.user.id)
                if (
                    (voice := weapon.voice) is not None
                    and (vc := voice.channel) is not None
                    and len(vc_members := vc.members) > 0
                    and (weapons := self.get_weapons()) is not None
                ):
                    weapons = {
                        member: weapons[random.randint(0, len(weapons) - 1)]["name"][
                            "ja_JP"
                        ]
                        for member in vc_members
                    }
                    embed = discord.Embed(title="武器ルーレット")
                    for member, weapon in weapons.items():
                        embed.add_field(
                            name=utils.dpy_utils.mention(
                                utils.dpy_utils.mention_type.user,
                                member.id,
                            ),
                            value=utils.dpy_utils.code_block(weapon),
                        )
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("u-n?", ephemeral=True)
        else:
            weapons = self.get_weapons()
            if weapons is None:
                return await interaction.response.send_message(
                    embed=utils.dpy_utils.create_error_embed(
                        interaction.guild,  # type: ignore
                        "API error",
                    ),
                    ephemeral=True,
                )
            weapon = weapons[random.randint(0, len(weapons) - 1)]
            await interaction.response.send_message(
                embed=self.create_weapon_embed(weapon, interaction.guild)
            )

    @app_commands.command(name="ステージルーレット")
    async def random_stage(self, interaction: discord.Interaction):
        stages = self.get_stages()
        if stages is None:
            return await interaction.response.send_message(
                embed=utils.dpy_utils.create_error_embed(
                    interaction.guild,  # type: ignore
                    "API error",
                ),
                ephemeral=True,
            )
        stage = stages[random.randint(0, len(stages) - 2)]
        await interaction.response.send_message(
            embed=self.create_stage_embed(stage, interaction.guild)
        )

    def get_weapons(self):
        response = requests.get(api_url.stat_ink_weapon)
        if response.status_code != 200:
            return None
        return list(response.json())

    def get_stages(self):
        response = requests.get(api_url.stat_ink_stage)
        if response.status_code != 200:
            return None
        return list(response.json())

    def create_weapon_embed(self, weapon_node, guild: discord.Guild | None):
        embed = discord.Embed(
            title="武器ルーレット",
            description=weapon_node["name"]["ja_JP"],
        )
        utils.dpy_utils.set_footer(embed, guild)
        return embed

    def create_stage_embed(self, stage_node, guild: discord.Guild | None):
        embed = discord.Embed(
            title="ステージルーレット",
            description=stage_node["name"]["ja_JP"],
        )
        utils.dpy_utils.set_footer(embed, guild)
        return embed


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RandCog(bot))
