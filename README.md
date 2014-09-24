neolo
=====

Text Analysis Software for Saulo Brandão.  Developed by Joshua Crowgey
in summer 2014.

```
usage: neolo [-h] [--dicts DICT [DICT ...]] [--mltd] [--msttr] [--hdd]
             [--verbose] [--wordlen] [--wordtypes] [--hapax]
             TEXT

Extract lexical statistics from a text file.

positional arguments:
  TEXT                  the text you want to investigate

optional arguments:
  -h, --help            show this help message and exit
  --dicts DICT [DICT ...]
                        a list of reference texts to compute neologism count
  --mltd                measure of lexical textual diversity
  --msttr               mean segmental type-token ratio
  --hdd                 HD-D probabilistic TTR
  --verbose, -v         increase the verbosty (can be repeated: -vvv)
  --wordlen, -w         print the distribution of words by length
  --wordtypes, -t       print the distribution of wordtypes (unigrams) by
                        count
  --hapax, -x           print the list of hapax legomena

Select one or more statistics via the above options.
```

Neologism Count
---------------
The name of this program reflects this original functionality.  Neologism
count is computed by referencing known wordlists or dictionaries.  Word types
found in the text under consideration which are not found in the reference 
dictionaries/wordlists are considered neologisms.

To show a simple example, suppose you have a text file called mary.txt 
which contains the following traditional poem:

```
Mary had a little lamb,
Her fleece was white as snow.
Everywhere that mary went,
the lamb was sure to go.
```

Supposing you're using the debian distro of GNU/Linux, there is a list of 
English words stored in /usr/share/dict/words that you can use as a 
reference.  You can ask neolo to check mary.txt for neologisms using 
the --dicts option.  The --dicts option takes a list of one ore more filenames
to use as references in calculating neologisms.

```
user@computer:~/src/neolo$ ./neolo texts/mary.txt --dicts /usr/share/dict/words
Opening texts/mary.txt with encoding:  utf-8 
Tokenizing, downcasing, stemming text: texts/mary.txt ... done.
Counting and sorting words in text: texts/mary.txt ...done.
Opening /usr/share/dict/words with encoding:  utf-8 
Tokenizing, downcasing, stemming dict files: ['/usr/share/dict/words'] ... done.
Counting and sorting words in dictonaries: ['/usr/share/dict/words'] ...done.
Neologism list:

Statistics:
-----------
Text size: 21 tokens in 18 types.
Number of hapax legomena: 15
TTR (type-token ratio): 0.8571428571428571
HTR (hapax-token ratio): 0.7142857142857143
HTyR (hapax-type ratio): 0.8333333333333334
Neologisms:  0 types not found in 1 dictionaries
Dictionaries contained 234937 tokens in 233615 types.
```

As you can see, there are no words in mary.txt which aren't in the reference
wordlist file, so neolo says "Neolgisms: 0 types not found in 1 dictionaries".

However, if you edit mary.txt such that instead of fleece, the poem's second
line says ``Her pleece was white as snow.'', now neolo prints a neologism list
along with its regular output.

```
user@computer:~/src/neolo$ ./neolo texts/mary.txt --dicts /usr/share/dict/words
Opening texts/mary.txt with encoding:  utf-8 
Tokenizing, downcasing, stemming text: texts/mary.txt ... done.
Counting and sorting words in text: texts/mary.txt ...done.
Opening /usr/share/dict/words with encoding:  utf-8 
Tokenizing, downcasing, stemming dict files: ['/usr/share/dict/words'] ... done.
Counting and sorting words in dictonaries: ['/usr/share/dict/words'] ...done.
Neologism list:
pleece

Statistics:
-----------
Text size: 21 tokens in 18 types.
Number of hapax legomena: 15
TTR (type-token ratio): 0.8571428571428571
HTR (hapax-token ratio): 0.7142857142857143
HTyR (hapax-type ratio): 0.8333333333333334
Neologisms:  1 types not found in 1 dictionaries
Dictionaries contained 234937 tokens in 233615 types.
```

MLTD
----

MSTTR
-----

HD-D
----
