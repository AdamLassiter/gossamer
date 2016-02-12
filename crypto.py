from Crypto import Random
from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES

# TODO: Test module


# Uses Random
def NewKey(length):
	Random.new().read(length)



# Uses SHA512
class Hash:

	def __init__(self):
		pass


	def digest(self, text, n=1024):
		hash_obj = SHA512.new(text)
		for i in xrange(n - 1):
			hash_obj = SHA512.new(hash_obj.digest())
		return hash_obj.digest()



# Uses AES in CFB block mode
class SymmetricEncryption:

	def __init__(self, strength=128, key=None):
		self.key    = key if key else NewKey(strength >> 3) # bits -> bytes


	def __repr__(self):
		return self.key


	def __str__(self):
		return self.key


	def encrypt(self, text):
		iv     = NewKey(AES.block_size)
		cipher = AES.new(self.key, AES.MODE_CFB, iv)
		return iv + cipher.encrypt(text)


	def decrypt(self, text):
		iv, text = text[:AES.block_size], text[AES.block_size:]
		cipher   = AES.new(self.key, AES.MODE_CFB, iv)
		return cipher.decrypt(text)



# Uses RSA
class AsymmetricEncryption:

	def __init__(self, strength=2048, key=None):
		self.key = RSA.importKey(key) if key else RSA.generate(strength)


	def __repr__(self):
		return self.key.privatekey().exportKey()


	def __str__(self):
		return self.key.publickey().exportKey()


	def encrypt(self, text):
		return self.key.encrypt(text, "")[0]


	def decrypt(self, text):
		return self.key.decrypt(text)



# Uses NewKey
class SaltedPadding:

	def __init__(self, padding_width=32, control_char=255):
		self.padding_width = padding_width
		self.control_char  = chr(control_char)
		self.control_ord   = control_char


	def pad(self, text):
		assert len(text) <= 30
		text += self.control_char
		salt  = NewKey(self.padding_width - len(text))
		salt  = salt.replace(self.control_char, chr((self.control_ord + 1) % 256))
		return text + salt


	def unpad(self, text):
		assert len(text) == self.padding_width
		control_char_pos = -(1 + reversed(text).index(self.control_char))
		return text[ :control_char_pos ]



# Uses AsymmetricEncryption
class Signature:

	def __init__(self, strength=2048, key=None):
		self.key = AsymmetricEncryption(strength=strength, key=key)


	def __repr__(self):
		return self.key.privatekey().exportKey()


	def __str__(self):
		return self.key.publickey().exportKey()


	def sign(self, text):
		return self.key.encrypt(Hash().digest(text))


	def verify(self, signature, text):
		if not self.key.decrypt(signature) == Hash().digest(text):
			raise Exception()



# Uses Hash
class HashChain:

	def __init__(self):
		self.my_new_raw  = NewKey(64)
		self.my_new_hash = Hash().digest(self.my_new_raw)
		self.my_old_raw  = None
		self.your_hash   = None


	def chain(self):
		self.my_old_raw  = self.my_new_raw
		self.my_new_raw  = NewKey(64)
		self.my_new_hash = Hash().digest(self.my_new_raw)
		return self.my_old_raw + self.my_new_hash


	def verify(self, hashes):
		if self.your_hash:
			your_raw   = hashes[:64]
			your_hash  = hashes[64:]
			if not Hash().digest(your_raw) == self.your_hash:
				raise Exception()
		self.your_hash = your_hash
