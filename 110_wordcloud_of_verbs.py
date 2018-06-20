#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import re
import shutil
import sys
import time

import nltk
lemmatizer = nltk.WordNetLemmatizer()

from wordcloud import WordCloud, STOPWORDS

import math
import random

reload(sys)
sys.setdefaultencoding("utf-8")



t_gm = time.gmtime()
t_ft = time.strftime("%Y%m%d", t_gm)
t_dt = time.strftime("%Y-%m-%d %H:%M:%S", t_gm)

int2str = "01234567890abcdef"


#####
# directry name, keyword
keywords = []
entrys = [["2010-2018","./rawdata/watchmaking_2010-2018.txt",keywords], ["2000-2009","./rawdata/watchmaking_2000-2009.txt",keywords], ["1990-1999","./rawdata/watchmaking_1990-1999.txt",keywords], ["1900-1989","./rawdata/watchmaking_1900-1989.txt",keywords]]
#####


# stopwords
stopwords = ["be", "have"]
stopwords.extend(STOPWORDS)

# output dir
output_dir = "output"
if not os.path.exists(output_dir):
	os.mkdir(output_dir)

# for TF/IGF (a mutant of TF/IDF)
wordlist = {}

# check all document
pattern = re.compile("[¥d¥.¥/¥']+")
for et in entrys:
	print et[0]
	wordlist.setdefault(et[0], [])

	tmp = ""
	line2s = []
	f = open(et[1], 'r')
	for line in f.readlines():
		line = line.rstrip()
		if line == "":
			line2s.append(tmp)
			tmp = ""
		else:
			tmp += " " + line

	for line in line2s:
		sentences = nltk.sent_tokenize(line)
		for sentence in sentences:
			sentence = sentence.lower()
			
			if len(et[2]) > 0:
				flag_kw = 0
				for keyword in et[2]:
					if keyword in sentence:
						flag_kw = 1
						break
				if flag_kw == 0:
					continue

			tokens = nltk.word_tokenize(sentence)
			tagged = nltk.pos_tag(tokens)
					
			for tag in tagged:
				if len(tag[0]) <= 2:
					continue
				if pattern.search(tag[0]):
					continue
				if tag[1][0].upper() == 'V':
					verb_origin = lemmatizer.lemmatize(tag[0], pos='v')
					wordlist[et[0]].append(verb_origin)

	f.close()


##################################################
# calculate TF/IGF (a mutant of TF/IDF)

### TF
# Occurences of one word in one group
n_tg = {}
# Occurences of all words in one group
sum_n_tg = {}

for et in entrys:
	n_tg.setdefault(et[0], {})
	sum_n_tg.setdefault(et[0], 0)
	for wd in wordlist[et[0]]:
		n_tg[et[0]].setdefault(wd, 0)
		n_tg[et[0]][wd] += 1
		sum_n_tg[et[0]] += 1

### IGF
# number of all groups
N = len(entrys)
# number of groups for one word
gf = {}
for et in entrys:
	for wd in set(wordlist[et[0]]):
		gf.setdefault(wd, 0)
		gf[wd] += 1

### TF/IGF
tfigf = {}
for et in entrys:
	tfigf.setdefault(et[0], {})
	for wd in set(wordlist[et[0]]):
		tfigf[et[0]][wd] = (float(n_tg[et[0]][wd])/sum_n_tg[et[0]]) * (math.log(N/float(gf[wd])))
#		tfigf[et[0]][wd] = (float(n_tg[et[0]][wd])/sum_n_tg[et[0]]) * (N/float(gf[wd]))


##################################################
# output, make wordcloud
for et in entrys:
	print et[0]
	text = ""
	words = []
	fw = open(output_dir+"/feature_verb_pairs_"+et[0]+".tsv", 'w')
	fw2 = open(output_dir+"/feature_verb_pairs_"+et[0]+".csv", 'w')
	for wd, val in sorted(tfigf[et[0]].items(), key=lambda x:x[1], reverse=True):
		fw.write(wd+"\t"+str(val)+"\t"+str(n_tg[et[0]][wd])+"\n")
		fw2.write(wd+","+str(val)+","+str(n_tg[et[0]][wd])+"\n")
		val2 = val * 10000
		print val, val2
		if val2 < 1:
			continue
		for i in xrange(int(val2)):
			words.append(wd)
	fw.close()
	fw2.close()

	random.shuffle(words)
	for wd in words:
		text += wd + " "
	text = text.strip()
	wordcloud = WordCloud(background_color='white',width=300,height=200,stopwords=set(stopwords)).generate(text)
	wordcloud.to_file(output_dir+"/wordcloud_verb_"+et[0]+".png")
