import json
import random
import discord
from discord.ext import commands
from discord import app_commands
import requests

from data import WeaponsDict
from nullable import nullable
from utils.util import dpy_util, encoding_type, loading_mode, mention_type
from utils.values import api_url

WEAPONS_PATH = "./data/weapons.json"


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
    ) -> None:
        if all:
            if (guild := interaction.guild) is not None:
                member_weapon = await guild.fetch_member(interaction.user.id)
                if (
                    (voice := member_weapon.voice) is not None
                    and (vc := voice.channel) is not None
                    and len(vc_members := vc.members) > 0
                    and (weapons := self.get_weapons()) is not None
                ):
                    members_weapon = {
                        member: weapons[random.randint(0, len(weapons) - 1)]["name"][
                            "ja_JP"
                        ]
                        for member in vc_members
                    }
                    embed = discord.Embed(title="武器ルーレット")
                    for member, weapon in members_weapon.items():
                        embed.add_field(
                            name=dpy_util.mention(
                                mention_type.user,
                                nullable(member.id),
                            ),
                            value=dpy_util.code_block(weapon),
                        )
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("u-n?", ephemeral=True)
        else:
            members_weapon = self.get_weapons()
            if members_weapon is None:
                return
            member_weapon = members_weapon[random.randint(0, len(members_weapon) - 1)]
            await interaction.response.send_message(
                embed=self.create_weapon_embed(member_weapon, interaction.guild)
            )

    def get_weapons(self):
        response = requests.get(api_url.stat_ink_weapon)
        if response.status_code != 200:
            return None
        res_json = list(response.json())
        return res_json

    def create_weapon_embed(self, weapon_node, guild: discord.Guild | None):
        embed = discord.Embed(
            title="武器ルーレット",
            description=weapon_node["name"]["ja_JP"],
        )
        dpy_util.set_footer(embed, guild)
        return embed


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RandCog(bot))
