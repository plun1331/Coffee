import discord
import re
import asyncio

from discord.ext import commands
from utils import checks, default
from utils.database import sqlite, create_tables



# https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/mod.py <--- Source
class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"Member {argument} does not exist.") from None
        else:
            return m.id


class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = argument

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f'reason that is being inputted is too long ({len(argument)}/{reason_max})')
        return ret


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite.Database()
    
    def logs(self, guild_id):
        data = self.db.fetchrow("SELECT * FROM Logging WHERE guild_id=?", (guild_id,))
        if data:
            return data["logs_id"]
        else:
            return None

    @commands.command(
      name="kick",
      help="Kick a user from the server!",
      usage="@elf#2169 posting memes in general"
    )
    @commands.guild_only()
    @checks.has_permissions(kick_members=True)
    async def kick_(self, ctx : commands.Context, member: discord.Member, *,   reason: str = None):
      """ Kicks a user from the server. """
      if await checks.check_priv(ctx, member):
             return
      try:
          await member.kick(reason=default.responsible(ctx.author, reason))
          embed = discord.Embed(
            color = 0x2F3136
          )
          embed.set_footer(text=f"Command invoked by {ctx.author}")
          embed.set_author(name=f"✅ {member.name} has been kicked from the server", icon_url=member.avatar_url)
          await ctx.send(embed=embed)
          await member.send(f"You've been kicked from **{ctx.guild.name}** for **{reason}** by **{ctx.author}**")

          log_channel = self.bot.get_channel(self.logs(ctx.guild.id))
          if log_channel:
            embed = discord.Embed(
              title="Kick 📝",
              description=f"**User Kicked:** `{member}`\n**Moderator:** `{ctx.author}`\n**Reason:** `{reason}`"
            )
          await log_channel.send(embed=embed)

      except Exception as e:
          await ctx.send(e)

    @commands.command(
      name="ban",
      help="Ban a user from the server.",
      usage="@elf#2169 being an idiot >:("
    )
    @commands.guild_only()
    @checks.has_permissions(ban_members=True)
    async def banish(self, ctx : commands.Context, member: discord.Member, *,   reason: str = None):
      """ Bans a user from the server. """
      if await checks.check_priv(ctx, member):
             return
      try:
          await member.ban(reason=default.responsible(ctx.author, reason))
          embed = discord.Embed(
            color = 0x2F3136
          )
          embed.set_footer(text=f"Command invoked by {ctx.author}")
          embed.set_author(name=f"✅ {member.name} has been banned from the server", icon_url=member.avatar_url)
          await ctx.send(embed=embed)
          await member.send(f"You've been banned from **{ctx.guild.name}** for **{reason}** by **{ctx.author}**")

          log_channel = self.bot.get_channel(self.logs(ctx.guild.id))
          if log_channel:
            embed = discord.Embed(
              title="Ban 📝",
              description=f"**User banned:** `{member}`\n**Moderator:** `{ctx.author}`\n**Reason:** `{reason}`"
            )
          await log_channel.send(embed=embed)

      except Exception as e:
          await ctx.send(e)
    
    


def setup(bot):
    bot.add_cog(Moderation(bot))
