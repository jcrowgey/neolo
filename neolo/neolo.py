#!/usr/bin/env python3
#
# script commissioned by Saulo
# originally intended to identify "neologisms" in a text by
# searching through a given dictionary/wordlist/othertext
#
# now supports many other statistical operations as well
#

import sys
import re
from collections import Counter
from math import factorial as fact
from math import sqrt
from functools import reduce
import operator
import argparse
import codecs
import logging

PUNC_STR = '([_+\-\(\)\.,:;!?\'"\[\]])'
PUNC_RE = re.compile(PUNC_STR)
S_RE    = re.compile('[\.!?]')

def lemma1(N,p):
  """return a value for p which is the sum of int(n/p^i) for all i where
  int(n/p^i) <= n"""

  v = 1
  i = 1
  tosum = []
  while v>=1:
    v = int(float(N)/float(p**i))
    if v<1:
      break
    tosum.append(v)
    i+=1
  return sum(tosum)

def lemma2(X):
  """See Wu 1993'An Accurate computation of the hypergeometric
  distribution function'.

  We can calculate n! = p1^r1*p2^r2...pk^rk where ps are prime numbers less
  than or equal to n.  The exponent for each p is given by lemma1(n,p).

  So, we will return here for X! a list of primes to be multipled.  For example,
  X = 5.

  1. Find primes less than or equal to 5
    erasthos(5) = [2, 3, 5]
  2. For each of these primes, find the exponent
    2: int(5/2) + int(5/2^2) = 2 + 1 = 3
    3: int(5/3) = 1
    5: int(5/5) = 1

  3. we have [ 2^3 * 3^1 * 5^1 ] so return {2:3,3:1,5:1}"""

  primes = erathos(X)
  exp = {}
  for p in primes:
    exp[p] = lemma1(X,p)
  return exp

