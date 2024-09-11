import numpy as np
import math

ZERO = 0.0000001
def separation_coefficient(dist: int):
    margin: float = 50
    if dist > margin:
        return 0
    else:
        aux = math.log(dist + 1) * 50000
        if aux == 0: aux = ZERO
        return 1 / aux
def main():
    for i in range(0,100,5):
        print(f'{i = } {separation_coefficient(i) = }')


if __name__ == '__main__':
    main()