import discord
from discord.ext import commands, tasks
import sqlite3
import database
from datetime import datetime
import io, os

connection = sqlite3.connect("gdll.db")
c = connection.cursor()

database.initialize_tables()

connection.commit()
connection.close()

intents = discord.Intents.all()
intents.guilds = True

class MainCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

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

            database.register_in_database(uid, nickname)
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

    @tasks.loop(hours=24)
    async def show_leaderboard(self):

        guild = self.bot.get_guild(1290009064071237733)
        leaderboard_channel = discord.utils.get(guild.channels, id=1290171958834757776)

        leaderboard_embed = discord.Embed(
            title="GDLL Leaderboard",
            description=f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}",
            color=discord.Color.dark_gray()
        )

        competitors = database.get_best_competitors()

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

                database.retrieve_data_from_file(queries)
                connection.close()

                await ctx.channel.send("**Backup** loaded __successfully__ !")

        except discord.ext.commands.errors.MissingPermissions:
            await ctx.channel.send("You are not **allowed** to use this __command__ !")

        except FileNotFoundError:
            await ctx.channel.send("Failed to **retrieve** data from __file__ ! (the file was not found)")