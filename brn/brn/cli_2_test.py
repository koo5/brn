#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

# testing python startup optimizations here. long story short: pyoxidizer or maybe cython.

#https://gregoryszorc.com/blog/2019/01/10/what-i%27ve-learned-about-optimizing-python/
#sheve off about 40ms from startup time, by running python with -S and managing sys.path yourself.
#import sys
#sys.path.append('/home/koom/brnkacka/brn/venv/lib/python3.8/site-packages/')

# https://pyoxidizer.readthedocs.io/en/latest/getting_started.html#getting-started
# https://gregoryszorc.com/blog/2018/12/18/distributing-standalone-python-applications/
# https://gregoryszorc.com/blog/2019/01/10/what-i%27ve-learned-about-optimizing-python/

# or just cython?

# see also https://coldfix.de/2017/02/25/slow-entrypoints/

from franz.openrdf.connect import ag_connect
