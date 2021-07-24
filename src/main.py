#!/usr/bin/python3
import datetime
import os
import numpy as np
WAIT_FOR_N_CANVAS_PAINTED = int(os.getenv("WAIT_FOR_N_CANVAS_PAINTED", "10"))
WAIT_FOR_N_SECONDS_GRAFANA_JAVASCRIPT = int(os.getenv("WAIT_FOR_N_SECONDS_GRAFANA_JAVASCRIPT", "0"))
WAIT_FOR_N_SECONDS_GRAFANA_HTTP = int(os.getenv("WAIT_FOR_N_SECONDS_GRAFANA_HTTP", "120"))
GRAFANA_URL = os.getenv("GRAFANA_URL")
DEBUG = os.getenv("DEBUG")
if DEBUG:
    WIDTH = 1304
    HEIGHT = 984
else:
    import epd12in48b
    # allow local development
    WIDTH = epd12in48b.EPD_WIDTH
    HEIGHT = epd12in48b.EPD_HEIGHT

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


        image = Image.open("example.png")



        black_image = image.convert('RGB')

        r, g, b = black_image.split()

        total_x, total_y = r.size
        new_array = np.zeros((total_x, total_y)).astype('uint8')
        for y in range(total_y):
            for x in range(total_x):
                true_r = r.getpixel((x, y))
                true_g = g.getpixel((x, y))
                true_b = b.getpixel((x, y))

                # higher these go, the more faded it appears
                threshold = 80
                if true_r < threshold and true_g < threshold and true_b < threshold:
                    new_array[x][y] = 255

                if true_r > 100 and true_g < 100 and true_b < 100:
                    new_array[x][y] = 255

        black_image = Image.fromarray(new_array).transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)


        red_image = image.convert('RGB')

        r, g, b = red_image.split()

        total_x, total_y = r.size
        new_array = np.zeros((total_x, total_y)).astype('uint8')
        for y in range(total_y):
            for x in range(total_x):
                true_r = r.getpixel((x, y))
                true_g = g.getpixel((x, y))
                true_b = b.getpixel((x, y))
                new_array[x][y] = 255

                if true_r > 150 and true_g < 100 and true_b < 100:
                    new_array[x][y] = 0

        # Recombine back to RGB image
        red_image = Image.fromarray(new_array).transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)


        if DEBUG:
            red_image.save("red.png")
            black_image.save("black.png")
            return

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
        epd.display(black_image, red_image)

        print("Writing grafana image...done")
        end = datetime.datetime.now()

        print(f"Total refresh duration: {end - start}")


asyncio.get_event_loop().run_until_complete(main())
