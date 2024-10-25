import discord
from discord.ext import commands
import database
import sqlite3

connection = sqlite3.connect("gdll.db")

class StatsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="stats")
    async def stats(self, ctx):
        
        uid = ctx.author.id

        infos = database.get_competitor_by_id(uid)
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

        competitor1 = database.get_competitor_by_id(user1.id)
        old_rank1 = competitor1[0][2]

        competitor2 = database.get_competitor_by_id(user2.id)
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

        
        database.update_competitor(new_elo1, competitor1, "elo")
        database.update_competitor(new_elo2, competitor2, "elo")
        
        database.update_competitor(competitor1[0][4] + 1, competitor1, "played_games")
        database.update_competitor(competitor1[0][5] + 1, competitor1, "wins")

        database.update_competitor(competitor2[0][4] + 1, competitor2, "played_games")
        database.update_competitor(competitor2[0][6] + 1, competitor2, "losses")


        if new_elo1 > competitor1[0][8]:
            database.update_competitor(new_elo1, competitor1, "best_elo")

        updated_competitor1 = database.get_competitor_by_id(user1.id) 
        updated_competitor2 = database.get_competitor_by_id(user2.id)

        database.update_competitor((updated_competitor1[0][5] / updated_competitor1[0][4]) * 100, competitor1, "winrate")
        database.update_competitor((updated_competitor2[0][5] / updated_competitor2[0][4]) * 100, competitor2, "winrate")     

        newrank_competitor1 = await self.check_rankup(ctx, updated_competitor1, old_rank1)
        newrank_competitor2 = await self.check_rankup(ctx, updated_competitor2, old_rank2)

        database.update_competitor(newrank_competitor1, competitor1, "rank")
        database.update_competitor(newrank_competitor2, competitor2, "rank")
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
    