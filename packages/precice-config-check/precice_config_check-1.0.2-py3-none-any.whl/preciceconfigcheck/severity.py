from enum import Enum

import preciceconfigcheck.color as c


# Colors: 0: gray, 1: red, 2: green, 3: yellow, 4: blue, 5: magenta, 6: cyan, 7: white
class Severity(Enum):
    DEBUG = c.dyeing("DEBUG", c.blue)
    WARNING = c.dyeing("WARNING", c.yellow)
    ERROR = c.dyeing("ERROR", c.red)
