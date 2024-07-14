import discord
from discord.ext import commands
import gspread

credential = {

}

gc = gspread.service_account_from_dict(credential)


class 총력전(commands.Cog):
    """총력전 commands"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='총력전')
    async def 총력전(self, ctx):
        sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1JGBeDCu8KtVIsWd4QbQhNJekeG1YD8ZmGmbfXYznT7k/edit#gid=1190002439')

        worksheet = sh.worksheet("총력전 분포도")

        first = worksheet.acell('D9').value
        platinum_cut = worksheet.acell('D10').value  
        season = worksheet.acell('C2:C3').value
        name = worksheet.acell('D2:E3').value
        population = worksheet.acell('H16:H17').value
        first_cost = worksheet.acell('H10').value
        platinum_cut_cost = worksheet.acell('H11').value
        embed = discord.Embed(title=f'{season} 총력전 통계: {name}')
        embed.add_field(name='1위', value=f'{first}점/사용 코스트: {first_cost}', inline=False)
        embed.add_field(name='플레컷', value=f'{platinum_cut}점/사용 코스트: {platinum_cut_cost}', inline=False)
        embed.add_field(name='인구수', value=f'{population}', inline=False)
        
        await ctx.send(embed=embed, reference=ctx.message)


def setup(bot):
    bot.add_cog(총력전(bot))
