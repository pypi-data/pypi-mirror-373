__version__ = "1.2.0"
__author__ = "Temal"

import subprocess
import argparse
from typing import Optional, List

output = b""

try:
    output = subprocess.check_output(["powercfg", "-getactivescheme"])
except Exception as error:
    print(error)

if b"a1841308-3541-4fab-bc81-f71556f20b4a" in output:
    current_powerplan_guid = "a1841308-3541-4fab-bc81-f71556f20b4a"
    current_powerplan_name = "Power saver"
    gotten = True

elif b"381b4222-f694-41f0-9685-ff5bb260df2e" in output:
    current_powerplan_guid = "381b4222-f694-41f0-9685-ff5bb260df2e"
    current_powerplan_name = "Balanced"
    gotten = True

elif b"8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c" in output:
    current_powerplan_guid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
    current_powerplan_name = "High performance"
    gotten = True

elif b"e9a42b02-d5df-448d-aa00-03f14749eb61" in output:
    current_powerplan_guid = "e9a42b02-d5df-448d-aa00-03f14749eb61"
    current_powerplan_name = "Ultimate performance"
    gotten = True

elif b"Ult" in output:
    current_powerplan_guid = "e9a42b02-d5df-448d-aa00-03f14749eb61"
    current_powerplan_name = "Ultimate performance"
    gotten = True

elif b"11111111-1111-1111-1111-111111111111" in output:
    current_powerplan_guid = "11111111-1111-1111-1111-111111111111"
    current_powerplan_name = "Atlas Power Scheme"

else:
    gotten = False
    current_powerplan_guid = "UNKNOWN"
    current_powerplan_name = "UNKNOWN"


def get_current_scheme_guid():
    return current_powerplan_guid


def get_current_scheme_name():
    return current_powerplan_name


def change_current_scheme_to_powersaver():
    try:
        subprocess.call("powercfg /s a1841308-3541-4fab-bc81-f71556f20b4a")
        return True
    except Exception as error:
        print(error)
        return False


def change_current_scheme_to_balanced():
    try:
        subprocess.call("powercfg /s 381b4222-f694-41f0-9685-ff5bb260df2e")
        return True
    except Exception as error:
        print(error)
        return False


def change_current_scheme_to_high():
    try:
        subprocess.call("powercfg /s 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c")
        return True
    except Exception as error:
        print(error)
        return False


def main(argv: Optional[List[str]] = None) -> int:
    """
    CLI entry point.
    Default (no args): print current scheme name.
    -g/--guid: print current scheme GUID.
    -n/--name: print current scheme name (explicit).
    """
    parser = argparse.ArgumentParser(
        prog="powerplan",
        description="Get current Windows power plan name or GUID and switch between standard plans.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-g", "--guid", action="store_true", help="Print the GUID of the current power plan")
    group.add_argument("-n", "--name", action="store_true", help="Print the name of the current power plan (default)")

    args = parser.parse_args(argv)

    if args.guid:
        print(get_current_scheme_guid())
    else:
        print(get_current_scheme_name())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())