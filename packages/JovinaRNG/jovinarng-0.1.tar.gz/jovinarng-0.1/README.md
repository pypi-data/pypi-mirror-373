### Python package developed for use during course of "Programiranje i progrmski jezici"

## Classes : 
class JovinaRandom:
&emsp;def \_\_init\_\_(self, min:int, max:int):
&emsp;&emsp;self.min = min
&emsp;&emsp;self.max = max

## Class methods :
def generate_number(self)->int:
&emsp;return random.randint(self.min, self.max)

##Useage example :
    jr = JovinaRandom(3, 7)
    print(jr.generate_number())