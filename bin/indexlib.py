import array
import shelve
import xml.sax
from xmlhandler.corpusXMLHandler import CorpusXMLHandler
from xmlhandler.classes.sentence import Sentence
from xmlhandler.classes.word import Word

NGRAM_LIMIT=16

def make_array(initializer=None):
	if initializer is None:
		return array.array('L')
	else:
		return array.array('L', initializer)


# Taken from counter.py
def load_array_from_file( an_array, a_filename ) :
    MAX_MEM = 10000
    fd = open( a_filename )
    isMore = True
    while isMore :
        try :    
            an_array.fromfile( fd, MAX_MEM )
        except EOFError :
            isMore = False # Did not read MAX_MEM_ITEMS items? Not a problem...
    fd.close()

def save_array_to_file(array, path):
	file = open(path, "w")
	array.tofile(file)
	file.close()

def load_symbols_from_file(symbols, path):
	file = shelve.open(path)
	sym = {}
	sym.update(file)
	symbols.symbol_to_number = sym['symbol_to_number']
	symbols.number_to_symbol = sym['number_to_symbol']
	file.close()

def save_symbols_to_file(symbols, path):
	sym = {"symbol_to_number": symbols.symbol_to_number,
	       "number_to_symbol": symbols.number_to_symbol}
	file = shelve.open(path)
	file.clear()
	file.update(sym)
	file.close()


#def compare_indices(corpus, max, pos1, pos2):
#	while pos1<max and pos2<max and corpus[pos1] == corpus[pos2]:
#		pos1 += 1
#		pos2 += 1
#
#	if pos1>=max:
#		return -1
#	elif pos2>=max:
#		return 1
#	else:
#		return int(corpus[pos1] - corpus[pos2])

def compare_ngrams(ngram1, pos1, ngram2, pos2, ngram1_exhausted=-1, ngram2_exhausted=1, limit=NGRAM_LIMIT):
	max1 = len(ngram1)
	max2 = len(ngram2)
	i = 0
	while pos1<max1 and pos2<max2 and ngram1[pos1]==ngram2[pos2] and i<NGRAM_LIMIT:
		pos1 += 1
		pos2 += 1
		i += 1

	if pos1>=max1 and pos2>=max2:
		return 0
	elif pos1>=max1:
		return ngram1_exhausted
	elif pos2>=max2:
		return ngram2_exhausted
	else:
		return int(ngram1[pos1] - ngram2[pos2])


class SymbolTable():
	def __init__(self):
		self.symbol_to_number = {'': 0}
		self.number_to_symbol = ['']
		self.last_number = 0

	def intern(self, symbol):
		if not self.symbol_to_number.has_key(symbol):
			self.last_number += 1
			self.symbol_to_number[symbol] = self.last_number
			#self.number_to_symbol[self.last_number] = symbol
			self.number_to_symbol.append(symbol)  # Risky and not intention-expressing

		return self.symbol_to_number[symbol]


