"""Render a 1080x1080 post image from an HTML file.

Usage: python3 render.py input.html output.png
"""
import os
import sys

from playwright.sync_api import sync_playwright


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("usage: python3 render.py input.html output.png")
    src, out = os.path.abspath(sys.argv[1]), sys.argv[2]
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        page.goto("file://" + src)
        page.wait_for_timeout(400)
        page.screenshot(path=out)
        browser.close()
    print(out)


if __name__ == "__main__":
    main()