def erathos(N):
  """Return all prime numbers <= N"""
  if N < 2: return []
  lng = ((N//2)-1+N%2)
  sieve = [True]*(lng+1)
  for i in range(int(sqrt(N)) >> 1):
    if not sieve[i]: continue
    for j in range((i*(i+3)<<1) +3, lng, (i<<1)+3):
      sieve[j] = False
  primes = [2]
  primes.extend([(i<<1) + 3 for i in range(lng) if sieve[i]])
  return primes

def wu_hypergeom_0(r,n,N):
  """Instead of using m!(N-r)!/N!(m-r)!, caclulate a series of factors
  for num and denom and then cancel common terms for a simplest fraction
  to do the actual computation"""

  m = N - n
  m_fact = lemma2(m)
  N_minus_r_fact = lemma2(N-r)
  N_fact = lemma2(N)
  m_minus_r_fact = lemma2(m-r)

  # numerator
  num = Counter(m_fact)
  num.update(N_minus_r_fact)

  # denominator
  den = Counter(N_fact)
  den.update(m_minus_r_fact)

  # now reduce the faction to simplest terms
  simple_num = {}
  simple_den = {}
  for f in num:
    if f in den:
      if num[f] == den[f]: continue
      elif num[f] < den[f]: simple_den[f] = den[f]-num[f]
      else: simple_num[f] = num[f] - den[f]
    else: simple_num[f] = num[f]
  for f in [ v for v in den if v not in num ]:
    simple_den[f] = den[f]


  # finally, evaluate the fraction
  final_num = product([k**v for k,v in simple_num.items()])
  final_den = product([k**v for k,v in simple_den.items()])

  return final_num/final_den

def product(iterable):
  return reduce(operator.mul, iterable, 1)

def hypergeom_0(r,n,N):
  getcontext().prec = 3
  m = N - n
  return Decimal(fact(m)*fact(N-r))/Decimal(fact(N)*fact(m-r))

def tokenize(f):
  """Tokenize all the lines in a file"""
  # TODO need a more robust, crosslingual tokenizer
  return [PUNC_RE.sub(" \g<0> ",l) for l in f]

def downcase(f):
  """Stem, downcase all the lines in a file"""
  # TODO: still need a stem method (this is language dependent!
  return [l.lower() for l in f]

def count(f):
  """Return the words of f as a dictionary with keys as wordforms and
  counts as values"""
  return Counter(f)

def chunks(l, n):
  """Yield successive n-sized chunks from l"""
  for i in range(0, len(l), n):
    yield l[i:i+n]

def hdd(types):
  """Calculate HD-D (McCarthy and Jarvis 2007,2010),

  1. for each wordtype, calculate the probability of drawing it
  in a random sample of 42 tokens
  (note, the positive occurance of a wordtype = 1/42 of the TTR, because
  subsequent appearances of that type in a sample don't add another type)

  2. need to consider probability of occuring once + twice + ...
  therefore it's easier to consider the probability of occuring 0 times and
  take 1 - p.


  3. calculate this values * 1/42 to get each word's contribution

  main hypergeom function:
  h(x;r,n,N) = n!r!(N-n)!(N-r)! / N!x!(n-x)!(r-x)!(N-n-r+x)!
  but see Wu 1993 for a simplified method
  """

  hdd = 0.0
  toks = sum(types.values())
  for t in types:
    hdd += (1-wu_hypergeom_0(42, types[t], toks))*(1/42)
  return hdd

def msttr(text):
  """Mean segmental type-token ratio (Johnson,1944)

  From Saulo's description:
  1. Divide the text into equal segments by word tokens (100 words)
  2. For each segment, calculate the token-type ratio
  3. Calculate the arithmetic mean of the TTRs for each segment
  """

  segments = chunks(" ".join(text).split(),100)
  ttrs=[]
  for seg in segments:
    types = Counter(seg)
    ttrs.append(float(len(types))/float(sum(types.values())))
  return sum(ttrs)/float(len(ttrs))

def mltd(text):
  """Measure of Lexical Textual Diversity (McCarthy, 2005)

  From Saulo's description:
  1. Start by adding words to a segment until type/token ratio falls to 0.72,
  then continue at the next segment
  2. Measure ratio of tokens/number-of-segments"""
  seg_n = 0
  seg = []
  toks = 0
  for w in " ".join(text).split():
    toks+=1
    seg.append(w)
    types = Counter(seg)
    if float(len(types))/float(sum(types.values()))<0.72:
      seg_n+=1
      seg = []
  return float(toks)/float(seg_n)

def wordlen_dist(text_words):
  maxlen = max([len(w) for w in text_words])
  print("\nWord-length distribution:")
  print("Length: Count\n-------------")
  for i in range(1,maxlen+1):
    print(str(i)+":",len([w for w in text_words if len(w) == i]))
  print("-------------")

def punc_ratio(text_words):
  pcount=0
  for t in text_words:
    if PUNC_RE.match(t):
      pcount+=text_words[t]
  return pcount/sum(text_words.values())

      
def sent_split(inlines, abbrevs=None):
  """join and split inlines and return outlines as 
     one sentence per line, abbrevs is a list of non-sentence
     splitting stings (which presumably have the relevant punc)"""


  outlines = []
  lcont = ''
  for l in inlines:
    ## if this line is empty, continue to next
    if l.strip() == "": continue

    ## protect any abbrevs by using a tag string and the abbrevs index
    if abbrevs != None:
      for i,a in enumerate(abbrevs):
      
        # if a has a dot then i need to escape it
        if a.find('.') != -1:
          a = a[0:a.find('.')]+r'\.'+a[a.find('.')+1:]

        AB_RE=re.compile(r'\b'+a)
        while AB_RE.search(l) != None:
          m = AB_RE.search(l)
          print("matched for "+a+" in "+l+"at "+str(m.span()),file=sys.stderr)
          l=l[0:m.span()[0]]+"#ABTAG"+str(i)+"#"+l[m.span()[0]+len(a)-1:]
          print("after sub for "+a+" in "+l+"at "+str(m.span()),file=sys.stderr)

    ## split the current l into groups
    lparts = S_RE.split(l.strip())

    ## see if there's more than one part
    if len(lparts) > 1: # multi part

      ## append any lcont to the first
      lparts[0] = lcont+" "+lparts[0]
      lcont=""

      ## see if the last segment will continue to the next
      if not S_RE.match(l.strip()[-1]):
        outlines.extend([p.strip() for p in lparts[0:-2] if p.strip() != ''])
        lcont=lparts[-1]
      else: 
        outlines.extend([p.strip() for p in lparts if p.strip() != ''])

    else: # just one part here
      ## see if this line will continue to the next
      if not S_RE.match(l.strip()[-1]):
        lcont=lcont+" "+l.strip()
      else:
        if lcont+" "+l.strip() != '':
          outlines.append(lcont+" "+l.strip())

  # go through outlines and put back strings from abtags
  ## need regex to find \d+ not just a single d
  if abbrevs != None:
    ABTAG_NUM_RE=re.compile('#ABTAG([0-9]+)#')
    cleanlines = []
    for o in outlines:
      print("preclean: "+o,file=sys.stderr)
      while o.find("#ABTAG") > -1:
        i = int(ABTAG_NUM_RE.search(o).group(1))
        o = o[0:o.find("#ABTAG")]+abbrevs[i]+" "+o[o.find("#ABTAG")+7+len(str(i)):]
      cleanlines.append(o)
      print("cleaned: "+o,file=sys.stderr)
    return cleanlines 
  else: return outlines

def setup_argparse():
  ap = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      description="Extract lexical statistics from a text file.",
      epilog="""Select one or more statistics via the above options.

Note that some options with optional args (--sents/-s, eg) or options 
which take lists of files (--dicts, eg) can create ambiguity parsing 
the command line.  When using these options, it may be best to place 
them after the name of the text you're trying to analyze:

$ ./neolo mytext.txt --dicts d1.txt d2.txt -sents abbrevs.txt""")
  ap.add_argument('text', metavar="TEXT", type=str,
      help="the text you want to investigate")
  ap.add_argument('--dicts', metavar="DICT", nargs='+',
      help="a list of reference texts to compute neologism count")
  ap.add_argument('--mltd', action="store_true",
      help="measure of lexical textual diversity")
  ap.add_argument('--msttr', action="store_true",
      help="mean segmental type-token ratio")
  ap.add_argument('--hdd', action="store_true", help="HD-D probabilistic TTR")
  ap.add_argument('--verbose', '-v', action='count', dest='verbosity',
      default=1, help='increase the verbosty (can be repeated: -vvv)')
  ap.add_argument('--wordlen', '-w', action="store_true",
      help="print the distribution of words by length")
  ap.add_argument('--wordtypes', '-t', action="store_true",
      help="print the distribution of wordtypes (unigrams) by count")
  ap.add_argument('--hapax', '-x', action="store_true",
      help="print the list of hapax legomena")
  ap.add_argument('--punc-ratio', '-p', action="store_true",
      help="print the ratio of punctuation tokens out of total tokens")
  ap.add_argument('--no-hyphen', '-y', action="store_true",
      help="remove the hyphen (-) from the list of punctuation symbols"+\
           " used in tokenization")
  ap.add_argument('--no-apostrophe', '-a', action="store_true",
      help="remove the apostrophe (') from the list of punctuation symbols"+\
           " used in tokenization")
  ap.add_argument('--sents', '-s', metavar="ABBREV", const='noabbrev',
      nargs='?',
      help="print sentence length statistics, uses an (optional) "+\
           "abbreviations file containing stings which don't end sentences "+\
           "(eg: Mr.).  One abbreviaion per line, include relevant "+\
           "punctuation.  Note that items in the abbreviations file will "+\
           "also be protected during later tokenization.")
  return ap

def try_open(filename):
  """Try several encodings and return the lines from the first one 
     that seems to work"""
  text = ''
  encodings = ['utf-8', 'latin1', 'windows-1250', 'windows-1252']
  for e in encodings:
    try:
      fh = codecs.open(filename, 'r', encoding=e)
      text = fh.readlines()
    except UnicodeDecodeError:
      s = "Got unicode error with "+e+" trying different encoding"
      logging.warning(s)
    else:
      s = "Opening "+filename+"with encoding: "+e
      logging.info(s)
      break 
  return text

def main():
  ap = setup_argparse()
  args = ap.parse_args()
  logging.basicConfig(format='%(levelname)s:%(message)s',
                          level=50-(args.verbosity*10))
  text = try_open(args.text)

  if args.no_apostrophe:
    PUNC_STR = '([_+\-\(\)\.,:;!?"\[\]])'
    PUNC_RE = re.compile(PUNC_STR)
  if args.no_hyphen:
    PUNC_STR = ''.join(PUNC_STR.split('-'))
    PUNC_RE = re.compile(PUNC_STR)

  ## if sents option, use the sent_split version of the basic text
  if args.sents:
    abbrevs=None
    if args.sents!='noabbrev':
      # open abbreviations file
      abbrevlines = try_open(args.sents)
      abbrevs = [ a.strip() for a in abbrevlines ]
    text = sent_split(text, abbrevs=abbrevs)

  logging.info("Tokenizing, downcasing, text: "+str(args.text)+" ...")
  clean_text = downcase(tokenize(text))
  if args.sents:
    print(len(clean_text),"sentences in your text.")
    print("Average sentence length:",
           sum([len(l.split()) for l in clean_text])/len(clean_text),
           "tokens.")
  logging.info("... done.")
  # get the wordtypes and counts
  logging.info("Counting and sorting words in "+str(args.text)+" ...")
  text_words = count([w for l in clean_text for w in l.split()])
  logging.info("... done.")
  hapax = [ w for w in text_words if text_words[w] == 1 ]


  dicts = []
  if args.dicts:
    dicts = [ try_open(f) for f in args.dicts ]
    logging.info("Tokenizing, downcasing, dict files:"+str(args.dicts)+" ...")
    clean_dicts = [ downcase(tokenize(d)) for d in dicts ]
    logging.info("... done.")
    logging.info("Counting and sorting words in dictonaries:"+str(args.dicts)+" ...")
    dict_words = count([w for l in
                      [line for clean_d in clean_dicts for line in clean_d]
                      for w in l.split()])
    logging.info("... done.")

    # print neolo
    print("Neologism list:")
    neolo = 0
    for w in sorted(text_words):
      if not w in dict_words:
        print(w)
        neolo+=1

  print("\nStatistics:")
  print("-----------")
  tokens = sum(text_words.values())
  print("Text size:",str(tokens),
        "tokens in",str(len(text_words)),"types.")

  ## Saulo's requested default stats
  print("Number of hapax legomena:",len(hapax))      
  print("TTR (type-token ratio):",float(len(text_words))/float(tokens))
  print("HTR (hapax-token ratio):",float(len(hapax))/float(tokens))
  print("HTyR (hapax-type ratio):",float(len(hapax))/float(len(text_words)))

  if args.dicts:
    print("Neologisms: ",str(neolo), "types not found in",
          str(len(clean_dicts)),"dictionaries")
    print("Dictionaries contained",str(sum(dict_words.values())),
          "tokens in",str(len(dict_words)),"types.")


  if args.msttr:
    print("MSTTR...",end="")
    sys.stdout.flush()
    print(msttr(clean_text))
  if args.mltd:
    print("MLTD...",end="")
    sys.stdout.flush()
    print(mltd(clean_text))
  if args.hdd:
    print("HD-D...",end="")
    sys.stdout.flush()
    print(hdd(text_words))
  if args.wordlen:
    wordlen_dist(text_words)
  if args.wordtypes:
    print("\nWordtypes and frequencies (unigram model):")
    print("------------------------------------------")
    print("(Rank,Count,Wordform)")
    print("---------------------")
    for i,t in enumerate(sorted(text_words.items(), 
                                key=lambda x: (-x[1],x[0]))):
      print(i+1,t[1],t[0])
  if args.hapax:
    print("\nHapax legomena:")
    print("----------------")
    for w in sorted(hapax):
      print(w)
  if args.punc_ratio:
    print("\nPunctuation ratio:",punc_ratio(text_words))

if __name__ in  "__main__":
  main()
