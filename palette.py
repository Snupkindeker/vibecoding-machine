class Palette:
    def __init__(self):
        pass


if __name__ == "__main__":
    for i in range(0, 1000):
        if i < 10:
            print(f'\033[0;0{i}m', i, '. ' + "Python", sep='')
        else:
            print(f'\033[0;{i}m', i, '. ' + "Python", sep='')

'''
Bold - 1
Italic - 3
Underline - 4
White bg - 7
Crossed - 9
Boldly underlined - 21

Black - 30
Red - 31
Green - 32
Gold - 33
Blue - 34
Purple - 35
Cyan - 36
Gray - 37

Black bg - 40
Red bg - 41
Green bg - 42
Gold bg - 43
Blue bg - 44
Purple bg - 45
Cyan bg - 46
Gray bg - 47

Boxed - 51/52

Bright black - 90
Bright red - 91
Bright green - 92
Bright yellow - 93
Bright blue - 94
Bright purple - 95
Bright cyan - 96
Bright white - 97

Bright black bg - 100
Bright red bg - 101
Bright green bg - 102
Bright yellow bg - 103
Bright blue bg - 104
Bright purple bg - 105
Bright cyan bg - 106
Bright white bg - 107
'''