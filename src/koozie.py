#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyfiglet",
# ]
# ///

import pyfiglet


def main() -> None:
    """Display 'koozie' in fun ASCII art format."""
    fig = pyfiglet.Figlet(font="banner")
    ascii_art = fig.renderText("koozie")
    print(ascii_art)


if __name__ == "__main__":
    main()
