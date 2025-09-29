#!/bin/python3
# MIT License
# 
# Copyright (c) 2025 Grayson Peddie
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy

import sys
import os
import re
import subprocess

def parse_objectclass(olc_str):
    # Remove newlines and extra spaces
    olc_str = ' '.join(olc_str.splitlines())

    # Extract NAME
    name_match = re.search(r"NAME\s+'([^']+)'", olc_str)
    name = name_match.group(1) if name_match else "Unknown"

    # Extract DESC    
    desc_match = re.search(r"DESC\s+'([^']+)'", olc_str)
    desc = desc_match.group(1) if desc_match else ""

    # Extract SUP
    sup_match = re.search(r"SUP\s+(\w+)", olc_str)
    sup = sup_match.group(1) if sup_match else ""

    must_match = re.search(r"MUST\s+\(([^)]+)\)", olc_str)
    must_attrs = []
    if must_match:
        must_attrs = [attr.strip().replace(' ','') for attr in must_match.group(1).split('$')]

    may_match = re.search(r"MAY\s+\(([^)]+)\)", olc_str)
    may_attrs = []
    if may_match:
        may_attrs = [attr.strip().replace(' ','') for attr in may_match.group(1).split('$')]

    # Print formatted output
    print(f"ObjectClass: {name}")
    if desc:
        print(f"Description: {desc}")
    if sup:
        print(f"Sup: {sup}")
    if must_attrs:
        print("MUST attributes:")
        for attr in must_attrs:
            print(f"  - {attr}")
    if may_attrs:
        print("MAY attributes:")
        for attr in may_attrs:
            print(f"  - {attr}")
    print()  # Blank line between entries

def main():
    # Make sure this script is running as a root user.
    if os.getuid() != 0:
        print("\n  Cannot list the available attributes for any given object class as a non-root user.\n")
        sys.exit(1)

    # Get all object classes from schema
    result = subprocess.check_output(
        'ldapsearch -Q -Y EXTERNAL -b "cn=schema,cn=config" -LLL "(olcObjectClasses=*)" olcObjectClasses | grep -v "dn:"',
        shell=True
    ).decode()

    # Split output into entries by blank line or "dn:" line
    entries = re.split(r'olcObjectClasses:\s', result)

    if len(sys.argv) < 2:
        scriptname = os.path.basename(sys.argv[0])
        print(f"Usage: {scriptname} <objectclass_name>")
        print("\nAvailable object classes: ")
        for entry in entries:
            entry = ''.join(entry.strip().splitlines())
            # Check if this object class matches the target name
            name_match = re.search(r"NAME\s+'([^']+)'", entry)
            name = name_match.group(1) if name_match else ''
            name = name.replace(' ','')
            if name.strip() != '':
                print("  - ", name)
        sys.exit(1)

    target_name = sys.argv[1]

    for entry in entries:
        # Check if this object class matches the target name
        entry = ''.join(entry.strip().splitlines())
        name_match = re.search(r"NAME\s+'([^']+)'", entry)
        name = name_match.group(1) if name_match else ''
        name = name.replace(' ','')
        if name and name.lower() == target_name.lower():
            parse_objectclass(entry)

if __name__ == "__main__":
    main()
