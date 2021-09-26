import os, hashlib, codecs, time, subprocess

LANG_INFO = {
	'cpp': 'GNU C++17',
	'c': 'GNU C17',
	'cs': '.NET (C# 5)',
	'pas': 'Free Pascal 3.0.2',
	'py': 'Python 3.8.5',
	'rb': 'Ruby 3.0.2p107',
	'js': 'NodeJS 14.17.0',
	'julia': 'Julia 1.6.1'
}

class CompilationError(Exception):
	def __init__(self, msg="Please check your code again before running it"):
		self.msg = msg
		super().__init__(self.msg)

class RunnerError(Exception):
	def __init__(self, return_code, msg="Error occurred, return code {0}"):
		self.return_code = return_code
		self.msg = msg
		super().__init__(self.msg.format(self.return_code))

class RestrictedLibraryError(Exception):
	def __init__(self, library, msg="You can't use module or library \"{0}\""):
		self.lib = library
		self.msg = msg
		super().__init__(self.msg.format(self.lib))

class Runner:
	def __init__(self):
		self.compile_cmd = {
			'cpp': 'g++ temp/{0} -o temp/{1} -std=c++17 -O2 -march=native',
			'c': 'gcc temp/{0} -o temp/{1} -std=c17 -O2 -march=native',
			'cs': 'csc /langversion:5 /target:exe /out:temp\\{1} temp\\{0} > ./temp/csccompile.log',
			'pas': 'fpc temp/{0} -otemp/{1} -O2 > ./temp/pascompile.log'
		}
		self.run_cmd = {
			'cpp': '{p}/temp/{h}.exe',
			'c': '{p}/temp/{h}.exe',
			'cs': '{p}/temp/{h}.exe',
			'pas': '{p}/temp/{h}.exe',
			'py': 'python {p}/temp/{h}.py',
			'rb': 'ruby {p}/temp/{h}.rb',
			'js': 'node {p}/temp/{h}.js',
			'julia': 'julia {p}/temp/{h}.julia --startup-file=no -O0 --inline=yes --compile=min'
		}
		self.restricted = {
			'cpp': ['Windows.h', 'unistd.h', 'system', 'fstream', 'stdlib.h', 'FILE'],
			'c': ['Windows.h', 'unistd.h', 'system', 'fstream', 'stdlib.h', 'FILE'],
			'cs': ['System.Diagnostics', 'Process', 'File'],
			'py': ['os', 'pymem', 'tkinter', 'subprocess', 'codecs', 'open'],
			'rb': ['system', '`', 'File'],
			'js': ['child_process', 'FileReader'],
			'pas': ['crt'],
			'julia': ['open', 'run']
		}
		self.interpret_lang = ['py', 'rb', 'js', 'julia']

	def get_hash_code(self, filepath):
		file = codecs.open(f"./temp/{filepath}", 'r', encoding='utf-8')
		content = file.read().replace('\r\n', '').replace('\t', '')
		file.close()
		return hashlib.md5(content.encode('utf-8')).hexdigest()

	async def _compile(self, filepath, language):
		# compile
		if language in self.interpret_lang:
			return

		content = codecs.open(f'./temp/{filepath}', 'r', encoding='utf-8').read()

		for restrict in self.restricted[language]:
			if restrict in content:
				raise RestrictedLibraryError(library=restrict)

		err_code = os.system(self.compile_cmd[language].format(filepath, self.get_hash_code(filepath) + '.exe'))
		#err_code = os.system("g++ temp/{filepath} -o temp/{self.get_hash_code(filepath)}.exe ")
		if err_code:
			raise CompilationError()

	async def _run(self, filepath, txtstdin, language_ext):
		hashing = self.get_hash_code(filepath)
		# if is the interpret language write hashing session
		if language_ext in self.interpret_lang:
			f = codecs.open(f'./temp/{filepath}', 'r', encoding='utf-8')
			file = codecs.open(f'./temp/{hashing}.{language_ext}', 'w', encoding='utf-8')
			file.write(f.read())
			f.close()
			file.close()
		# write stdin into file:
		file = codecs.open(f'./temp/{hashing}.input', 'w', encoding='utf-8')
		file.write(txtstdin)
		file.close()

		fin = codecs.open(f'./temp/{hashing}.input', 'r', encoding='utf-8')
		fout = codecs.open(f'./temp/{hashing}.output', 'w', encoding='utf-8')

		# run file with stdin
		parent = os.getcwd()
		start = time.process_time()
		return_code = subprocess.call(self.run_cmd[language_ext].format(p=parent, h=hashing).split(), shell=True, timeout=10, stdin=fin, stdout=fout)
		end = time.process_time()

		fin.close()
		fout.close()

		if return_code:
			raise RunnerError(return_code=return_code)

		return end - start