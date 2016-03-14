__author__ = 'c60544'
import distutils
import shutil
import os

#
# base_path = str(os.path.dirname(os.path.realpath('__file__'))).replace("\\", "/")
#
# shutil.copytree(base_path+'/tempDir', '//hwvanad4071/data/AGO Open Data/log/run_2015-04-16_09-38/test/test')

tags = 'Note, Assisted, AssistedHousing, FHA, Multifamily, Insured, Multifamily, Minimum, b72c18ab-a68b-434e-b370-6dfc7dd113e6, b72c18ab-a68b-434e-b370-6dfc7dd113e6'

utag = tags.split()[-1]
lutag = tags.rfind(utag)-2
tags = tags[0:lutag]
print tags


#
# from nltk import word_tokenize, data
#
#
# sentence = "The Housing and Economic Recovery Act (HERA) of 2008 provided a first round of formula funding to States and units of general local government, and is referred to as NSP1. HUD awarded grants to a total of 309 grantees including the 55 states and territories and selected local governments to stabilize communities hardest hit by foreclosures and delinquencies."
#
# utagval = "8edf1d9c-4a1a-4e36-9efd-40e337b52079"
#
#
#
# sentence = sentence + '\n\nuTag: ' + utagval
#
# print sentence
#
# utagloc = sentence.find('uTag')
# cut = sentence[utagloc:utagloc+len(utagval)+6]
# print cut
# print utagloc
# print sentence.replace(cut,' ')
#
#
# sentence_break = data.load('tokenizers/punkt/english.pickle')
# # print sentence_break.tokenize(sentence.strip())[1]