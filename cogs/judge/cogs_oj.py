import discord, requests, codecs, os, subprocess

from .runner import Runner, LANG_INFO
from discord.ext import commands

class OJ(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def run(self, ctx, language_ext: str, *stdin):
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
	async def run_err(self, ctx, err):
		if isinstance(err, commands.CommandInvokeError):
			msg = err.original
			await ctx.send(embed=discord.Embed(title="Error !", description=str(msg), color=discord.Color.red()))

def setup(bot):
	bot.add_cog(OJ(bot))