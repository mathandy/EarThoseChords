from musictools import *
d = Diatonic('C')
a = d.num2note(6)
bla = [d.interval(x,a,ascending=True) for x in range(2,20)]
bla2 = [x[1] for x in bla]
for y in [(x, n, int(n), d.note2num(n))  for x, n in enumerate(bla2)]:
    print y

from musictools import *
d = Diatonic('C')
a = d.num2note(6)
bla = [d.interval(x,a,ascending=False) for x in range(2,20)]
bla2 = [x[0] for x in bla]
for y in [(x, n, int(n), d.note2num(n))  for x, n in enumerate(bla2)]:
    print y