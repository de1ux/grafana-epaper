#!/usr/bin/python3
import datetime
import os
import sys
import numpy as np

WAIT_FOR_N_CANVAS_PAINTED = int(os.getenv("WAIT_FOR_N_CANVAS_PAINTED", "10"))
WAIT_FOR_N_SECONDS_GRAFANA_JAVASCRIPT = int(os.getenv("WAIT_FOR_N_SECONDS_GRAFANA_JAVASCRIPT", "0"))
WAIT_FOR_N_SECONDS_GRAFANA_HTTP = int(os.getenv("WAIT_FOR_N_SECONDS_GRAFANA_HTTP", "120"))
GRAFANA_URL = os.getenv("GRAFANA_URL")
DEBUG = os.getenv("DEBUG")
WIDTH = 1304
HEIGHT = 984

from PIL import Image
import asyncio
import pyppeteer
from pyppeteer import launch

pyppeteer.DEBUG = True


async def main():
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

    if failed:
        raise Exception()

    print("Getting grafana image...done")


    red_image = Image.new("1", (WIDTH, HEIGHT), 255)
    image = Image.open("example.png")

    thresh = 40
    fn = lambda x: 0 if x > thresh else 255
    fn_red = lambda x: 255 if 5 < x < 100 else 0

    black_image = image.convert('L').point(fn, mode='1')
    red_image = image.convert('RGB')

    # Split into 3 channels
    r, g, b = red_image.split()
    total_x, total_y = r.size
    print(total_x, total_y)
    new_array = np.zeros((total_x, total_y)).astype('uint8')
    for y in range(total_y):
        for x in range(total_x):
            try:
                true_r = r.getpixel((x, y))
                true_g = g.getpixel((x, y))
                true_b = b.getpixel((x, y))
                if 80 < true_r < 130 and 125 <true_g < 200 and 68 < true_b < 114:
                    new_array[x][y] = 0
                else:
                    new_array[x][y] = 255


    # Recombine back to RGB image
    green_image = Image.fromarray(new_array).transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)


    green_image.save('red.png')
    black_image.save('black.png')


asyncio.get_event_loop().run_until_complete(main())