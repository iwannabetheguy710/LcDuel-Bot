class ELO:
	@staticmethod
	def key_K(R, M): # function to get K key, force user get inflationary of ELO
		K = 70
		if M > 3:
			K -= 50

		if R < 1800:
			K += 5
		elif R > 1800:
			K -= 10
			if R > 2300:
				K -= 5
		return K
	@staticmethod
	def change_rating(Ra, Rb, Ma, Mb, Sa, Sb): # rating calculate function with ELO System
		Qa = 10 ** (Ra / 400)
		Qb = 10 ** (Rb / 400)
		Ea = Qa / (Qa + Qb)
		Eb = Qb / (Qa + Qb)
		Ka, Kb = ELO.key_K(Ra, Ma), ELO.key_K(Rb, Mb)
		Ra_ = Ra + Ka*(Sa - Ea)
		Rb_ = Rb + Kb*(Sb - Eb)
		return [Ra_ - Ra, Rb_ - Rb]