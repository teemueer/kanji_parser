import os
import re
import codecs
import sqlite3
import requests

def read_lines(filepath, encoding='euc-jp'):
    with codecs.open(filepath, 'r', encoding) as f:
        for line in f:
            if line.startswith('#'): continue
            yield line.rstrip()
            
def parse_jis():
    for line in read_lines('JIS0208.TXT'):
        sjis, jis, uni, name = line.split('\t')
        if "<CJK>" in name:
            sjis    = int(sjis, 16)
            jis     = int(jis, 16)
            uni     = int(uni, 16)
            euc     = jis + 0x8080
            ku, ten = divmod(jis - 0x2020, 0x100)
            
            sql = 'insert into codepoints values (?,?,?,?,?,?)'
            cur.execute(sql, (uni, sjis, jis, euc, ku, ten))

def parse_kanjidic():
    fields = {
        'B':    'radical',      # (nelson) radical
        'C':    'radical_c',    # classical radical - if nelson differs
        'G':    'grade',        # grade - 1~6 kyouiku, 8 jouyou, 9~10 jinmeiyou
        'H':    'halpern',      # New Japanese-English Character Dictionary
        'L':    'heisig',       # Remembering The Kanji
        'N':    'nelson',       # Modern Reader's Japanese-English Character Dictionary
        'E':    'henshall',     # A Guide To Remembering Japanese Characters
        'DN':   'heisig6',      # Remembering The Kanji, 6th Edition
        'DK':   'halpern_k',    # Kanji Learners Dictionary
        'DL':   'halpern_k2',   # Kanji Learners Dictionary, 2nd Edition
    }

    for line in read_lines('kanjidic', 'euc-jp'):
        segment_pattern = re.compile(r'[^ {]+|{.*?}', re.UNICODE)
        segments = segment_pattern.findall(line.rstrip())
        
        info = {
            'kanji':    segments[0],
            'uni':      ord(segments[0]),
        }

        meanings = re.findall(r'{(.*?)}', line)
        sql = 'insert into meanings (uni, meaning) values (?, ?)'
        for meaning in meanings:
            cur.execute(sql, (info['uni'], meaning))
        
        segments = segments[2:len(meanings)*-1]

        onyomi  = []
        kunyomi = []
        
        for seg in segments:
            code = seg[0]
            
            if 0x30a0 <= ord(code) <= 0x30ef:
                onyomi.append(seg)
            elif 0x3040 <= ord(code) <= 0x309f:
                kunyomi.append(seg)
            else:
                if code == 'D': code = seg[:2]
                key = fields.get(code, None)
                if key: info[key] = seg[len(code):]
        
        sql = 'insert into kanji (%s) values (%s)' % (','.join(info.keys()), ','.join(['?']*len(info.values())) )
        cur.execute(sql, info.values())
        
        sql = 'insert into onyomi (uni, onyomi) values (?, ?)'
        for on in onyomi:
            cur.execute(sql, (info['uni'], on))
            
        sql = 'insert into kunyomi (uni, kunyomi) values (?, ?)'
        for kun in kunyomi:
            cur.execute(sql, (info['uni'], kun))

def parse_kradfile():
    sql = 'update kanji set parts = ? where uni = ?'
    for line in read_lines('kradfile', 'euc-jp'):
        kanji, parts = line.split(' : ')
        cur.execute(sql, (parts.replace(' ', ''), ord(kanji)))
            
con = sqlite3.connect(filepath)
cur = con.cursor()
cur.executescript(open('tables.sql', 'r').read())

parse_jis()         
parse_kanjidic()
parse_kradfile()

con.commit()
con.close()