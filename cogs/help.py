import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def make_embed(self):
        embed = discord.Embed(
            color=discord.Color.orange(),
        )
        embed.add_field(
            name="match",
            value="マッチング募集用メッセージの送信",
            inline=False
        )
        embed.add_field(
            name="role (引数)",
            value="ロール付与用メッセージの送信\n"\
                    "e.g.) `+role hoge`: `hogeRole`を生成",
            inline=False
        )
        embed.set_footer(
            text="不具合等のご報告は monoue（マコト）までお願いします。"
        )
        return embed

    @commands.command()
    async def help(self, ctx):
        embed = self.make_embed()
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
