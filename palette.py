class Palette:
    def __init__(self):

        # Normal text (0)
        self.normal = '\033[0;00m'

        # Text styles (1, 3, 4, 7, 9, 21)
        self.bold = '\033[0;01m'
        self.italic = '\033[0;03m'
        self.underlined = '\033[0;04m'
        self.inverted = '\033[0;07m' # White background, black text
        self.crossed = '\033[0;09m'
        self.underlined_bold = '\033[0;21m'

        # Pale background colors (30–37)
        self.pale_black = '\033[0;30m'
        self.pale_red = '\033[0;31m'
        self.pale_green = '\033[0;32m'
        self.pale_yellow = '\033[0;33m'
        self.pale_blue = '\033[0;34m'
        self.pale_purple = '\033[0;35m'
        self.pale_cyan = '\033[0;36m'
        self.pale_gray = '\033[0;37m'

        # Pale background colors (40–47)
        self.pale_black_bg = '\033[0;40m'
        self.pale_red_bg = '\033[0;41m'
        self.pale_green_bg = '\033[0;42m'
        self.pale_yellow_bg = '\033[0;43m'
        self.pale_blue_bg = '\033[0;44m'
        self.pale_purple_bg = '\033[0;45m'
        self.pale_cyan_bg = '\033[0;46m'
        self.pale_gray_bg = '\033[0;47m'

        # Bright text colors (90–97)
        self.black = '\033[0;90m'
        self.red = '\033[0;91m'
        self.green = '\033[0;92m'
        self.yellow = '\033[0;93m'
        self.blue = '\033[0;94m'
        self.purple = '\033[0;95m'
        self.cyan = '\033[0;96m'
        self.white = '\033[0;97m'

        # Bright background colors (100–107)
        self.black_bg = '\033[0;100m'
        self.red_bg = '\033[0;101m'
        self.green_bg = '\033[0;102m'
        self.yellow_bg = '\033[0;103m'
        self.blue_bg = '\033[0;104m'
        self.purple_bg = '\033[0;105m'
        self.cyan_bg = '\033[0;106m'
        self.white_bg = '\033[0;107m'

        # Boxed (51-52)
        self.boxed = '\033[0;51m'
        self.boxed_alt = '\033[0;52m'


if __name__ == "__main__":
    for i in range(0, 108):
        if i < 10:
            print(f'\033[0;0{i}m', i, '. ' + "This is Elon Musk - Tesla cofounder and CEO.", sep='')
        else:
            print(f'\033[0;{i}m', i, '. ' + "This is Elon Musk - Tesla cofounder and CEO.", sep='')

"""
Bold - 1
Italic - 3
Underline - 4
White bg - 7
Crossed - 9
Boldly underlined - 21

Pale black - 30
Pale red - 31
Pale green - 32
Pale yellow - 33
Pale blue - 34
Pale purple - 35
Pale cyan - 36
Pale gray - 37

Pale black bg - 40
Pale red bg - 41
Pale green bg - 42
Pale yellow bg - 43
Pale blue bg - 44
Pale purple bg - 45
Pale cyan bg - 46
Pale gray bg - 47

Boxed - 51/52

Black - 90
Red - 91
Green - 92
Yellow - 93
Blue - 94
Purple - 95
Cyan - 96
White - 97

Black bg - 100
Red bg - 101
Green bg - 102
Yellow bg - 103
Blue bg - 104
Purple bg - 105
Cyan bg - 106
White bg - 107
"""