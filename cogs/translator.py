import discord
from discord.ext import commands
import googletrans

class Translator(commands.Cog):
    """Translator commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='tr')
    async def tr(self, ctx, lang_to, args: str):
        lang_to = lang_to.lower()
        if lang_to not in googletrans.LANGUAGES and lang_to not in googletrans.LANGCODES:
            return await ctx.send(f"**Invalid language**", reference=ctx.message)
        
        text = ' '.join(args)
        translator = googletrans.Translator()
        text_translated = translator.translate(text, dest=lang_to).text
        await ctx.send(f"Result: **{text_translated}**", reference=ctx.message)

def setup(bot):
    bot.add_cog(Translator(bot))