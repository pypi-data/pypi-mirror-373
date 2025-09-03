import string
import random
import base64
from pasgen.pexceptions import PasgenExceptions

class pasgen:
    
    """
    Fast Password Generator
    
    """
    def __init__(self,length=7,puncChars=False,lowerCase=True,upperCase=True,Base64=False,ROT13=False,ROT47=False):
        self.puncChars = puncChars
        self.length = length
        self.loweCase = lowerCase
        self.upperCase = upperCase
        self.Base64 = Base64 
        self.ROT13 = ROT13
        self.ROT47 = ROT47
    @property
    def Generate(self):
       
        the_pass = []
        for _ in range(self.length):
            random_for_mix = random.randint(0, 2)
            if self.puncChars and random_for_mix == 0:
                rdm = random.randrange(0,len(string.punctuation))
                the_pass.append(string.punctuation[rdm])
                
            elif self.loweCase and random_for_mix == 1:
                rdm = random.randrange(0,len(string.ascii_lowercase))
                the_pass.append(string.ascii_lowercase[rdm])
                    
            elif self.upperCase and random_for_mix == 2:
                rdm = random.randrange(0,len(string.ascii_uppercase))
                the_pass.append(string.ascii_uppercase[rdm])
            
            else:
                rdm = random.randrange(0,len(string.digits))
                the_pass.append(string.digits[rdm])
       
        password = ''.join(the_pass) 
        if  self.ROT13:
            password =  self._ROT13_ENCODE(password)
        if  self.ROT47:
            password = self._ROT47_ENCODE(password)
        if  self.Base64:
            password =  self._BASE64_ENCODE(password)    
        return password
    
    def _ROT47_ENCODE(self,pswd):
        """
        ROT47 DECODE ALGORITHM
        """
        x = []
        for i in range(len(pswd)):
            j = ord(pswd[i])
            if j >= 33 and j <= 126:
                x.append(chr(33 + ((j + 14) % 94)))
            else:
                x.append(pswd[i])
        
        return ''.join(x)
   
    def _ROT13_ENCODE(self,pswd):
        """
        ROT13
        """
        x = []
        for i in range(len(pswd)):
            j = ord(pswd[i])
            if j >= 65 and j< 78:
                x.append(chr(j+13))
            elif j >= 78 and j <= 90:
                x.append(chr(j-13))
            elif j >= 97 and j < 110:
                x.append(chr(j+13))
            elif j >= 110 and j <= 122:
                x.append(chr(j-13))
            else:
                x.append(pswd[i])
        
        return ''.join(x)
    
    def _BASE64_ENCODE(self,psdw):
        sample_string = psdw
        sample_string_bytes = sample_string.encode("ascii") 
        base64_bytes = base64.b64encode(sample_string_bytes) 
        base64_string = base64_bytes.decode("ascii") 
        return(base64_string)