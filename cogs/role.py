import discord
from discord.ext import commands
import asyncio

class Role(commands.Cog):
    REGISTER_EMOJI = '✅'
    REMOVER_EMOJI = '❌'

    def __init__(self, bot):
        self.bot = bot
        self.embed = self.init_embed()

    def init_embed(self) -> discord.Embed():
        embed = discord.Embed()
        return embed

    # def make_text(self, role_mention, author_mention) -> str:
    #     return f"新ロール、 {role_mention} が作成されました。\n"\
    #         f"各自、{self.REGISTER_EMOJI}にて、本ロールのオン・オフが可能です。\n"\
    #         f"{author_mention} このロールが不要になりましたら、{self.REMOVER_EMOJI}でリアクションしてください。\n"\
    #         "サーバーから本ロールが削除されます。"

    def make_text(self, role_mention, author_mention) -> str:
        return f"各自、{self.REGISTER_EMOJI}にて、新ロールのオン・オフが可能です。\n"\
            f"{author_mention} このロールが不要になりましたら、{self.REMOVER_EMOJI}にて、サーバーから削除できます。"
    
    def get_role_index_not_used(self, roles):
        num = 0
        while True:
            found = False
            for role in roles:
                if role.name == f"role{num}":
                    found = True
                    break
            if found == False:
                break
            num += 1
        return num
    
    def make_role_name(self, roles):
        role_index = self.get_role_index_not_used(roles)
        return f"role{role_index}"
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        if payload.emoji.name == self.REGISTER_EMOJI:
            await self.handle_role_toggling_reaction(payload, True)
        else:
            emoji_name = payload.emoji.name
            if emoji_name != self.REGISTER_EMOJI and emoji_name != self.REMOVER_EMOJI:
                return
            guild_id = payload.guild_id
            guild = discord.utils.find(lambda g: g.id == guild_id, self.bot.guilds)
            member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
            if member.bot:
                return
            channel = self.bot.get_channel(payload.channel_id)
            self.embed.description = f"{self.role.mention}が削除されました。"
            self.embed.color = discord.Color.blue()
            await channel.send(embed=self.embed)
            await self.role.delete()


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if not payload.emoji.name == self.REGISTER_EMOJI:
            return
        if payload.user_id == self.bot.user.id:
            return
        await self.handle_role_toggling_reaction(payload, False)
    
    def get_role_corresponding_to_message(guild, message):
            role_name = message.embeds[0].fields[0].value
            role = discord.utils.get(guild.roles, name=role_name)
            return role

    async def handle_role_toggling_reaction(self, payload, adding):
        channel = self.bot.get_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel):
            return
        try:
            reactioned_message = await channel.fetch_message(payload.message_id)
            if reactioned_message.author.id != self.bot.user.id:
                return
            guild = reactioned_message.guild
            member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
            if member.bot:
                return
            role = Role.get_role_corresponding_to_message(guild, reactioned_message)
            if adding:
                await member.add_roles(role)
            else:
                await member.remove_roles(role)
        except Exception as e:
            print(e)
            print(type(e))


    @commands.command()
    async def role(self, ctx):
        await self.bot.wait_until_ready()
        role_name = self.make_role_name(ctx.guild.roles)
        self.role = await ctx.guild.create_role(name=role_name)
        self.embed.description = self.make_text(self.role.mention, ctx.author.mention)
        self.embed.clear_fields()
        self.embed.add_field(name="new_role_name", value=role_name)
        self.embed.color = discord.Color.blue()
        channel = ctx.channel
        msg = await ctx.send(embed=self.embed)
        self.msg_id = msg.id
        await msg.add_reaction(self.REGISTER_EMOJI)
        await msg.add_reaction(self.REMOVER_EMOJI)
        
                    
    @commands.command()
    async def rm(self, ctx, num):
        role_name = f"role{num}"
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role is None:
            self.embed.color = discord.Color.red()
            self.embed.description = f"{ctx.author.mention} `{role_name}`というロールは存在しません。"
            await ctx.send(embed=self.embed)
        else:
            self.embed.color = discord.Color.green()
            self.embed.description = f"{ctx.author.mention}さんが{role.mention}を削除しました。"
            await ctx.send(embed=self.embed)
            await role.delete()


def setup(bot):
    bot.add_cog(Role(bot))
