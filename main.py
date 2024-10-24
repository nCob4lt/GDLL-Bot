import discord
import sqlite3
from discord.ext import commands, tasks
from datetime import datetime
import io
import os

import discord.ext.commands
import clienttoken
import discord.ext

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

connection = sqlite3.connect("gdll.db")
c = connection.cursor()

c.execute(''' CREATE TABLE IF NOT EXISTS competitors (id INTEGER PRIMARY KEY, nickname TEXT, rank TEXT, elo INTEGER, played_games INTEGER, wins INTEGER, losses INTEGER, winrate REAL, best_elo INTEGER);''')
c.execute(''' CREATE TABLE IF NOT EXISTS matchmaking (id INTEGER PRIMARY KEY, nickname TEXT, tier TEXT, elo INTEGER)''')

connection.commit()
connection.close()

intents = discord.Intents.all()
intents.guilds = True

class MainCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.task_counter = 0
        self.tasks = {}

    @commands.Cog.listener(name="on_ready")
    async def starting(self):
        print("[Debug] Ready to use")
        if not self.show_leaderboard.is_running():
            self.show_leaderboard.start()
            print("[Debug] Leaderboard bg task running")
        if not self.create_backup.is_running():
            self.create_backup.start()
            print("[Debug] Backup saving bg task running")
            

    @commands.command(name="register")
    async def register(self, ctx):

        try:

            nickname = ctx.author.name
            uid = ctx.author.id

            connection = sqlite3.connect("gdll.db")
            c = connection.cursor()
            c.execute(''' INSERT INTO competitors (id, nickname, rank, elo, played_games, wins, losses, winrate, best_elo) VALUES (?,?,?,?,?,?,?,?,?);''', (uid, nickname, "Iron 1", 1000, 0, 0, 0, 0, 1000))
            connection.commit()
            connection.close()

            embed = discord.Embed(
                title="Registration",
                description="Successfully registered in the database !",
                color=discord.Color.dark_grey()
            )

            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            embed.set_thumbnail(url=ctx.guild.icon.url)
            embed.set_image(url=ctx.author.display_avatar.url)
            embed.set_footer(icon_url=ctx.guild.icon.url, text="Geometry Dash Layout League")

            role = discord.utils.get(ctx.guild.roles, id=1290350180528554094)
            await ctx.author.add_roles(role)

            return await ctx.channel.send(embed=embed)
        
        except sqlite3.IntegrityError:
            connection.close()
            return await ctx.channel.send("**You** are already registered in the __database__ ! ")            
    
    @commands.command(name="challenge")
    async def matchmake(self, ctx):

        try:
            tier = tiers[ctx.channel.id]
        except KeyError:

            await ctx.channel.send("Please __start__ matchmaking in **tiers** channels !")
            return
        
        nickname = ctx.author.name
        uid = ctx.author.id

        connection = sqlite3.connect("gdll.db")
        c = connection.cursor()
        c.execute(''' SELECT elo FROM competitors WHERE id = ?;''', (uid,))
        l = c.fetchall()
        print(l)

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
            c.execute('''INSERT INTO matchmaking (id, nickname, tier, elo) VALUES (?,?,?,?);''', (uid, nickname, tier, elo))
            connection.commit()
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

        print(self.tasks)

    async def loop_through_db(self, ctx):
        
        connection = sqlite3.connect("gdll.db")
        c = connection.cursor()
        c.execute(''' SELECT id, nickname, elo FROM matchmaking WHERE id != ? and tier = ?;''', (ctx.author.id, tiers[ctx.channel.id]))
        l = c.fetchall()
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
            
            c.execute('''DELETE FROM matchmaking WHERE id = ?;''', (ctx.author.id,))
            c.execute('''DELETE FROM matchmaking WHERE id = ?;''', (l[0][0],))
            connection.commit()
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
        
        connection = sqlite3.connect("gdll.db")
        c = connection.cursor()
        c.execute(''' SELECT * FROM matchmaking WHERE id = ?;''', (uid,))
        l = c.fetchall()
        print(l)

        if l != []:

            try:
                self.tasks[ctx.author.id].stop()
                del self.tasks[ctx.author.id]
            except KeyError:
                print("KeyError ignored in tasks registrations")

            c.execute('''DELETE FROM matchmaking WHERE id = ?;''', (ctx.author.id,))
            connection.commit()
            connection.close()

            await ctx.channel.send("Successfully **removed** from __matchmaking__ !")
        
        else:
            await ctx.channel.send("You are not __looking__ for **opponents right now** !")

    async def check_rankup(self, ctx, competitor, oldrank):

        new_rank = None
        member = discord.utils.get(ctx.guild.members, id=competitor[0][0])

        if 0 <= competitor[0][3] <= 1999:
            new_rank = "Iron 1"
            role = discord.utils.get(ctx.guild.roles, id=1290350180528554094)
            
        elif 2000 <= competitor[0][3] <= 2999:
            new_rank = "Iron 2"
            role = discord.utils.get(ctx.guild.roles, id=1290350180528554094)
        
        elif 3000 <= competitor[0][3] <= 3999:
            new_rank = "Gold 1"
            role = discord.utils.get(ctx.guild.roles, id=1290350291606044734)
            
        elif 4000 <= competitor[0][3] <= 4999:
            new_rank = "Gold 2"
            role = discord.utils.get(ctx.guild.roles, id=1290350291606044734)
            
        elif 5000 <= competitor[0][3] <= 5999:
            new_rank = "Platinum 1"
            role = discord.utils.get(ctx.guild.roles, id=1290350375932792852)
            
        elif 6000 <= competitor[0][3] <= 6999:
            new_rank = "Platinum 2"
            role = discord.utils.get(ctx.guild.roles, id=1290350375932792852)
            
        elif 7000 <= competitor[0][3] <= 7999:
            new_rank = "Sapphire 1"
            role = discord.utils.get(ctx.guild.roles, id=1290350463694143508)
            
        elif 8000 <= competitor[0][3] <= 8999:
            new_rank = "Sapphire 2"
            role = discord.utils.get(ctx.guild.roles, id=1290350463694143508)
            
        elif 9000 <= competitor[0][3] <= 9999:
            new_rank = "Diamond 1"
            role = discord.utils.get(ctx.guild.roles, id=1290350532103241829)
            
        elif 10000 <= competitor[0][3] <= 10999:
            new_rank = "Diamond 2"
            role = discord.utils.get(ctx.guild.roles, id=1290350532103241829)
            
        elif 11000 <= competitor[0][3] <= 11999:
            new_rank = "Veteran 1"
            role = discord.utils.get(ctx.guild.roles, id=1290350610151112734)
            
        elif 12000 <= competitor[0][3] <= 12999:
            new_rank = "Veteran 2"
            role = discord.utils.get(ctx.guild.roles, id=1290350610151112734)
            
        elif 13000 <= competitor[0][3] <= 13999:
            new_rank = "Guardian 1"
            role = discord.utils.get(ctx.guild.roles, id=1290350689360547983)
            
        elif 14000 <= competitor[0][3] <= 14999:
            new_rank = "Guardian 2"
            role = discord.utils.get(ctx.guild.roles, id=1290350689360547983)
            
        elif 15000 <= competitor[0][3] <= 15999:
            new_rank = "Elite 1"
            role = discord.utils.get(ctx.guild.roles, id=1290350743181594714)
            
        elif 16000 <= competitor[0][3] <= 16999:
            new_rank = "Elite 2"
            role = discord.utils.get(ctx.guild.roles, id=1290350743181594714)
            
        elif 17000 <= competitor[0][3] <= 17999:
            new_rank = "Grandmaster 1"
            role = discord.utils.get(ctx.guild.roles, id=1290350805576187945)
            
        elif 18000 <= competitor[0][3] <= 18999:
            new_rank = "Grandmaster 2"
            role = discord.utils.get(ctx.guild.roles, id=1290350805576187945)
            
        elif 19000 <= competitor[0][3]:
            new_rank = "Chosen ones"
            role = discord.utils.get(ctx.guild.roles, id=1290350805576187945)

        if oldrank != new_rank:

            user = discord.utils.get(ctx.guild.members, id=competitor[0][0])
            channel = discord.utils.get(ctx.guild.channels, id=1297989735020494921)

            changerank_embed = discord.Embed(
                title=f"Rank update : {user.name} !",
                description="Geometry Dash Layout League",
                color=discord.Color.dark_grey()
            )

            changerank_embed.add_field(name="New Rank :", value=f"{oldrank} -> {new_rank}")
            changerank_embed.set_thumbnail(url=ctx.guild.icon.url)
            changerank_embed.set_footer(icon_url=ctx.guild.icon.url, text="Geometry Dash Layout League")

            rank_roles_ids = [1290350180528554094,
                              1290350291606044734,
                              1290350375932792852,
                              1290350463694143508,
                              1290350532103241829,
                              1290350610151112734,
                              1290350689360547983,
                              1290350743181594714,
                              1290350805576187945
                              ]
            
            for r in member.roles:
                for k in range(len(rank_roles_ids)):
                    if r.id == rank_roles_ids[k]:
                        await member.remove_roles(r)

            await member.add_roles(role)
            await channel.send(f"{member.mention}", embed=changerank_embed)
        

        return new_rank

    @commands.command(name="determine")
    async def determine(self, ctx, user1: discord.Member, link1: str, pl: float, se: float, ex: float, sy: float, cr: float, user2: discord.Member, link2: str, pl2: float, se2: float, ex2: float, sy2: float, cr2: float):

        guild = ctx.guild
        judge_role = discord.utils.get(guild.roles, id=1290028500794736690)
        if judge_role not in ctx.author.roles:

            await ctx.channel.send("You __cannot__ use that **command** !")
            return

        l1 = [pl, se, ex, sy, cr]
        l2 = [pl2, se2, ex2, sy2, cr2]

        for criteria in l1:
            if not 0 <= criteria <= 5:
                await ctx.channel.send("Please **enter** notes between __0 and 5__ (bounds included)")
                return
            
        for criteria2 in l2:
            if not 0 <= criteria2 <= 5:
                await ctx.channel.send("Please **enter** notes between __0 and 5__ (bounds included)")
                return

        fnote1 = pl + se + ex + sy + cr
        fnote2 = pl2 + se2 + ex2 + sy2 + cr2
        win_elo = 250
        lose_elo = 300

        connection = sqlite3.connect("gdll.db")
        c = connection.cursor()
        print(user1.id)
        c.execute(''' SELECT * FROM competitors WHERE id = ?;''', (user1.id,))
        competitor1 = c.fetchall()
        old_rank1 = competitor1[0][2]

        c.execute(''' SELECT * FROM competitors WHERE id = ?;''', (user2.id,))
        competitor2 = c.fetchall()
        old_rank2 = competitor2[0][2]

        if competitor1[0][3] >= competitor2[0][3]:
            win_elo *= (competitor1[0][3] / competitor2[0][3]) * 0.75
            lose_elo *= (competitor1[0][3] / competitor2[0][3]) * 0.9
        else:
            win_elo *= (competitor2[0][3] / competitor1[0][3]) * 0.75
            lose_elo *= (competitor2[0][3] / competitor1[0][3]) * 0.9

        # win_elo *= (fnote1 / fnote2) * 0.75
        lose_elo *= (fnote2 / fnote1)
        lose_elo *= 0.95
        
        old_elo1 = competitor1[0][3]
        old_elo2 = competitor2[0][3]
        new_elo1 = competitor1[0][3] + round(win_elo)
        if not (competitor2[0][3] - round(lose_elo)) < 1000:
            new_elo2 = competitor2[0][3] - round(lose_elo)
        else:
            lose_elo = competitor2[0][3] - 1000
            new_elo2 = competitor2[0][3] - lose_elo

        c.execute('''UPDATE competitors SET elo = ? WHERE id = ?;''', (new_elo1, competitor1[0][0]))
        c.execute('''UPDATE competitors SET elo = ? WHERE id = ?;''', (new_elo2, competitor2[0][0]))
        
        c.execute('''UPDATE competitors SET played_games = ? WHERE id = ?;''', (competitor1[0][4] + 1, competitor1[0][0]))
        c.execute('''UPDATE competitors SET wins = ? WHERE id = ?;''', (competitor1[0][5] + 1, competitor1[0][0]))

        c.execute('''UPDATE competitors SET played_games = ? WHERE id = ?;''', (competitor2[0][4] + 1, competitor2[0][0]))
        c.execute('''UPDATE competitors SET losses = ? WHERE id = ?;''', (competitor2[0][6] + 1, competitor2[0][0]))

        if new_elo1 > competitor1[0][8]:
            c.execute('''UPDATE competitors SET best_elo = ? WHERE id = ?;''', (new_elo1, competitor1[0][0]))
        if new_elo2 > competitor2[0][8]:
            c.execute('''UPDATE competitors SET best_elo = ? WHERE id = ?;''', (new_elo1, competitor2[0][0]))
        connection.commit()

        c.execute('''SELECT * FROM competitors WHERE id = ?''', (user1.id,))
        updated_competitor1 = c.fetchall()
        c.execute('''SELECT * FROM competitors WHERE id = ?''', (user2.id,))
        updated_competitor2 = c.fetchall()

        c.execute('''UPDATE competitors SET winrate = ? WHERE id = ?;''', ((updated_competitor1[0][5] / updated_competitor1[0][4]) * 100, competitor1[0][0]))
        c.execute('''UPDATE competitors SET winrate = ? WHERE id = ?;''', ((updated_competitor2[0][5] / updated_competitor2[0][4]) * 100, competitor2[0][0]))      

        newrank_competitor1 = await self.check_rankup(ctx, updated_competitor1, old_rank1)
        newrank_competitor2 = await self.check_rankup(ctx, updated_competitor2, old_rank2)
        c.execute('''UPDATE competitors SET rank = ? WHERE id = ?;''', (newrank_competitor1, competitor1[0][0]))
        c.execute('''UPDATE competitors SET rank = ? WHERE id = ?;''', (newrank_competitor2, competitor2[0][0]))
        connection.commit()
        connection.close()

        await ctx.channel.send("ELO __determined__ and stats **updated** !")

        results_embed = discord.Embed(
            title="| - Results",
            description=f"Challenge : {competitor1[0][1]} VS {competitor2[0][1]}",
            color=discord.Color.blue()
        )

        results_embed.set_thumbnail(url=ctx.guild.icon.url)
        results_embed.set_footer(icon_url=ctx.guild.icon.url, text="Geometry Dash Layout League")

        results_embed.add_field(name=f"{competitor1[0][1]}", value=f"Final note : {fnote1} / 25", inline=True)
        results_embed.add_field(name=f"{competitor2[0][1]}", value=f"Final note : {fnote2} / 25", inline=True)
        results_embed.add_field(name=" ", value=" ", inline=True)

        results_embed.add_field(name=f"ELO", value=f"{old_elo1} -> {new_elo1} (+ {round(win_elo)})", inline=True)
        results_embed.add_field(name=f"ELO", value=f"{old_elo2} -> {new_elo2} (- {round(lose_elo)})", inline=True)
        results_embed.add_field(name=" ", value=" ", inline=True)

        g = ctx.guild

        results_channel = discord.utils.get(g.channels, id=1290171449595662337)
        await results_channel.send(embed=results_embed)
        await results_channel.send(f"{user1.mention} ({competitor1[0][1]}) : {link1}")
        await results_channel.send(f"{user2.mention} ({competitor2[0][1]}) : {link2}")

        channelid = ctx.channel.id
        channel = discord.utils.get(guild.channels, id=channelid)
        await channel.delete()

    @commands.command(name="stats")
    async def stats(self, ctx):
        
        connection = sqlite3.connect("gdll.db")
        c = connection.cursor()
        uid = ctx.author.id

        c.execute(''' SELECT * FROM competitors WHERE id = ?;''', (uid,))
        infos = c.fetchall()
        connection.close()


        stats_embed = discord.Embed(
            title=f"- Geometry Dash Layout League -",
            description=f"| - {ctx.author.name} *stats*",
            color=discord.Color.dark_gray()
        )

        stats_embed.add_field(name="User ID", value=f"{infos[0][0]}", inline=True)
        stats_embed.add_field(name="Nickname", value=f"{infos[0][1]}", inline=True)
        stats_embed.add_field(name="Rank", value=f"{infos[0][2]}", inline=True)

        stats_embed.add_field(name="ELO", value=f"{infos[0][3]}", inline=True)
        stats_embed.add_field(name="Played games", value=f"{infos[0][4]}", inline=True)
        stats_embed.add_field(name="Wins", value=f"{infos[0][5]}", inline=True)

        stats_embed.add_field(name="Losses", value=f"{infos[0][6]}", inline=True)
        stats_embed.add_field(name="Winrate", value=f"{round(infos[0][7], 2)} %", inline=True)
        stats_embed.add_field(name="", value="", inline=True)

        stats_embed.set_image(url=ctx.author.display_avatar.url)
        stats_embed.set_footer(icon_url=ctx.guild.icon.url, text="Geometry Dash Layout League")

        await ctx.channel.send(embed=stats_embed)

    @tasks.loop(hours=24)
    async def show_leaderboard(self):

        guild = bot.get_guild(1290009064071237733)
        leaderboard_channel = discord.utils.get(guild.channels, id=1290171958834757776)

        leaderboard_embed = discord.Embed(
            title="GDLL Leaderboard",
            description=f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}",
            color=discord.Color.dark_gray()
        )

        connection = sqlite3.connect("gdll.db")
        c = connection.cursor()
        c.execute('''SELECT * FROM competitors ORDER BY elo DESC LIMIT 10;''')
        competitors = c.fetchall()

        for i in range(len(competitors)):
            leaderboard_embed.add_field(name=f"N°{i+1} | {competitors[i][1]}", value=f"Current ELO : **{competitors[i][3]}** | Best ELO : **{competitors[i][8]}** | Wins : **{competitors[i][5]}** | Rank : **{competitors[i][2]}**", inline=False)

        connection.close()
        leaderboard_embed.set_footer(icon_url=guild.icon.url, text="Geometry Dash Layout League")
        leaderboard_embed.set_thumbnail(url=guild.icon.url)
        await leaderboard_channel.send(embed=leaderboard_embed)

    @tasks.loop(hours=1)
    async def create_backup(self):
        connection = sqlite3.connect("gdll.db")
        with io.open(f"saves/gdllbackup{datetime.today().strftime('%Y-%m-%d%H%M%S')}.sql", "w") as p:
            for line in connection.iterdump():
                p.write('%s\n' % line)
        connection.close()

    @commands.command(name="loadsave")
    @commands.has_guild_permissions(administrator=True)
    async def load_save(self, ctx, filename: str):

        try:
            with open(f"saves/{filename}", "r") as f:
                queries = f.readlines()

                try:
                    os.remove("gdll.db")
                except FileNotFoundError:
                    print("[Debug] Database already deleted")

                connection = sqlite3.connect("gdll.db")
                c = connection.cursor()
                for query in queries:

                    c.execute(query)
                connection.close()

                await ctx.channel.send("**Backup** loaded __successfully__ !")

        except discord.ext.commands.errors.MissingPermissions:
            await ctx.channel.send("You are not **allowed** to use this __command__ !")

        except FileNotFoundError:
            await ctx.channel.send("Failed to **retrieve** data from __file__ ! (the file was not found)")


class GDLL(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="ll!", intents=discord.Intents.all())

    async def setup_hook(self) -> None:
        await self.add_cog(MainCog(self))
        await self.tree.sync()


bot = GDLL()
bot.run(clienttoken.clientToken.token)