class SuffixArray():
	def __init__(self):
		self.corpus = make_array()    # List of word numbers
		self.suffix = make_array()    # List of word positions
		self.symbols = SymbolTable()  # word<->number conversion table

	def set_basepath(self, basepath):
		self.basepath = basepath
		self.corpus_path = basepath + ".corpus"
		self.suffix_path = basepath + ".suffix"
		self.symbols_path = basepath + ".symbols"

	def load(self):
		load_array_from_file(self.corpus, self.corpus_path)
		load_array_from_file(self.suffix, self.suffix_path)
		load_symbols_from_file(self.symbols, self.symbols_path)

	def save(self):
		save_array_to_file(self.corpus, self.corpus_path)
		save_array_to_file(self.suffix, self.suffix_path)
		save_symbols_to_file(self.symbols, self.symbols_path)

	def append_word(self, word):
		self.corpus.append(self.symbols.intern(word))

	# For debugging.
	def append_string(self, sentence):
		for w in sentence.split():
			self.append_word(w)

	def build_suffix_array(self):
		tmpseq = range(0, len(self.corpus))
		tmpsuf = sorted(tmpseq, cmp=(lambda a,b: compare_ngrams(self.corpus, a, self.corpus, b)))
		self.suffix = make_array(tmpsuf)


	def find_ngram_range(self, ngram, min=0, max=None):
		# Returns a tuple (min, max) of matching ngram positions in suffix array
		# TODO: We will need a more "incremental" approach for searching for
		# patterns that use multple word attributes.
		
		if max is None:
			max = len(self.suffix) - 1

		first = self.binary_search_ngram(ngram, min, max, (lambda a,b: a >= b))
		last  = self.binary_search_ngram(ngram, min, max, (lambda a,b: a > b)) - 1

		if first <= last:
			return (first, last)
		else:
			return None

	def binary_search_ngram(self, ngram, min, max, cmp):
		# Find the least suffix that satisfies suffix `cmp` ngram.
		while min < max:
			mid = (min+max)/2
			if cmp(compare_ngrams(self.corpus, self.suffix[mid], ngram, 0, ngram2_exhausted=0), 0):
				max = mid      # If 'mid' satisfies, then what we want *is* mid or *is before* mid
			else:
				mid += 1
				min = mid      # If 'mid' does not satisfy, what we want *must be after* mid.

		return mid


	# For debugging.
	def dump_suffixes(self, limit=10):
		for pos in self.suffix:
			print "%4d:" % pos,
			for i in range(pos, pos+limit):
				if i < len(self.corpus):
					print self.symbols.number_to_symbol[self.corpus[i]],
				else:
					print "*",

			print ""


class Index():
	# Attribute order must be the same as the parameters of 'Word'
	WORD_ATTRIBUTES = ['surface', 'lemma', 'pos', 'syn']

	def __init__(self):
		self.arrays = {}
		for attr in Index.WORD_ATTRIBUTES:
			self.arrays[attr] = SuffixArray()  ## Always initialize?

	#def load(self, attribute, basepath):
	#	array = self.arrays[attribute] = SuffixArray()
	#	array.set_basepath(basepath)
	#	array.load()

	def set_basepath(self, path):
		for attr in Index.WORD_ATTRIBUTES:
			self.arrays[attr].set_basepath(path + "." + attr)

	def load_all(self):
		for array in self.arrays.values():
			array.load()

	def save_all(self):
		for array in self.arrays.values():
			array.save()

	def append_sentence(self, sentence):
		# Adds a sentence (presumably extracted from a XML file) to the index.

		for attr in Index.WORD_ATTRIBUTES:
			for word in sentence.word_list:
				value = getattr(word, attr)
				self.arrays[attr].append_word(value)
			self.arrays[attr].append_word('')  # '' (symbol 0)  means end-of-sentence

	def build_suffix_arrays(self):
		for attr in Index.WORD_ATTRIBUTES:
			print "Building suffix array for %s..." % attr
			self.arrays[attr].build_suffix_array()

	def iterate_sentences(self):
		# Returns an iterator over all sentences in the corpus.

		id = 1
		guide = Index.WORD_ATTRIBUTES[0]        # guide?
		length = len(self.arrays[guide].corpus)

		words = []
		for i in range(0, length):
			if self.arrays[guide].corpus[i] == 0:
				# We have already a whole sentence.
				sentence = Sentence(words, id)
				id += 1
				words = []
				yield sentence

			else:
				args = []
				for attr in Index.WORD_ATTRIBUTES:
					number = self.arrays[attr].corpus[i]
					symbol = self.arrays[attr].symbols.number_to_symbol[number]
					args.append(symbol)
				
				args.append([])
				words.append(Word(*args))

	# For debugging.
	def print_sentences(self):
		for sentence in self.iterate_sentences():
			for word in sentence.word_list:
				print word.surface,
			print ""



# For testing.
#h = SuffixArray()
#s = "the quick brown fox jumps over the lazy dog which wanted the fox to jump away into the house"
#h.append_string(s)
#h.build_suffix_array()

# For more testing.
def index_from_corpus(path):
	#file = open(path)
	parser = xml.sax.make_parser()
	index = Index()
	parser.setContentHandler(CorpusXMLHandler(index.append_sentence))
	parser.parse(path)
	index.build_suffix_arrays()
	return index

#h = index_from_corpus("../toy/genia/corpus.xml")

#h.set_basepath("/tmp/foo")
#h.save_all()
