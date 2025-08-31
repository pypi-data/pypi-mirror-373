# example_usage.py
import random
import time
import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from loghtml import log, info, debug, warning, error, report_exception, config

log("teste")
log("novo log linha")
log('Outr 2')
log('Outr 3')
debug('Teste config', color='green')

log('Connection', color='yellow', tag='ping')
log('Outr 2')
log('Outr 3')
log('Connection', color='yellow', tag='ping')