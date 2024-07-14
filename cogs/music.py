import asyncio
from os import replace
import re
import aiohttp
from aiohttp.helpers import current_task
import discord
import wavelink
from essentials.player import WebPlayer
from discord.ext import commands
from essentials.checks import in_same_channel, player_connected, voice_connected
from datetime import datetime
from pytz import timezone
import time



class Music(commands.Cog):
    """Music commands"""

    def __init__(self, bot):
        self.bot = bot
        self.URL_REG = re.compile(r"https?://(?:www\.)?.+")

    @commands.command(name="connect", aliases=["con", "c", "join"])
    @voice_connected()
    async def connect_(self, ctx):
        """Connect the player"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if player.is_connected:
            if not player.bound_channel:
                player.bound_channel = ctx.channel

            if player.channel_id == ctx.channel.id:
                return await ctx.send(
                    "이미 들어와있어요!"
                )

            return await ctx.send(
                f"봇이 다른 채널에 들어가있어요."
            )

        channel = ctx.author.voice.channel
        self.bot.voice_users[ctx.author.id] = channel.id

        msg = await ctx.send(f"**`{channel.name}`**에 들어가는중...")
        await player.connect(channel.id)
        player.bound_channel = ctx.channel
        print(f"join the channel: {channel.id}/{channel.name}: {datetime.now(timezone('Asia/Seoul')).strftime('%F %H시 %M분')}")
        File = open("log.txt", "a")
        File.write(f"join the channel: {channel.id}/{channel.name}: {datetime.now(timezone('Asia/Seoul')).strftime('%F %H시 %M분')}\n")
        File.close()
        await msg.edit(
            content=f" **`{channel.name}`**에 들어왔어요!"
        )

    @commands.command(name="disconnect", aliases=["dc", "fuckoff", "leave"])
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def disconnect_(self, ctx):
        """Destroy the player"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)
        channel = ctx.author.voice.channel
        await ctx.send(f'**`{channel.name}`**에서 나갔어요' )
        print(f"quit the channel: {channel.id}/{channel.name}: {datetime.now(timezone('Asia/Seoul')).strftime('%F %H시 %M분')}")
        File = open("log.txt", "a")
        File.write(f"quit the channel: {channel.id}/{channel.name}: {datetime.now(timezone('Asia/Seoul')).strftime('%F %H시 %M분')}\n")
        File.close()
        await player.destroy()
        

    @commands.command(name="play", aliases=["p"])
    @voice_connected()
    async def play_(self, ctx, *, query):
        """Play or add song to queue"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if not player.is_connected:
            await ctx.invoke(self.connect_)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"저는 여기에 있어요: {player.bound_channel.mention}", delete_after=5
            )

        msg = await ctx.send(f"`{query}`찾는중 :mag_right:")
        query = query.strip("<>")
        if not self.URL_REG.match(query):
            query = f"ytsearch:{query}"

        tracks = await self.bot.wavelink.get_tracks(query)

        if not tracks:
            return await msg.edit(content="노래를 못찾았어요.." )

        if isinstance(tracks, wavelink.TrackPlaylist):
            for track in tracks.tracks:
                await player.queue.put(track)

            msg.edit(
                content=f'**{tracks.data["playlistInfo"]["name"]}**({len(tracks.tracks)}) 플리를 추가했어요!'
            )
        else:
            await player.queue.put(tracks[0])
            print(f"{ctx.author.name}({ctx.author.id}) added {str(tracks[0])} in queue: {datetime.now(timezone('Asia/Seoul')).strftime('%F %H시 %M분')}")
            File = open("log.txt", "a")
            File.write(f"{ctx.author.name}({ctx.author.id}) added {str(tracks[0])} in queue: {datetime.now(timezone('Asia/Seoul')).strftime('%F %H시 %M분')}\n")
            File.close()
            await msg.edit(content=f"대기열에 **{str(tracks[0])}**를 추가했어요." )

        if not player.is_playing:
            await player.do_next()

    @commands.command()
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def skip(self, ctx):
        """Skip currently playing song"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"저는 여기에 있어요: {player.bound_channel.mention}", delete_after=5
            )

        current_loop = player.loop
        player.loop = "NONE"

        await player.stop()

        if current_loop != "CURRENT":
            player.loop = current_loop
        
        await ctx.send('노래를 넘겼어요.')

    @commands.command(name='pause', aliases=["stop"])
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def pause(self, ctx):
        """Pause the player"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"저는 여기에 있어요: {player.bound_channel.mention}", delete_after=5
            )

        if player.is_playing:
            if player.is_paused:
                return await ctx.send("이미 멈췄는데.." )

            await player.set_pause(pause=True)
            return await ctx.send("멈췄어요!" )

        await ctx.send("저 지금 아무것도 안하는데.." )

    @commands.command()
    @player_connected()
    @voice_connected()
    @in_same_channel()
    async def resume(self, ctx):
        """Resume the player"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"저는 여기에 있어요: {player.bound_channel.mention}", delete_after=5
            )

        if player.is_playing:
            if not player.is_paused:
                return await ctx.send("재생중인데.." )

            await player.set_pause(pause=False)
            return await ctx.send("다시 틀게요!" )

        await ctx.send("저 지금 아무것도 안하는데.." )

    @commands.command()
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def seek(self, ctx, seconds: int, reverse: bool = False):
        """Seek the player backward or forward"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"저는 여기에 있어요: {player.bound_channel.mention}", delete_after=5
            )

        if player.is_playing:
            if not player.is_paused:
                if not reverse:
                    new_position = player.position + (seconds * 1000)
                    if new_position > player.current.length:
                        new_position = player.current.length
                else:
                    new_position = player.position - (seconds * 1000)
                    if new_position < 0:
                        new_position = 0

                await player.seek(new_position)
                return await ctx.send(f"Player has been seeked {seconds} seconds.")

            return await ctx.send(
                "노래가 멈춰져있어요. !resume하고 다시 시도해봐요 XD"
            )

        await ctx.send("Player is not playing anything.")

    @commands.command(aliases=["vol"])
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def volume(self, ctx, vol: int, forced=False):
        """Set volume"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"저는 여기에 있어요: {player.bound_channel.mention}", delete_after=5
            )

        if vol < 0:
            return await ctx.send("음량은 0보다 작을 순 없어요..")

        if vol > 100 and not forced:
            return await ctx.send("음량은 100보다 클 순 없어요..")

        await player.set_volume(vol)
        await ctx.send(f"음량을 {vol}으로 맞췄어요!")

    @commands.command()
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def loop(self, ctx, type: str):
        """Set loop to `NONE`, `CURRENT` or `PLAYLIST`"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Player is bounded to {player.bound_channel.mention}", delete_after=5
            )

        valid_types = ["NONE", "CURRENT", "PLAYLIST"]
        type = type.upper()

        if type not in valid_types:
            return await ctx.send("반복재생의 타입은 `NONE`, `CURRENT`, `PLAYLIST`입니다.")

        if len(player.queue._queue) < 1 and type == "PLAYLIST":
            return await ctx.send(
                "플리 반복재생 하려면 두 곡이상 있어야 해요."
            )

        if not player.is_playing:
            return await ctx.send("아무 노래도 틀지 않아서 반복재생 할 수 없어요.")

        player.loop = type

        await ctx.send(f"`{type}`타입으로 반복재생을 시작합니다.")

    @commands.command(aliases=["np"])
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def nowplaying(self, ctx):
        """What's playing now?"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Player is bounded to {player.bound_channel.mention}", delete_after=5
            )

        if not player.current:
            return await ctx.send("아무것도 안틀었어요..")

        await player.invoke_player()

    @commands.command(aliases=["q"])
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def queue(self, ctx):
        """Player's current queue"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Player is bounded to {player.bound_channel.mention}", delete_after=5
            )

        queue = player.queue._queue
        if len(queue) < 1:
            return await ctx.send("있었는데, 없었습니다.")

        embed = discord.Embed(color=discord.Color(0x2F3136))
        embed.set_author(name="대기열", icon_url="https://thenounproject.com/api/private/icons/4547937/edit/?backgroundShape=SQUARE&backgroundShapeColor=%23000000&backgroundShapeOpacity=0&exportSize=752&flipX=false&flipY=false&foregroundColor=%23000000&foregroundOpacity=1&imageFormat=png&rotation=0")

        tracks = ""
        if player.loop == "CURRENT":
            next_song = f"다음곡 > [{player.current.title}]({player.current.uri}) \n\n"
        else:
            next_song = ""

        if next_song:
            tracks += next_song

        for index, track in enumerate(queue):
            tracks += f"{index + 1}. [{track.title}]({track.uri}) \n"

        embed.description = tracks

        await ctx.send(embed=embed)

    @commands.command(aliases=["eq"])
    @voice_connected()
    @player_connected()
    @in_same_channel()
    async def equalizer(self, ctx):
        """Set equalizer"""
        player: WebPlayer = self.bot.wavelink.get_player(ctx.guild.id, cls=WebPlayer)

        if ctx.channel != player.bound_channel:
            return await ctx.send(
                f"Player is bounded to {player.bound_channel.mention}", delete_after=5
            )

        eqs = {
            "1️⃣": ["Flat", wavelink.eqs.Equalizer.flat()],
            "2️⃣": ["Boost", wavelink.eqs.Equalizer.boost()],
            "3️⃣": ["Metal", wavelink.eqs.Equalizer.metal()],
            "4️⃣": ["Piano", wavelink.eqs.Equalizer.piano()],
        }

        embed = discord.Embed(title="EQ를 골라주세요!")
        embed.description = f"현재의 EQ - **{player.eq.name}**\n\n1. Flat \n2. Boost\n3. Metal\n4. Piano"
        embed.set_thumbnail(url="https://cdn.shahriyar.dev/equalizer.png")

        msg = await ctx.send(embed=embed)

        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        await msg.add_reaction("3️⃣")
        await msg.add_reaction("4️⃣")

        def check(reaction, user):
            return (
                reaction.message.id == msg.id
                and user.id == ctx.author.id
                and reaction.emoji in ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
            )

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=60.0, check=check
                )
            except:
                await msg.delete()
                break

            selected_eq = eqs[reaction.emoji][1]
            await player.set_equalizer(selected_eq)

            embed.description = (
                f"현재의 EQ - **{eqs[reaction.emoji][0]}**\n\n"
                "1. Flat \n2. Boost\n3. Metal\n4. Piano"
            )

            await msg.edit(embed=embed)

    @commands.command(aliases=["lyric"])
    async def lyrics(self, ctx, query: str = None):
        """Search lyrics"""
        if not query:
            player: WebPlayer = self.bot.wavelink.get_player(
                ctx.guild.id, cls=WebPlayer
            )
            if not player.is_playing:
                return await ctx.send(
                    "아무것도 안틀었어요. 노래를 틀거나 곡의 이름을 검색해서 이 명령어를 써주세요."
                )

            title = player.current.title

        else:
            title = query

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://some-random-api.ml/lyrics?title={title}"
            ) as response:
                song_data = await response.json()
                if song_data:
                    lyrics = song_data["lyrics"]

        lines = [line.replace("\n", "") for line in lyrics.split("\n")]
        pages = []

        stack = ""
        for line in lines:
            new_stack = stack + line + "\n"
            if len(new_stack) > 300:
                pages.append(stack)
                stack = ""
            stack += line + "\n"

        if not pages:
            pages.append(stack)

        embed = discord.Embed(title=f"{song_data['author']}/{song_data['title']}")
        embed.description = pages[0]
        try:
            embed.set_thumbnail(url=song_data["thumbnail"]["genius"])
        except:
            pass

        if len(pages) == 1:
            return await ctx.send(embed=embed)

        else:
            current_page = 0
            embed.set_footer(text=f"{current_page + 1}/{len(pages)}")

            book: discord.Message = await ctx.send(embed=embed)
            buttons = ["◀️", "▶️"]

            for emoji in buttons:
                await book.add_reaction(emoji)

            await asyncio.sleep(1)
            while True:
                reaction, reaction_user = await self.bot.wait_for(
                    "reaction_add", timeout=180
                )

                if reaction.emoji == "◀️":
                    current_page -= 1
                    if current_page < 0:
                        current_page = 0
                        continue

                elif reaction.emoji == "▶️":
                    current_page += 1

                try:
                    await book.remove_reaction(reaction.emoji, reaction_user)
                except:
                    pass

                try:
                    content = pages[current_page]
                except:
                    current_page -= 1
                    continue

                embed.description = content
                embed.set_footer(text=f"{current_page + 1}/{len(pages)}")
                await book.edit(embed=embed)


def setup(bot):
    bot.add_cog(Music(bot))