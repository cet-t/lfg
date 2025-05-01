from datetime import datetime
import yaml
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

# from data import RoleIDsDict
from modals.time import TimeModal
from utils.nullable import nullable
import utils.dpy_utils
from utils.common_utils import file_mode, is_empty
from utils.values import file_path


class ConfigCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(__name__)

    @app_commands.command(name="深夜募集時間帯変更")
    async def change_midnight(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TimeModal())

    # @app_commands.command()
    # @app_commands.describe(midnight="深夜募集")
    # async def register_roles(
    #     self,
    #     interaction: discord.Interaction,
    #     midnight: Optional[discord.Role] = None,
    # ) -> None | discord.InteractionCallbackResponse:
    #     if (guild := interaction.guild) is None:
    #         return
    #     member = await guild.fetch_member(interaction.user.id)
    #     admin_roles = [role for role in member.roles if role.permissions.administrator]
    #     is_admin = is_empty(admin_roles)
    #     if is_admin:
    #         return await interaction.response.send_message(
    #             embed=utils.dpy_utils.create_error_embed(guild, "権限がありません"),
    #             ephemeral=True,
    #         )

    #     role_ids_dict = nullable[RoleIDsDict](None)
    #     with open(
    #         file_path.roles_yml,
    #         file_mode.read,
    #     ) as f:
    #         if (data := yaml.load(f, Loader=yaml.Loader)) is not None:
    #             role_ids_dict.value = RoleIDsDict(data)
    #     if not role_ids_dict.has_value:
    #         role_ids_dict.value = RoleIDsDict(roles={})

    #     if interaction.guild is None:
    #         return

    #     role_ids = role_ids_dict.value.get("roles").get(interaction.guild.id)
    #     if role_ids is None:
    #         return
    #     if midnight is not None:
    #         role_ids["midnight"] = midnight.id

    #     role_ids_dict.value["roles"][interaction.guild.id] = role_ids
    #     if role_ids_dict.has_value:
    #         with open(
    #             file_path.roles_yml,
    #             file_mode.write_override,
    #         ) as f:
    #             yaml.dump(role_ids_dict.value, f, indent=2)

    #     embed = discord.Embed()
    #     embed.add_field(
    #         name="",
    #         value=f"{midnight.mention if midnight is not None else ""}",
    #     )
    #     await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ConfigCog(bot))
