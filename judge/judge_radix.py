import sys, codecs

class RadixJudge:
	def __init__(self, **kwargs):
		self.settings = {
			"allow_temp_0": False,
		}

	def _differ(self, fileo, differ_fileo):
		f1 = codecs.open(fileo, 'r', encoding='utf-8')
		f2 = codecs.open(differ_fileo, 'r', encoding='utf-8')