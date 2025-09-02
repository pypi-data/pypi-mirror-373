"""
A tool to quickly generate software license files with customizable project details
"""

import appdirs
import argparse
import datetime
import os
import pathlib
import sys

import requests


CACHE_DIR = appdirs.user_cache_dir("getlicense")
DEFAULT_COPYRIGHT_HOLDER_NAME = str(pathlib.Path("~").expanduser().name)
DEFAULT_PROJECT_NAME = str(pathlib.Path(os.getcwd()).name)
DEFAULT_COPYRIGHT_YEAR = str(datetime.datetime.now().year)


argparser = argparse.ArgumentParser(
    prog="getlicense",
    description="A tool to quickly generate software license files with customizable project details",
)

argparser.add_argument(
    "license_name",
    nargs="?",
    default=None,
    help="Name of license template to fetch (e.g., mit, gpl3 and etc.)",
)
argparser.add_argument(
    "--individual",
    help="The name of the individual who holds the copyright to the software",
)
argparser.add_argument(
    "-L",
    "--list-cached-templates",
    action="store_true",
    help="List cached license templates",
)
argparser.add_argument(
    "-l",
    "--list-templates",
    action="store_true",
    help="List available license templates",
)
argparser.add_argument(
    "-n",
    "--no-cache",
    action="store_true",
    help="Don't cache the license template file when downloaded",
)
argparser.add_argument(
    "-c",
    "--offline",
    action="store_true",
    help="Get the cached license template instead of downloading",
)
argparser.add_argument(
    "--organization",
    help="The name of the organization that holds the copyright to the software",
)
argparser.add_argument(
    "-o",
    "--output",
    default="LICENSE",
    help="Where to write the license template content to",
)
argparser.add_argument(
    "--project",
    help="The name of the software project",
)
argparser.add_argument(
    "--year",
    help="The year of the software's copyright",
)


def getlicense() -> None:
    """
    A tool to quickly generate software license files with customizable project details
    """

    args = argparser.parse_args()

    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    if args.list_templates:
        repository_contents = requests.get(
            "https://api.github.com/repos/licenses/license-templates/contents/templates"
        ).json()
        available_templates = [item["name"] for item in repository_contents]

        print("Available license templates:")
        print(", ".join(available_templates), end="\n\n")

    if args.list_cached_templates:
        cached_templates = [
            item
            for item in os.listdir(CACHE_DIR)
            if item.endswith(".licenseit.txt")
            and os.path.isfile(os.path.join(CACHE_DIR, item))
        ]

        print("Cached license templates:")
        print(", ".join(cached_templates), end="\n\n")

    if args.list_templates or args.list_cached_templates:
        return

    license_name = args.license_name

    content_to_write = ""

    if license_name is None:
        print("Nothing happened!")
        return

    path_to_cache_file = os.path.join(CACHE_DIR, f"{license_name}.getlicense.txt")

    if args.offline:
        if not os.path.isfile(path_to_cache_file):
            print(f"Couldn't find the {license_name!r} license template! (offline)")
            args.offline = False

        if args.offline:
            with open(path_to_cache_file) as cache_file:
                content_to_write = cache_file.read()
            print(f"Got the {license_name!r} license template!")

    if not args.offline:
        getlicense_request = requests.get(
            f"https://raw.githubusercontent.com/licenses/license-templates/master/templates/{license_name}.txt"
        )

        if getlicense_request.status_code >= 400:
            print(
                f"Error {getlicense_request.status_code}, Couldn't get the {license_name!r} license template!",
                file=sys.stderr,
            )
            return

        content_to_write = getlicense_request.text
        print(f"Got the {license_name!r} license template!")

        if not args.no_cache:
            with open(path_to_cache_file, "w") as cache_file:
                cache_file.write(getlicense_request.text)
            print(
                f"Cached the {license_name!r} license template at {path_to_cache_file!r}!"
            )

    did_output_file_exist = os.path.exists(args.output)

    copyright_holder = args.organization or args.individual
    if not copyright_holder:
        copyright_holder = input(
            f"Who holds the copyright to the software? ({DEFAULT_COPYRIGHT_HOLDER_NAME}) "
        )
        copyright_holder = (
            copyright_holder if copyright_holder.strip() else DEFAULT_COPYRIGHT_HOLDER_NAME
        )

    content_to_write = content_to_write.replace("{{ organization }}", copyright_holder)

    project = args.project
    if not project:
        project = input(
            f"What is name of the software project? ({DEFAULT_PROJECT_NAME}) "
        )
        project = project if project.strip() else DEFAULT_PROJECT_NAME

    content_to_write = content_to_write.replace("{{ project }}", project)

    year = args.year
    if not year:
        year = input(
            f"What is the copyright year of your software? ({DEFAULT_COPYRIGHT_YEAR}) "
        )
        year = year if year.strip() else DEFAULT_COPYRIGHT_YEAR

    content_to_write = content_to_write.replace("{{ year }}", year)

    with open(args.output, "w") as output_file:
        output_file.write(content_to_write)

    if not did_output_file_exist:
        print("Created the license file!")

    else:
        print("Overwrote the license file!")


if __name__ == "__main__":
    getlicense()
