import re

keyword = re.compile('^([\x21-\x7e]+)$')
production = re.compile('<(?P<rule>[a-zA-Z_0-9])>\s*::=\s*(?:(?:(?:[a-zA-Z_0-9])<(?:[a-zA-Z_0-9])>|(?:[a-zA-Z_0-9\?]))\s*(?:\||$))+')
terminal = re.compile('[a-zA-Z_0-9\?](?=\||$)')
tnt_terminal = re.compile('[a-zA-Z_0-9\?](?=<)')
tnt_nonterminal = re.compile('<([a-zA-Z_0-9\?]+)>')
blank_line = re.compile('^\s*$')
