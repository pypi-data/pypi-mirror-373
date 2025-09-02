from .findings import stats, summary, cves
from . import eprint
import argparse
import traceback
import sys
import os
from blackduck.HubRestApi import HubInstance

def cli():
    """
    Parse parameters from cli and invoke report function
    """
    parser = argparse.ArgumentParser(
        description="""Report the offending libraries from a given project+version in a short format suitable for notifications. 
        Note blackduck connection depends on a .restconfig.json file which must be present in the current directory. It's format is: 

        {
        "baseurl": "https://foo.blackduck.xyz.com",
        "api_token": "YOUR_TOKEN_HERE",
        "insecure": false,
        "debug": false
        }

"""
    )
    parser.add_argument("project_name")
    parser.add_argument("version_name")
    parser.set_defaults(operational=False)
    parser.add_argument(
        "-c",
        "--cutoff",
        default="high",
        choices=["medium", "high", "critical", "low"],
        help="Minimum level of risk to report",
    )
    parser.add_argument(
        "-f",
        "--format",
        default="SHORT",
        choices=["SHORT", "PANDAS", "CSV", "JSON", "HTML"],
        help="Report format",
    )
    parser.add_argument(
        "--tree",
        dest="tree",
        action="store_true",
        help="Print tree of subprojects as stats are being gathered. POSIX exit codes for OK, DATA_ERR, CONFIG (0,65,78). ",
    )
    parser.set_defaults(tree=False)
    parser.add_argument(
        "--experimental",
        dest="experimental",
        action="store_true",
        help="make a flat request (non-recursive) to vulnerable_sbom endpoint",
    )
    parser.set_defaults(experimental=False)

    parser.add_argument(
        "--urls",
        dest="urls",
        action="store_true",
        help="Print url of offending components as part of output",
    )
    parser.set_defaults(urls=False)

    args = parser.parse_args()
    headers = {
        "c": "Component",
        "v": "Version",
        "critical": "Critical Security Risk",
        "high": "High Security Risk",
        "medium": "Medium Security Risk",
        "low": "Low Security Risk",
        "os": "Operational Risk",
    }

    try:
        hub = HubInstance()
    except Exception as e: 
        eprint("cant create hub instance. Check .restconfig.json file")
        eprint(e)
    
    df = None
    tree = 0 if args.tree else -1

    try:
        if args.experimental:
            return print(cves(args.project_name, args.version_name))

        df = stats(
            args.project_name,
            args.version_name,
            args.operational,
            args.cutoff,
            headers,
            tree,
            args.experimental
        )
    except NameError as e:
        eprint(e)
        sys.exit(os.EX_DATAERR)
    except Exception as e:
        if str(e) == "'bearerToken'":
            eprint(
                "Invalid Authorization Token. Check contents of .restconfig.json. Try --help for more information"
            )
        traceback.print_exc()
        sys.exit(os.EX_CONFIG)

    summary(df, args.cutoff, headers, args.format, args.urls)
    sys.exit(os.EX_OK)

if __name__ == "__main__":
    cli()
