import sys, codecs

class DiffJudgement:
	def __init__(self, **kwargs):
		self.settings = {
			"allow_tail_space": False,
			"allow_head_space": True,
			"allow_tail_blank_line": False,
			"allow_head_blank_line": True
		}
		for setting in kwargs:
			if setting in self.settings:
				self.settings[setting] = kwargs[setting]
			else:
				raise KeyError(f"invalid setting \'{setting}\'")

	def _differ(self, fileo: str, differ_fileo: str):
		f1 = codecs.open(fileo, 'r', encoding='utf-8')
		f2 = codecs.open(differ_fileo, 'r', encoding='utf-8')

		output = f1.read().split('\r\n')
		differ_output = f2.read().split('\r\n')

		if not self.settings['allow_head_blank_line']:
			while bool(len(output)) and output[0] == str():
				output.pop(0)
			while bool(len(differ_output)) and differ_output[0] == str():
				differ_output.pop(0)
		if not self.settings['allow_tail_blank_line']:
			while bool(len(output)) and output[-1] == str():
				output.pop(-1)
			while bool(len(differ_output)) and differ_output[-1] == str():
				differ_output.pop(-1)

		if len(output) != len(differ_output):
			return False

		for i in range(len(output)):
			if not self.settings['allow_tail_space']:
				output[i] = output[i].rstrip()
				differ_output[i] = differ_output[i].rstrip()
			if not self.settings['allow_head_space']:
				output[i] = output[i].lstrip()
				differ_output[i] = differ_output[i].lstrip()

		for i in range(len(output)):
			if output[i] != differ_output[i]:
				return False

		f1.close()
		f2.close()

		return True

sys.stdout.write(str(DiffJudgement(allow_tail_space=False)._differ('../OUT1', '../OUT2')))