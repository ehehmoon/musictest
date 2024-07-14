import discord
import pathlib
import textwrap
import google.generativeai as genai
from discord.ext import commands


genai.configure(api_key='Ur token')
model = genai.GenerativeModel('gemini-pro')


class GEMINI(commands.Cog):
    """Gemini commands"""

    def __init__(self, bot):
        self = bot



    @commands.command(name='gemini')
    async def gemini(self, ctx, *, prompt):
        response = send_gemini(prompt)
        if not response:
            embed = discord.Embed(title = f'WTF :bomb:', description = 'Gemini got errored 암소소리', colour = 0x000000)

        else:
            embed = discord.Embed(title = f'Gemini Result for ur question:', description = response, colour = 0x0067ff)
        await ctx.send(embed=embed, reference=ctx.message)

def send_gemini(prompt):
    print('ok!')
    response = model.generate_content(prompt)
    return(response.text)

def setup(bot):
    bot.add_cog(GEMINI(bot))
