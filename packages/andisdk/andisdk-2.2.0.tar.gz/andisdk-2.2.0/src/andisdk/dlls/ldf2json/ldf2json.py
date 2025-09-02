# Copyright (c) Technica Engineering GmbH. All rights reserved.
import sys
import json
import ldfparser
import argparse
from lark import Lark

parser = argparse.ArgumentParser(description='Convert LDF file to JSON')
parser.add_argument('input', type=str, help='LDF file')
parser.add_argument('output', type=str, help='JSON file')

def parseLDFtoDict(path: str):
    try:
        return ldfparser.parseLDFtoDict(path)
    except UnicodeDecodeError:
        return ldfparser.parseLDFtoDict(path, encoding="latin-1")

if __name__ == "__main__":

    args = parser.parse_args()
    ldf = parseLDFtoDict(args.input)
    
    output = sys.stdout if args.output == '-' else open(args.output, 'w')
    
    print(json.dumps(ldf, indent=4), file=output)
