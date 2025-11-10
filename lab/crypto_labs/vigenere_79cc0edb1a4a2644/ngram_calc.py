from collections import Counter
from math import log
import json
from argparse import ArgumentParser


def get_ctr(txt, n):
    ctr = Counter("".join(x) for x in zip(*[txt[i:] for i in range(n)]))
    return ctr


def calc_ngram(txt, ns):
    ctrs = [get_ctr(txt, n) for n in ns]
    dt = {}
    for d in ctrs:
        dt |= d
    ln = sum([v for v in dt.values()])
    return {k: log(v / ln) for k, v in dt.items()}


if __name__ == "__main__":
    par = ArgumentParser()
    par.add_argument("-i", "--input", help="Input file", required=True)
    par.add_argument("-o", "--output", help="Output file", required=True)
    par.add_argument(
        "-n", "--ngrams", help="Ngram number", nargs="+", default=["1", "2", "3"]
    )
    parsed = par.parse_args()
    with open(parsed.input) as f:
        txt = f.read()
    ng = calc_ngram(txt, [int(x) for x in parsed.ngrams])
    with open(parsed.output, "w") as f:
        json.dump(ng, f)
