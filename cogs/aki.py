import discord
import asyncio
import akinator
from discord.ext import commands
from akinator.async_aki import Akinator
from discord.ext.commands import BucketType


aki = Akinator()
emojis_c = ['✅', '❌', '🤷', '👍', '👎', '⏮', '🛑']
emojis_w = ['✅', '❌']


def w(name, desc, picture):
        embed_win = discord.Embed(title=f"{name} ({desc})라고 생각합니다! 제가 맞혔나요?", colour=0x00ff00)
        embed_win.set_image(url=picture)
        return embed_win

class Aki(commands.Cog):
    """Aki commands"""

    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='aki', aliases=["아키"])
    @commands.max_concurrency(1, per=BucketType.default, wait=False)
    async def aki(self, ctx):
        user = ctx.author
        print('command verificated')
        desc_loss = ''
        d_loss = ''
        print('initialization conformed')

        def check_c(reaction, user):
            return user == ctx.author and str(reaction.emoji) in emojis_c
        
        def check_w(reaction, user):
            return user == ctx.author and str(reaction.emoji) in emojis_w
        
        
        q = await aki.start_game(child_mode=False, language='kr')
        count = 0

        print('check finished')

        embed_question = discord.Embed(title='주의사항: 모든 이모지가 추가 된 후 이모지를 눌러주세요.', colour=0x00ff00)
        await ctx.send(embed=embed_question)
        

        while aki.progression <= 85:
            
            
            embed_quiz = discord.Embed(title='아키쨩의 질문!', description=q, colour=0x00ff00)
            msg = await ctx.send(embed=embed_quiz)

            for m in emojis_c:
                await msg.add_reaction(m)

            try:
                symbol, username = await self.bot.wait_for('reaction_add', timeout=45.0, check=check_c)
            
            except asyncio.TimeoutError:
                await msg.delete()
                embed_game_ended = discord.Embed(title='언제오노..', colour=0x00ff00)
                await ctx.send(embed=embed_game_ended)
                return
            
            if str(symbol) == emojis_c[0]:
                answer = 'yes'
            elif str(symbol) == emojis_c[1]:
                answer = 'no'
            elif str(symbol) == emojis_c[2]:
                answer = 'idk'
            elif str(symbol) == emojis_c[3]:
                answer = 'p'
            elif str(symbol) == emojis_c[4]:
                answer = 'pn'
            elif str(symbol) == emojis_c[5]:
                answer = 'back'
            elif str(symbol) == emojis_c[6]:
                await msg.delete()
                embed_game_ended = discord.Embed(title='파악~식노 ㅋㅋ', colour=0x00ff00)
                await ctx.send(embed=embed_game_ended)
                return
            
            if answer == 'back':
                try:
                    await msg.delete()
                    q = await aki.back()
                except akinator.CantGoBackAnyFurther:
                    pass
            else:
                await msg.delete()
                count = count + 1
                print(count)
                q = await aki.answer(answer)
                
            
        await aki.win()

        win_message = await ctx.send(embed=w(aki.first_guess['name'], aki.first_guess['description'], aki.first_guess['absolute_picture_path']))

        for e in emojis_w:
            await win_message.add_reaction(e)

        try:
            s, u = await self.bot.wait_for('reaction_add', timeout=30.0, check=check_w)

        except asyncio.TimeoutError:
            for times in aki.guesses:
                d_loss = d_loss + times['name'] + '\n'
            t_loss = '제가 생각한 사람들의 리스트임니다 :'
            embed_loss = discord.Embed(title=t_loss, description=d_loss, colour=0x00ff00)
            await ctx.send(embed=embed_loss)
            return
        
        if str(s) == emojis_w[0]:
            embed_win = discord.Embed(title=f'앗싸! {count}번 만에 맞혔다!', colour=0x00ff00)
            await ctx.send(embed=embed_win)
            print(f"aki: {aki.first_guess['name']}")

        elif str(s) == emojis_w[1]:
            for times in aki.guesses:
                desc_loss = desc_loss + times['name'] + '\n'
            title_loss = '다음엔 제가 이길테니까요.. 제가 생각한 사람들의 리스트임니다 :'
            embed_loss = discord.Embed(title=title_loss, description=desc_loss, colour=0x00ff00)
            await ctx.send(embed=embed_loss)

def setup(bot):
    bot.add_cog(Aki(bot))