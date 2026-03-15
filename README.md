# Discord Photo Frame

A simple [discord.py](https://discordpy.readthedocs.io/en/stable/) bot that listens for a reaction emoji on any messages with an image or tenor link, downloads and formats the image, then submits it to an attached e-ink display.

Uses [discord.py](https://discordpy.readthedocs.io/en/stable/) for bot stuff and [Inky](https://github.com/pimoroni/inky) for the e-ink interface. Intended to be run on a Raspberry Pi Zero 2 with an attached [Inky Impression](https://shop.pimoroni.com/products/inky-impression?variant=56039376912763), but should be easily adapted to any e-ink / computer setup. 

[[Falco Blog entry about this project](https://falcoblog.com/projects/discordframe/)