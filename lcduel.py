import discord, json, codecs, requests, asyncio, os, subprocess

from dotenv import load_dotenv
from ratings import *
from judge.runner import Runner, LANG_INFO
from ratings_chart import *
from discord.ext import commands

class LcDuel(commands.Bot):
	def __init__(self, command_prefix, self_bot=False):
		f = codecs.open('data.json', 'r', encoding='utf-8')
		self.data = json.loads(f.read())
		f.close()

		super().__init__(command_prefix=command_prefix, self_bot=self_bot)
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
		async def profile(ctx, user=None):
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

		@self.command(name="rank") # aliases command d.rank function after this line is the function run when this command executed
		async def rank(ctx):
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
		async def register(ctx, user):
			try:
				self.data['user'][user] = {'rating': 1500, 'diff': 0, 'match': 0, 'history': [1500]}
				await ctx.send(f"**Registered rating for {user}. Use `update` to update the database.**")
			except Exception as e:
				input(e)
				await ctx.send(f"**Can't register ratings for {user}. Something went wrong :(((**")

		@self.command(name="update", pass_context=True) # aliases command d.update function after this line is the function run when this command executed
		async def update(ctx, *args):
			try:
				self.data['user'] = dict(sorted(self.data['user'].items(), key=lambda i: i[1]['rating'], reverse=True))
				with open('data.json', 'w') as out_data_file:
					json.dump(self.data, out_data_file)
				await ctx.send(f"**Database updated successfully ! :white_check_mark:**")
			except:
				await ctx.send(f"**Can't update leaderboard on the database. Something went wrong !**")

		@self.command(name="matchresult", pass_context=True) # aliases command d.profile function after this line is the function run when this command executed
		@commands.has_role("Admin") # restricted for @Admin role only to executed this command
		async def matchresult(ctx, user1, user2, res : str):
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

		@self.command(name="remove") # aliases command d.remove function after this line is the function run when this command executed
		@commands.has_role("Admin") # restricted for @Admin role only to executed this command
		async def remove(ctx, *args):
			try:
				for u in args:
					del self.data['user'][u]
				await ctx.send(f"**:white_check_mark: Successfully !**")
			except:
				await ctx.send(f"**Can't remove one of that user. Something went wrong**")

		@self.command(name="send") # aliases command d.send function after this line is the function run when this command executed
		@commands.has_role("Admin") # restricted for @Admin role only to executed this command
		async def send(ctx, user: commands.Greedy[discord.User], msg):
			try:
				for u in user:
					await u.send(msg)
				await ctx.send("**:white_check_mark: Success !**")
			except:
				await ctx.send("Failed !")

		# start match utility
		@self.command(name="startmatch")
		@commands.has_role("Admin")
		async def startmatch(ctx, user: commands.Greedy[discord.User], msg, t: int):
			try:
				mention = str()
				hour, minute, second = str(t//3600).zfill(2), str((t%3600)//60).zfill(2), str((t%3600)%60).zfill(2)
				# better embed when start match
				embed_startmatch = discord.Embed(title="Trận đấu bắt đầu !", description=f"Thời gian làm bài là {hour}:{minute}:{second}.\nNếu như đã làm xong vui lòng gửi bài của mình cho <@!740475107947839508> !", color=discord.Color.green())
				for u in user:
					mention += f"{u.mention}\n"
					await u.send(embed=discord.Embed(title="Duelist Tournament", description=msg, color=discord.Color.green()))
				embed_startmatch.add_field(name="Thí sinh", value=mention)
				await ctx.message.delete()
				msg = await ctx.send(embed=embed_startmatch)
				await asyncio.sleep(t)
				await msg.delete()
				for u in user:
					await u.send(embed=discord.Embed(title="Duelist Tournament", description="Hiện tại thời gian làm bài đã hết vui lòng bạn gửi bài làm của mình dưới dạng file nén `DUEL_<tên thí sinh>.zip` cho <@!740475107947839508> để tiến hành nộp bài !", color=discord.Color.red()))
				await ctx.send(mention.replace('\n', ' '))
				await ctx.send(embed=discord.Embed(title="Trận đấu kết thúc", description="Hiện tại thời gian làm bài đã hết vui lòng bạn gửi bài làm của mình dưới dạng file nén `DUEL_<tên thí sinh>.zip` cho <@!740475107947839508> để tiến hành nộp bài !", color=discord.Color.red()))
			except:
				await ctx.send("**Can't start match ! Something went wrong !**")

		######################################################################

		@self.command(name="resetall")
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

		"""
		@self.command(name="submit")
		@commands.has_any_role('Admin', 'Duelist Contestant')
		async def submit(ctx, problem):
			att_url = ctx.message.attachments[0].url
			file_req = requests.get(att_url)
			f = codecs.open('content.txt', 'w', encoding='utf-8')
			f.write(file_req.content.decode('utf-8'))
			f.close()
			await ctx.message.delete()
			await ctx.send(f"**Success ! :white_check_mark:**")
		"""

		# clean temporary file command ###########################################
		@self.command(name='clean')
		@commands.cooldown(1, 15, commands.BucketType.user)
		@commands.has_role("Admin")
		async def clean(ctx):
			for file in os.listdir('./temp'):
				os.remove(f"./temp/{file}")
			await ctx.send("**Cleaned temporary file on server ! :white_check_mark:**")

		# handling error for clean command
		@clean.error
		async def clean_err(ctx, err):
			if isinstance(err, commands.CommandOnCooldown):
				await ctx.send(f"**Command in cooldown, retry after {int(err.retry_after)}s.**")

		######################################

		# run code command
		@self.command(name='run')
		@commands.cooldown(1, 10, commands.BucketType.user)
		async def run(ctx, language_ext: str, *stdin):
			if language_ext == 'info':
				info_embed = discord.Embed(title="Version language from server", color=discord.Color.blue())
				lang, version = str(), str()
				if len(stdin) != 1:
					for (key, value) in LANG_INFO.items():
						lang += f"{key}" + '\n'
						version += f"{value}" + '\n'
				info_embed.add_field(name="Language version", value=version)
				info_embed.add_field(name="Aliases", value=lang)
				await ctx.send(embed=info_embed)
			if len(stdin) == 0:
				stdin = str()
			elif stdin[0] == stdin[-1] and stdin[0] == '```':
				stdin = '\n'.join(list(stdin)).replace('```', '')[1:-1]
			else:
				stdin = '\n'.join(stdin[0].split(r'\n'))
			if len(ctx.message.attachments):
				att_url = ctx.message.attachments[0].url
				file_req = requests.get(att_url)
				file_save = str(ctx.author.id) + f'.{language_ext}'
				f = codecs.open(f'./temp/{file_save}', 'w', encoding='utf-8')
				f.write(file_req.content.decode('utf-8'))
				f.close()
				hashing = Runner().get_hash_code(file_save)
				msg = await ctx.send("`Compile and running file ...`")
				if str(hashing + '.exe') not in os.listdir('./temp'):
					await Runner()._compile(file_save, language_ext)
				await msg.edit(content="`Running ...`")
				try:
					t = await Runner()._run(file_save, stdin, language_ext)
				except subprocess.TimeoutExpired:
					raise discord.ext.commands.CommandInvokeError('Time expired while running program (5s).')
				done_embed = discord.Embed(description=f"Result of session {ctx.author.mention}", color=discord.Color.green())
				done_embed.add_field(name="Stdin", value=f"```\n{str(stdin)}\n```", inline=False)
				done_embed.add_field(name="Output", value=f"```\n{codecs.open(f'./temp/{hashing}.output', 'r', encoding='utf-8').read()}\n```", inline=False)
				done_embed.add_field(name="Time", value=f"```\n{t}\n```", inline=False)
				done_embed.set_footer(text=f"Session ID: {hashing}")
				await msg.edit(embed=done_embed)

		@run.error
		async def run_err(ctx, err):
			if isinstance(err, commands.CommandInvokeError):
				msg = err.original
				await ctx.send(embed=discord.Embed(title="Error !", description=str(msg), color=discord.Color.red()))

		##############################################

load_dotenv('.env')

TOKEN = os.environ.get('BOT_TOKEN')

bot = LcDuel(command_prefix=']')
bot.run(TOKEN)