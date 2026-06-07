#!/usr/bin/env python3
"""Rewrite numerals in text as spoken words for TTS. No dependencies."""
import re, sys

ONES = ["zero","one","two","three","four","five","six","seven","eight","nine",
        "ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen",
        "seventeen","eighteen","nineteen"]
TENS = ["","","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]
SCALES = [(1_000_000_000,"billion"),(1_000_000,"million"),(1_000,"thousand")]

def under_thousand(n):
    out = []
    if n >= 100:
        out.append(ONES[n//100]); out.append("hundred"); n %= 100
    if n >= 20:
        t = TENS[n//10]; o = n%10
        out.append(f"{t}-{ONES[o]}" if o else t)
    elif n > 0:
        out.append(ONES[n])
    return out

def spell_int(n):
    if n == 0: return "zero"
    words = []
    for value, name in SCALES:
        if n >= value:
            words += under_thousand(n//value) + [name]; n %= value
    words += under_thousand(n)
    return " ".join(words)

def spell_number(num_str):
    num_str = num_str.replace(",", "")
    if "." in num_str:
        whole, frac = num_str.split(".", 1)
        w = spell_int(int(whole)) if whole else "zero"
        digits = " ".join(ONES[int(d)] for d in frac)
        return f"{w} point {digits}"
    return spell_int(int(num_str))

SUFFIX = {"k":"thousand","m":"million","b":"billion"}

def convert(text):
    # 47k / 4.5M
    def suf(m):
        return f"{spell_number(m.group(1))} {SUFFIX[m.group(2).lower()]}"
    text = re.sub(r'(\d[\d,]*\.?\d*)\s*([kKmMbB])\b', suf, text)
    # 91% -> ninety-one percent
    text = re.sub(r'(\d[\d,]*\.?\d*)\s*%', lambda m: f"{spell_number(m.group(1))} percent", text)
    # bare numbers
    text = re.sub(r'\d[\d,]*\.?\d*', lambda m: spell_number(m.group(0)), text)
    return text

if __name__ == "__main__":
    src = " ".join(sys.argv[1:]) or sys.stdin.read()
    print(convert(src))
