#############################################################################
## Thx you Mhite & Minsuk for providing wonderful script to build my project.
## matt hite (mhite@hotmail.com)
## Minsuk Song <msuk.song@gmail.com>
#############################################################################
##
from __future__ import print_function

import sys
import argparse
import random



#################################################################
## globals
MAGIC = "$9$"
###################################
## letter families
FAMILY = ["QzF3n6/9CAtpu0O", "B1IREhcSyrleKvMW8LXx", "7N-dVbwsY2g4oaJZGUDj", "iHkq.mPf5T"]
EXTRA = dict()
for x, item in enumerate(FAMILY):
    for c in item:
        EXTRA[c] = 3 - x
###################################
## forward and reverse dictionaries
NUM_ALPHA = [x for x in "".join(FAMILY)]
ALPHA_NUM = {NUM_ALPHA[x]: x for x in range(0, len(NUM_ALPHA))}
###################################
## encoding moduli by position
ENCODING = [[1, 4, 32], [1, 16, 32], [1, 8, 32], [1, 64], [1, 32], [1, 4, 16, 128], [1, 32, 64]]


def _nibble(cref, length):
    nib = cref[0:length]
    rest = cref[length:]
    if len(nib) != length:
        print("[-] Ran out of characters: hit '%s', expecting %s chars" % (nib, length))
        sys.exit(1)
    return nib, rest

def _gap(c1, c2):
    return (ALPHA_NUM[str(c2)] - ALPHA_NUM[str(c1)]) % (len(NUM_ALPHA)) - 1

def _gap_decode(gaps, dec):
    num = 0
    if len(gaps) != len(dec):
        print("[-] Nibble and decode size not the same!")
        sys.exit(1)
    for x in range(0, len(gaps)):
        num += gaps[x] * dec[x]
    return chr(num % 256)

def juniper_decrypt(crypt):
    """Juniper $9$ password decryptor
    """
    try:
        chars = crypt.split("$9$", 1)[1]
    except:
        return crypt
    first, chars = _nibble(chars, 1)
    toss, chars = _nibble(chars, EXTRA[first])
    prev = first
    decrypt = ""
    while chars:
        decode = ENCODING[len(decrypt) % len(ENCODING)]
        nibble, chars = _nibble(chars, len(decode))
        gaps = []
        for i in nibble:
            g = _gap(prev, i)
            prev = i
            gaps += [g]
        decrypt += _gap_decode(gaps, decode)
    return decrypt

def _reverse(my_list):
    new_list = list(my_list)
    new_list.reverse()
    return new_list

def _gap_encode(pc, prev, encode):
    _ord = ord(pc)

    crypt = ''
    gaps = []
    for mod in _reverse(encode):
        gaps.insert(0, int(_ord/mod))
        _ord %= mod

    for gap in gaps:
        gap += ALPHA_NUM[prev] + 1
        prev = NUM_ALPHA[gap % len(NUM_ALPHA)]
        crypt += prev

    return crypt

def _randc(cnt = 0):
    ret = ""
    for _ in range(cnt):
        ret += NUM_ALPHA[random.randrange(len(NUM_ALPHA))]
    return ret

def juniper_encrypt(plaintext, salt = None):
    """Juniper $9$ password encryptor
    """
    if salt is None:
        salt = _randc(1)
    rand = _randc(EXTRA[salt])

    pos = 0
    prev = salt
    crypt = MAGIC + salt + rand

    for x in plaintext:
        encode = ENCODING[pos % len(ENCODING)]
        crypt += _gap_encode(x, prev, encode)
        prev = crypt[-1]
        pos += 1

    return crypt



def _update_pw_line(line, pw_masking):
    if line.rstrip().endswith("## SECRET-DATA"):
        spl = line.split('"')
        if len(spl)<=1: return line
        pw = spl[1]
        #
        if pw.startswith("$9$"):
            if pw_masking:
                spl[1] = f"{'X'*9}"
            else:
                spl[1] = juniper_decrypt(pw)
        line = '"'.join(spl)
    return line


def _file_passwords_update(input_file, output_file, pw_masking):
    with open(input_file, 'r') as f:
        lst = f.readlines()
    ulist = (_update_pw_line(line, pw_masking) for line in lst)
    cfg = "".join(ulist)
    with open(output_file, 'w') as f:
        f.write(cfg)


def decrypt_doller9_file_passwords(input_file, output_file):
    """Decrypts all $9$ passwords found in input file, and create a new updated output file
    with plain text passwords

    Args:
        input_file (str): juniper configuration file name
        output_file (str): output file name
    """
    _file_passwords_update(input_file, output_file, False)


def mask_doller9_file_passwords(input_file, output_file):
    """Masks all $9$ passwords found in juniper configuration input file,
    and creates a new updated output file with plain masked passwords

    Args:
        input_file (str): juniper configuration file name
        output_file (str): output file name
    """

    _file_passwords_update(input_file, output_file, True)

if __name__ == "__main__":
    pass
