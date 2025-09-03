import random

class JovinaRandom:
    def __init__(self, min:int, max:int):
        self.min = min
        self.max = max
    
    def generate_number(self)->int:
        return random.randint(self.min, self.max)

if __name__ == '__main__':
    jr = JovinaRandom(3, 7)
    print(jr.generate_number())