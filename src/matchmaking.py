import discord
from discord.ext import commands, tasks
import database
import sqlite3

connection = sqlite3.connect("gdll.db")

tiers = {1290084217157324890: "g",
         1290084262401409044: "fg",
         1290084389342154825: "f",
         1290084607223664680: "ef",
         1290084670960042055: "e",
         1290084708830543955: "de",
         1290085955599863828: "d",
         1290085994741370962: "cd",
         1290086261675261962: "c",
         1290086300518711376: "bc",
         1290086346613985310: "b",
         1290086366968807555: "ab",
         1290086384664707112: "a",
         1290086431288594483: "s",
         1290086464771854407: "star",
         1290086492751925258: "superstar"}

class MatchmakingCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.task_counter = 0
        self.tasks = {}

    @commands.command(name="challenge")
    async def matchmake(self, ctx):

        try:
            tier = tiers[ctx.channel.id]
        except KeyError:

            await ctx.channel.send("Please __start__ matchmaking in **tiers** channels !")
            return
        
        nickname = ctx.author.name
        uid = ctx.author.id

        l = database.get_user_elo(uid)

        elo = l[0][0]

        if tier == "fg":
            if not elo > 2000:
                await ctx.channel.send("Your **ELO** is too __low__ to compete in this tier !")
                return
        elif tier == "ef":
            if not elo > 4000:
                await ctx.channel.send("Your **ELO** is too __low__ to compete in this tier !")
                return
        elif tier == "de":
            if not elo > 6000:
                await ctx.channel.send("Your **ELO** is too __low__ to compete in this tier !")
                return
        elif tier == "cd":
            if not elo > 8000:
                await ctx.channel.send("Your **ELO** is too __low__ to compete in this tier !")
                return
        elif tier == "bc":
            if not elo > 10000:
                await ctx.channel.send("Your **ELO** is too __low__ to compete in this tier !")
                return
        elif tier == "ab":
            if not elo > 12000:
                await ctx.channel.send("Your **ELO** is too __low__ to compete in this tier !")
                return
            
        try:
            database.insert_in_matchmaking(uid, nickname, tier, elo)
        except sqlite3.IntegrityError:
            await ctx.channel.send('You are **already** looking for opponents ! Wait until the process __finishes__ or send __**"ll!cancel"**__ to cancel matchmaking')
            connection.close()
            return

        embed = discord.Embed(
            title="Matchmaking",
            description="Looking for opponents right now !",
            color=discord.Color.dark_grey()
        )

        embed.set_author(name=f"Tier {tier}")
        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.set_footer(icon_url=ctx.guild.icon.url, text="Geometry Dash Layout League")

        await ctx.channel.send(embed=embed)

        try:
            t = tasks.loop(seconds=4)(self.loop_through_db)
            self.tasks[ctx.author.id] = t
            t.start(ctx)
        except TypeError:
            pass

    async def loop_through_db(self, ctx):
        
        l = database.search_matchmaking(ctx, tiers)
        print(l)

        if l != []:

            self.tasks[ctx.author.id].stop()
            del self.tasks[ctx.author.id]
           
            embed = discord.Embed(
            title="Matchmaking",
            description=f"Opponent found ! - {l[0][1]}",
            color=discord.Color.dark_grey()
            )

            member = discord.utils.get(ctx.guild.members, id=l[0][0])
            embed.set_author(name=f"Tier {tiers[ctx.channel.id]}")
            embed.set_image(url=member.display_avatar.url)
            embed.set_thumbnail(url=ctx.guild.icon.url)
            embed.set_footer(icon_url=ctx.guild.icon.url, text="Geometry Dash Layout League")
            await ctx.channel.send(f"Opponent found ! {ctx.author.mention} | {member.mention}", embed=embed)
            
            database.delete_from_matchmaking(ctx.author.id)
            database.delete_from_matchmaking(l[0][0])
            connection.close()

            self.tasks[member.id].stop()
            del self.tasks[member.id]

            guild = ctx.guild
            member = ctx.author
            opponent = discord.utils.get(guild.members, id=l[0][0])
            admin_role = guild.get_role(1290029015981359197)
            judge_role = guild.get_role(1290028500794736690)
            category = discord.utils.get(ctx.guild.categories, id=1291435596727975958)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True),
                opponent: discord.PermissionOverwrite(read_messages=True),
                admin_role: discord.PermissionOverwrite(read_messages=True),
                judge_role: discord.PermissionOverwrite(read_messages=True)
            }

            channel = await category.create_text_channel(f'game_{ctx.author.id}', overwrites=overwrites)
            print(channel.id)
            intro_embed = discord.Embed(
                title="Challenge !",
                description=f"{ctx.author.mention}, your opponent : {opponent.mention}, {l[0][2]} ELO",
                color=discord.Color.dark_grey()
            )
            
            file = discord.File("images/embed.png", filename="image.png")

            intro_embed.set_author(name="Send your best layouts !")
            intro_embed.set_thumbnail(url=ctx.guild.icon.url)
            intro_embed.set_image(url="attachment://image.png")
            intro_embed.set_footer(icon_url=ctx.guild.icon.url, text="Geometry Dash Layout League")

            await channel.send(f"{ctx.author.mention} {opponent.mention}, send your applications and wait for the judges to give it notes !", file=file, embed=intro_embed)

        else:
            connection.close()

    @commands.command(name="cancel")
    async def cancel_matchmaking(self, ctx):

        uid = ctx.author.id
        
        l = database.search_in_matchmaking_by_id(uid)
        print(l)

        if l != []:

            try:
                self.tasks[ctx.author.id].stop()
                del self.tasks[ctx.author.id]
            except KeyError:
                print("KeyError ignored in tasks registrations")

            database.delete_from_matchmaking(uid)
            connection.close()

            await ctx.channel.send("Successfully **removed** from __matchmaking__ !")
        
        else:
            await ctx.channel.send("You are not __looking__ for **opponents right now** !")
        