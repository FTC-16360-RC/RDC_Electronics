import Scorer
import keyboard

s = Scorer.Scorer()

print("scorer rEADY")

while True:
    new = s.pop_top()
    if new != "empty":
        print(new)