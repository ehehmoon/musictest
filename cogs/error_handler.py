

from discord.ext import commands
from essentials.errors import MustBeSameChannel, NotConnectedToVoice, PlayerNotConnected


class Errorhandler(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"`{error.param.name}`은 꼭 필요한 요소입니다.")

        if isinstance(error, commands.CommandNotFound):
            await ctx.send('저희는 그런 커맨드 받지 않습니다.')

        if isinstance(error, commands.NotOwner):
            pass

        if isinstance(error, commands.MissingPermissions):
            if len(error.missing_perms) > 1:
                sorno = "권한들"
                isare = "이"
            else:
                sorno = "권한"
                isare = "이"

            perms = ", ".join(error.missing_perms)
            await ctx.send(
                f"{perms.replace('_', ' ').replace('guild', 'server').title()} {sorno}{isare} 필요합니다."
            )

        if isinstance(error, commands.BotMissingPermissions):
            if len(error.missing_perms) > 1:
                sorno = "권한들"
                isare = "이"
            else:
                sorno = "권한"
                isare = "이"

            perms = ", ".join(error.missing_perms)
            await ctx.send(
                f"{perms.replace('_', ' ').replace('guild', 'server').title()} {sorno}{isare} 필요합니다."
            )

        if isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send(
                "연속적으로 같은 명령어를 쓰지 말아주세요"
            )

        if isinstance(error, PlayerNotConnected):
            await ctx.send("저는 보이스챗에 없어요.")

        if isinstance(error, MustBeSameChannel):
            await ctx.send("제가 있는 보이스챗에 들어와주세요.")

        if isinstance(error, NotConnectedToVoice):
            await ctx.send("보이스챗에 안계시네요.")


def setup(bot):
    bot.add_cog(Errorhandler(bot))
