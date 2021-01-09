#!/usr/bin/python
# -*- coding:utf-8 -*-
import io
import sys
import os
import datetime
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

WAIT_FOR_N_CANVAS_PAINTED = int(os.getenv("WAIT_FOR_N_CANVAS_PAINTED", "10"))
WAIT_FOR_N_SECONDS_GRAFANA_JAVASCRIPT = int(os.getenv("WAIT_FOR_N_SECONDS_GRAFANA_JAVASCRIPT", "0"))
WAIT_FOR_N_SECONDS_GRAFANA_HTTP = int(os.getenv("WAIT_FOR_N_SECONDS_GRAFANA_HTTP", "120"))
GRAFANA_URL = os.getenv("GRAFANA_URL")
DEBUG = os.getenv("DEBUG")
if DEBUG:
    WIDTH = 1304
    HEIGHT = 984
else:
    # allow local development
    import epd12in48b
    WIDTH = epd12in48b.EPD_WIDTH
    HEIGHT = epd12in48b.EPD_HEIGHT

import time

from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageColor
import PIL.ImageOps

from PIL import Image
import asyncio
import pyppeteer
from pyppeteer import launch

pyppeteer.DEBUG = True

async def main():
    while True:
        while True:
            start = datetime.datetime.now()

            failed = False

            if os.getenv("CHROMIUM_PATH"):
                browser = await launch(headless=True, executablePath=os.getenv("CHROMIUM_PATH"))
            else:
                browser = await launch(headless=True)

            print("Getting grafana image...")

            page = await browser.newPage()
            await page.goto(GRAFANA_URL, {'timeout': WAIT_FOR_N_SECONDS_GRAFANA_HTTP * 1000})
            await page.setViewport({'width': WIDTH, 'height': HEIGHT})

            canvii = 0
            attempts = 0
            if WAIT_FOR_N_SECONDS_GRAFANA_JAVASCRIPT:
                await asyncio.sleep(WAIT_FOR_N_SECONDS_GRAFANA_JAVASCRIPT)


            while canvii < WAIT_FOR_N_CANVAS_PAINTED:
                canvii = await page.evaluate("""() => {
                    try {
                        document.querySelector('.navbar').remove();
                        document.querySelector('.sidemenu').remove();
                    } catch {}
                    return document.querySelectorAll('canvas').length
                }""")

                print("evaluated")
                if WAIT_FOR_N_SECONDS_GRAFANA_JAVASCRIPT:
                    break
                else:
                    await asyncio.sleep(1)

                print(f"Loaded {canvii} of {WAIT_FOR_N_CANVAS_PAINTED} canvases")
                attempts += 1
                if attempts > 20:
                    failed = True
                    break

            screenshot = await page.screenshot({'path': 'example.png'})
            try:
                await browser.close()
            except Exception as e:
                print(e)

            if not failed:
                break

        print("Getting grafana image...done")

        if DEBUG:
            return

        Blackimage2 = Image.new("1", (WIDTH, HEIGHT), 255)
        image = Image.open("example.png")

        thresh = 40
        fn = lambda x : 0 if x > thresh else 255
        inverted_image = image.convert('L').point(fn, mode='1')

        print("Initializing display...")
        epd = epd12in48b.EPD()
        # Initialize library.
        epd.Init()
        print("Initializing display...done")

        # Clear epdlay.
        print("Clearing display...")
        epd.clear()
        print("Clearing display...done")

        print("Writing grafana image...")

        epd.display(inverted_image, Blackimage2)

        print("Writing grafana image...done")
        end = datetime.datetime.now()

        print(f"Total refresh duration: {end - start}")


asyncio.get_event_loop().run_until_complete(main())


