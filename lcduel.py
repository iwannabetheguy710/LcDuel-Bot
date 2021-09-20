import discord, json, codecs, requests, asyncio, os

from dotenv import load_dotenv
from ratings import *
from discord.ext import commands

class LcDuel(commands.Bot):
	def __init__(self, command_prefix, self_bot=False):
		super().__init__(command_prefix=command_prefix, self_bot=self_bot)
		f = codecs.open('data.json', 'r', encoding='utf-8')
		self.data = json.loads(f.read())
		f.close()
		self.init_command()

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

	# on_ready function will auto called when the bot start
	async def on_ready(self):
		await self.change_presence(activity=discord.Game(name="Ranking of Duelist"))
		print("The bot is start ... Now !")

	# on_message function will auto called when user send message
	async def on_message(self, message):
		await self.process_commands(message)

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
			role_ranking = self.get_role_ranking(self.data['user'][qry_user]['rating'])
			profile_embed = discord.Embed(description=f"Rating profile of **{role_ranking[0]}** {qry_user} ({role_ranking[1]})", color=role_ranking[2])
			profile_embed.add_field(name="Rating", value="%.2f"%self.data['user'][qry_user]['rating'], inline=True)
			profile_embed.add_field(name="Diff", value=f"{'+' if self.data['user'][qry_user]['diff'] > 0 else ''}%.2f"%self.data['user'][qry_user]['diff'], inline=True)
			profile_embed.add_field(name="Matches", value=self.data['user'][qry_user]['match'], inline=True)
			await ctx.send(embed=profile_embed)

		@self.command(name="rank") # aliases command d.rank function after this line is the function run when this command executed
		async def _rank(ctx):
			rank_embed = discord.Embed(title="Luyencode.net Cốt thủ Ranking")
			field_user, rating_field, diff_field = "", "", ""
			for k in self.data['user']:
				field_user += k + '\n'
				rating_field += "%.2f\n" % self.data['user'][k]['rating']
				diff_field += f"{'+' if self.data['user'][k]['diff'] > 0 else ''}%.2f\n" % self.data['user'][k]['diff']
			rank_embed.add_field(name="Name", value=field_user, inline=True)
			rank_embed.add_field(name="Rating", value=rating_field, inline=True)
			rank_embed.add_field(name="Diff", value=diff_field, inline=True)
			await ctx.send(embed=rank_embed)

		@self.command(name="register", pass_context=True) # aliases command d.register function after this line is the function run when this command executed
		async def _register(ctx, user):
			try:
				self.data['user'][user] = {'rating': 1500, 'diff': 0, 'match': 0}
				await ctx.send(f"**Registered rating for {user}. Use `update` to update the database.**")
			except Exception as e:
				input(e)
				await ctx.send(f"**Can't register ratings for {user}. Something went wrong :(((**")

		@self.command(name="update", pass_context=True) # aliases command d.update function after this line is the function run when this command executed
		async def _update(ctx, *args):
			try:
				self.data['user'] = dict(sorted(self.data['user'].items(), key=lambda i: i[1]['rating'], reverse=True))
				with open('data.json', 'w') as out_data_file:
					json.dump(self.data, out_data_file)
				await ctx.send(f"**Database updated successfully ! :white_check_mark:**")
			except:
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
				await ctx.message.delete()
				await ctx.send(f"**After result: {res}. Rating of {user1} is %.2f. Rating of {user2} is %.2f**" % (self.data['user'][user1]['rating'], self.data['user'][user2]['rating']))
			except Exception as e:
				input(e)
				await ctx.send(f"**{e}**")

		@self.command(name="remove") # aliases command d.remove function after this line is the function run when this command executed
		@commands.has_role("Admin") # restricted for @Admin role only to executed this command
		async def _remove(ctx, *args):
			try:
				for u in args:
					del self.data['user'][u]
				await ctx.send(f"**:white_check_mark: Successfully !**")
			except:
				await ctx.send(f"**Can't remove one of that user. Something went wrong**")

		@self.command(name="send") # aliases command d.send function after this line is the function run when this command executed
		@commands.has_role("Admin") # restricted for @Admin role only to executed this command
		async def _send(ctx, user: commands.Greedy[discord.User], msg):
			try:
				for u in user:
					await u.send(msg)
				await ctx.send("**:white_check_mark: Success !**")
			except:
				await ctx.send("Failed !")

		# start match utility
		@self.command(name="startmatch")
		@commands.has_role("Admin")
		async def _startmatch(ctx, user: commands.Greedy[discord.User], msg, t: int):
			try:
				mention = str()
				hour, minute, second = str(t//3600).zfill(2), str((t%3600)//60).zfill(2), str((t%3600)%60).zfill(2)
				# better embed when start match
				embed_startmatch = discord.Embed(title="Trận đấu bắt đầu !", description=f"Thời gian làm bài là {hour}:{minute}:{second}.\nNếu như đã làm xong vui lòng gửi bài của mình cho<@!740475107947839508> !", color=discord.Color.green())
				for u in user:
					mention += f"{u.mention}\n"
					await u.send(embed=discord.Embed(title="Duelist Tournament", description=msg, color=discord.Color.green()))
				embed_startmatch.add_field(name="Thí sinh", value=mention)
				await ctx.message.delete()
				msg = await ctx.send(embed=embed_startmatch)
				while bool(t):
					if (abs(t - 5) % 5 == 0):
						hour, minute, second = str(t//3600).zfill(2), str((t%3600)//60).zfill(2), str((t%3600)%60).zfill(2)
						new_embed = discord.Embed(title="Trận đấu bắt đầu !", description=f"Thời gian làm bài là {hour}:{minute}:{second}.\nNếu như đã làm xong vui lòng gửi bài của mình cho<@!740475107947839508> !", color=discord.Color.green())
						new_embed.add_field(name="Thí sinh", value=mention)
						await msg.edit(embed=new_embed)
					t -= 1
					await asyncio.sleep(1)
				await msg.delete()
				for u in user:
					await u.send(embed=discord.Embed(title="Duelist Tournament", description="Hiện tại thời gian làm bài đã hết vui lòng bạn gửi bài làm của mình dưới dạng file nén `DUEL_<tên thí sinh>.zip` cho <@!740475107947839508> để tiến hành nộp bài !", color=discord.Color.red()))
				await ctx.send(mention.replace('\n', ' '))
				await ctx.send(embed=discord.Embed(title="Trận đấu kết thúc", description="Hiện tại thời gian làm bài đã hết vui lòng bạn gửi bài làm của mình dưới dạng file nén `DUEL_<tên thí sinh>.zip` cho <@!740475107947839508> để tiến hành nộp bài !", color=discord.Color.red()))
			except:
				await ctx.send("**Can't start match ! Something went wrong !**")

		async def _update_clock(ctx, message, t):
			while bool(t):
				hour, minute, second = str(t//3600).zfill(2), str((t%3600)//60).zfill(2), str((t%3600)%60).zfill(2)
				await message.edit(embed=discord.Embed(title="Trận đấu bắt đầu !", description=f"Thời gian làm bài là {hour}:{minute}:{second}.\nNếu như đã làm xong vui lòng gửi bài của mình cho<@!740475107947839508> !", color=discord.Color.green()))
				t -= 1
				await asyncio.sleep(1)

		######################################################################

		@self.command(name="resetall")
		@commands.has_role('Admin')
		async def _resetall(ctx):
			for u in self.data['user']:
				self.data['user'][u]['rating'] = 1500
				self.data['user'][u]['diff'] = 0
				self.data['user'][u]['match'] = 0
			await ctx.send('**Reseted all information on rating leaderboard :white_check_mark:**')

		@self.command(name="submit")
		@commands.has_any_role('Admin', 'Duelist Contestant')
		async def _submit(ctx, problem):
			att_url = ctx.message.attachments[0].url
			file_req = requests.get(att_url)
			f = codecs.open('content.txt', 'w', encoding='utf-8')
			f.write(file_req.content.decode('utf-8'))
			f.close()
			await ctx.message.delete()
			await ctx.send(f"**Success ! :white_check_mark:**")

		@self.command(name="senword")
		async def _senword(ctx, word):
			self.sensitive_word[word] = 1
			with open('sensitive_word.json', 'w') as e:
				json.dump(self.sensitive_word, e)
			await ctx.message.delete()
			await ctx.send("**Success ! :white_check_mark:**")
		@self.command(name="delsenword")
		@commands.has_role("Admin")
		async def _delsenword(ctx, word):
			await ctx.message.delete()
			try:
				self.sensitive_word.pop(word)
				with open('sensitive_word.json', 'w') as e:
					json.dump(self.sensitive_word, e)
				await ctx.send("**Success ! :white_check_mark:**")
			except:
				await ctx.send(f"**\"{word}\" not found in sensitive word database !**")

load_dotenv('.env')

TOKEN = os.environ.get('BOT_TOKEN')

bot = LcDuel(command_prefix='d.')
bot.run(TOKEN)