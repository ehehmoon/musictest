import discord
from discord.ext import commands

class jjamtong(commands.Cog):
    """jjamtong desu"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='avatar', aliases=['av'])
    async def avatar(self, ctx, *, member: discord.Member = None):
        if not member:
            member = ctx.message.author
        
        embed = discord.Embed(title=f"**{member}**님의 프사")
        embed.set_image(url=member.avatar_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(jjamtong(bot))