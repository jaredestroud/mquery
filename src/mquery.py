#!/usr/bin/python3
from libs.libquery import MalQuery
import sys
import argparse

if __name__ == "__main__":
    print("[================[ >MQuery< ]==================]")
    parser = argparse.ArgumentParser()

    parser.add_argument("--provider", help="Specify provider \
            malshare, hba)", required=False, default="all")

    parser.add_argument("--hash", help="Specify hash (MD5, SHA128, SHA256)",
            required=False)

    parser.add_argument("--action", choices=['download','search','list','info'], 
            help="(download, lookup, list, info)", required=True)

    args = parser.parse_args()
    if (args.action == "search" or args.action == "download") and args.hash is None:
        print("\t[!] Search specified with no hash!\n")
        sys.exit(1)
    query = MalQuery(args.provider, args.action, args.hash)
