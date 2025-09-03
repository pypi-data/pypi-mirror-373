from pasgen.core import pasgen
debug = pasgen(length=12,puncChars=True,lowerCase=False,ROT47=False,upperCase=False,ROT13=False,Base64=False)

#Keyword : test
#ROT47
""" ROT_47_TEST = debug._ROT47_ENCODE()
assert (ROT_47_TEST == "E6DE")

#ROT13 
ROT_13_TEST = debug._ROT13_ENCODE()
assert (ROT_13_TEST == "grfg/")
 """
print(debug.Generate)