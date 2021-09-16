import discord, json, codecs

from ratings import *
from discord.ext import commands

class LcDuel(commands.Bot):
	def __init__(self, command_prefix, self_bot=False):
		super().__init__(command_prefix=command_prefix, self_bot=self_bot)
		f = codecs.open('data.json', 'r', encoding='utf-8')
		self.data = json.loads(f.read())
		f.close()
	# on_ready function will auto called when the bot start
	async def on_ready(self):
		print("Bot started !")

	# a init command function all command of this bot will be declared here
	def init_command(self):
		@self.command(name="profile", pass_context=True) # aliases command d.profile function after this line is the function run when this command executed
		async def _profile(ctx, user=None):
			qry_user = user
			if user == None:
				qry_user = f"<@!{ctx.author.id}>"
			if qry_user not in self.data['user']:
				await ctx.send(f"**User {qry_user} cannot found in database. Please register rating for this user !**")
				return None
			profile_embed = discord.Embed(description=f"Rating profile of {qry_user}")
			profile_embed.add_field(name="Rating", value="%.2f"%self.data['user'][qry_user]['rating'], inline=True)
			profile_embed.add_field(name="Diff", value="%.2f"%self.data['user'][qry_user]['diff'], inline=True)
			profile_embed.add_field(name="Matches", value=self.data['user'][qry_user]['match'], inline=True)
			await ctx.send(embed=profile_embed)

		@self.command(name="rank") # aliases command d.profile function after this line is the function run when this command executed
		async def _rank(ctx):
			rank_embed = discord.Embed(title="Cốt thủ Ranking")
			field_user, rating_field, diff_field = "", "", ""
			for k in self.data['user']:
				field_user += k + '\n'
				rating_field += "%.2f\n" % self.data['user'][k]['rating']
				diff_field += "%.2f\n" % self.data['user'][k]['diff']
			rank_embed.add_field(name="Name", value=field_user, inline=True)
			rank_embed.add_field(name="Rating", value=rating_field, inline=True)
			rank_embed.add_field(name="Diff", value=diff_field, inline=True)
			await ctx.send(embed=rank_embed)

		@self.command(name="register", pass_context=True) # aliases command d.profile function after this line is the function run when this command executed
		async def _register(ctx, user):
			try:
				self.data['user'][user] = {'rating': 1500, 'diff': 0, 'match': 0}
				await ctx.send(f"**Registered rating for {user}. Use `update` to update the database.**")
			except Exception as e:
				input(e)
				await ctx.send(f"**Can't register ratings for {user}. Something went wrong :(((**")

		@self.command(name="update", pass_context=True) # aliases command d.profile function after this line is the function run when this command executed
		@commands.has_role("Admin") # restricted for @Admin role only to executed this command
		async def _update(ctx, *args):
			try:
				self.data['user'] = dict(sorted(self.data['user'].items(), key=lambda i: i[1]['rating'], reverse=True))
				with open('data.json', 'w') as out_data_file:
					json.dump(self.data, out_data_file)
				await ctx.send(f"**Database updated successfully ! :white_check_mark:**")
			except Exception as e:
				raise e
				await ctx.send(f"**Can't update leaderboard on the database. Something went wrong !**")

		@self.command(name="matchresult", pass_context=True) # aliases command d.profile function after this line is the function run when this command executed
		@commands.has_role("Admin") # restricted for @Admin role only to executed this command
		async def _matchresult(ctx, user1, user2, res : str):
			try:
				Ra, Rb = self.data['user'][user1]['rating'], self.data['user'][user2]['rating']
				Ma, Mb = self.data['user'][user1]['match'], self.data['user'][user2]['match']
				rA, rB = map(float, res.split('-'))
				diff = ELO.change_rating(Ra, Rb, Ma, Mb, rA, rB)
				self.data['user'][user1]['diff'] += diff[0]
				self.data['user'][user2]['diff'] += diff[1]
				self.data['user'][user1]['rating'] += diff[0]
				self.data['user'][user2]['rating'] += diff[1]
				self.data['user'][user1]['match'] += 1
				self.data['user'][user2]['match'] += 1
				await ctx.send(f"**After result: {res}. Rating of {user1} is %.2f. Rating of {user2} is %.2f**" % (self.data['user'][user1]['rating'], self.data['user'][user2]['rating']))
			except Exception as e:
				input(e)
				await ctx.send(f"**{e}**")

		@self.command(name="remove") # aliases command d.profile function after this line is the function run when this command executed
		@commands.has_role("Admin") # restricted for @Admin role only to executed this command
		async def _remove(ctx, *args):
			try:
				for u in args:
					del self.data['user'][u]
				await ctx.send(f"**:white_check_mark: Successfully !**")
			except:
				await ctx.send(f"**Can't remove one of that user. Something went wrong**")

		@self.command(name="send") # aliases command d.profile function after this line is the function run when this command executed
		@commands.has_role("Admin") # restricted for @Admin role only to executed this command
		async def _send(ctx, user: commands.Greedy[discord.User], msg):
			try:
				for u in user:
					await u.send(msg)
				await ctx.send("**:white_check_mark: Success !**")
			except:
				await ctx.send("Failed !")

		@self.command(name="eval")
		async def _eval(ctx, *args):
			expression = ''.join(args)
			await ctx.send(eval(expression))

bot = LcDuel(command_prefix='d.')
bot.init_command()
bot.run('<token>')