import discord, json, codecs

from discord.ext import commands
from .ratings import *
from .ratings_chart import *

class RatingsAndRanking(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		f = codecs.open('data.json', 'r', encoding='utf-8')
		self.data = json.loads(f.read())
		f.close()

	async def get_role_ranking(self, rating): # some stupid if else to get role of each rating
		default = ['"SGM"', 'Super Grandmaster', discord.Color.gold()]
		rating_role = {
			1200: ['"N"', 'Newbie', discord.Color.dark_grey()],
			1400: ['"P"', 'Pupil', discord.Color.dark_green()],
			1600: ['"S"', 'Specialist', discord.Color.teal()],
			1900: ['"E"', 'Expert', discord.Color.blue()],
			2100: ['"CM"', 'Candidate Master', discord.Color.purple()],
			2300: ['"M"', 'Master', discord.Color.dark_orange()],
			2400: ['"IM"', 'International Master', discord.Color.orange()],
			2600: ['"GM"', 'Grandmaster', discord.Color.dark_red()],
			3000: ['"IGM"', 'International Grandmaster', discord.Color.red()]
		}
		for rate in rating_role:
			if rating < rate:
				default = rating_role[rate]
				break
		return default

	@commands.command()
	async def profile(self, ctx, user=None):
		qry_user = user
		if user == None:
			qry_user = f"<@!{ctx.author.id}>"
		if qry_user not in self.data['user']:
			await ctx.send(f"**User {qry_user} cannot found in database. Please register rating for this user !**")
			return None
		await RatingChart(10, 5)._draw_chart(qry_user, self.data['user'][qry_user]['history'])
		role_ranking = await self.get_role_ranking(self.data['user'][qry_user]['rating'])
		profile_embed = discord.Embed(description=f"Rating profile of **{role_ranking[0]}** {qry_user} ({role_ranking[1]})", color=role_ranking[2])
		profile_embed.add_field(name="Rating", value="%.2f"%self.data['user'][qry_user]['rating'], inline=True)
		profile_embed.add_field(name="Diff", value=f"{'+' if self.data['user'][qry_user]['diff'] > 0 else ''}%.2f"%self.data['user'][qry_user]['diff'], inline=True)
		profile_embed.add_field(name="Matches", value=self.data['user'][qry_user]['match'], inline=True)
		profile_chart = discord.File(f"./temp/{qry_user[3:-1]}.png", filename="chart.png")
		profile_embed.set_image(url=f"attachment://chart.png")
		await ctx.send(embed=profile_embed, file=profile_chart)

	@commands.command()
	async def rank(self, ctx, page=1):
		rank_embed = discord.Embed(title="Luyencode.net Cốt thủ Ranking")
		field_user, rating_field, diff_field, index_rank = "", "", "", 0
		for k in self.data['user']:
			if int(index_rank / 10 + 1) == page:
				field_user += f'#{index_rank + 1} ' + k + '\n'
				rating_field += "%.2f\n" % self.data['user'][k]['rating']
				diff_field += f"{'+' if self.data['user'][k]['diff'] > 0 else ''}%.2f\n" % self.data['user'][k]['diff']
			index_rank += 1
		rank_embed.add_field(name="Name", value=field_user, inline=True)
		rank_embed.add_field(name="Rating", value=rating_field, inline=True)
		rank_embed.add_field(name="Diff", value=diff_field, inline=True)
		#await ctx.send("debug")
		await ctx.send(embed=rank_embed)

	@commands.command()
	@commands.has_role('Admin')
	async def register(self, ctx, user):
		try:
			self.data['user'][user] = {'rating': 1500, 'diff': 0, 'match': 0, 'history': [1500]}
			await ctx.send(f"**Registered rating for {user}. Use `update` to update the database.**")
		except Exception as e:
			await ctx.send(f"**Can't register ratings for {user}. Something went wrong :(((**")

	@commands.command()
	@commands.has_role('Admin')
	async def update(self, ctx, *args):
		try:
			self.data['user'] = dict(sorted(self.data['user'].items(), key=lambda i: i[1]['rating'], reverse=True))
			with open('data.json', 'w') as out_data_file:
				json.dump(self.data, out_data_file)
			await ctx.send(f"**Database updated successfully ! :white_check_mark:**")
		except:
			await ctx.send(f"**Can't update leaderboard on the database. Something went wrong !**")

	@commands.command()
	@commands.has_role('Admin')
	async def matchresult(self, ctx, user1, user2, res : str):
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
			await ctx.message.delete()
			await ctx.send(f"**After result: {res}. Rating of {user1} is %.2f. Rating of {user2} is %.2f**" % (self.data['user'][user1]['rating'], self.data['user'][user2]['rating']))
			self.data['user'][user1]['history'].append(self.data['user'][user1]['rating'])
			self.data['user'][user2]['history'].append(self.data['user'][user2]['rating'])
		except Exception as e:
			input(e)
			await ctx.send(f"**{e}**")

	@commands.command()
	@commands.has_role('Admin')
	async def remove(self, ctx, *args):
		try:
			for u in args:
				del self.data['user'][u]
			await ctx.send(f"**:white_check_mark: Successfully !**")
		except:
			await ctx.send(f"**Can't remove one of that user. Something went wrong**")

	@commands.command()
	@commands.has_role('Admin')
	async def resetall(ctx, qry=None):
		for u in self.data['user']:
			if qry is None:
				self.data['user'][u]['rating'] = 1500
				self.data['user'][u]['diff'] = 0
				self.data['user'][u]['match'] = 0
			else:
				self.data['user'][u][qry] = 1500 if qry == 'rating' else 0
		await ctx.send('**Reseted all information on rating leaderboard :white_check_mark:**')

def setup(bot):
	bot.add_cog(RatingsAndRanking(bot))