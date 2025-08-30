"""
from mypackage import module1 as MP
# module1 has two functions, hello() and another()

print("module1 >%s<" % MP)
MP.hello()
MP.another()


rd = __import__("rfc_draw")
print("rd >%s<" % rd)

#import rfc_draw as RD

#help(rd)  # prints PACKAGE CONTENTS, which has RFC_Draw

rd.RFC_Draw() # fails, module 'rfc_draw' has no attribute 'RFC_Draw'

import rfc_draw as RD  # This doesn't work
RD.RFC_Draw()
"""

import rfc_draw  # This does work
  # it loads and executes RFC_Draw(), as above :-)



