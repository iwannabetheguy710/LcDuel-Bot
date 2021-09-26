import discord, json, codecs, requests, asyncio, os

from dotenv import load_dotenv
from discord.ext import commands

class LcDuel(commands.Bot):
	def __init__(self, command_prefix, self_bot=False):
		"""
		f = codecs.open('data.json', 'r', encoding='utf-8')
		self.data = json.loads(f.read())
		f.close()
		"""

		super().__init__(command_prefix=command_prefix, self_bot=self_bot)
		self.load_extension('cogs.ratings.cogs_ratings')
		self.load_extension('cogs.judge.cogs_oj')
		self.init_command()

	# on_ready function will auto called when the bot start
	async def on_ready(self):
		await self.change_presence(activity=discord.Game(name="Hệ thống Duelist mới !"))
		print("The bot is start ... Now !")

	# on_message function will auto called when user send message
	async def on_message(self, message):
		await self.process_commands(message)

	# a init command function all command of this bot will be declared here
	def init_command(self):
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

load_dotenv('.env')

TOKEN = os.environ.get('BOT_TOKEN')

bot = LcDuel(command_prefix=']')
bot.run(TOKEN)