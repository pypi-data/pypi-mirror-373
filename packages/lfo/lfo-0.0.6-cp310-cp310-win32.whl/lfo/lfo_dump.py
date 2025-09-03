#!/usr/bin/env python3

import argparse
import sys

from time import sleep

from lfo import LFO

def main():
    cmdline = argparse.ArgumentParser(description='Test the LFO module...')
    cmdline.add_argument('-p', '--period', type=float, default=1, help="Set period of the LFO")
    cmdline.add_argument('-w', '--pulsewidth', type=float, default=0.5, help="Pulse width of the square wave")
    cmdline.add_argument('-d', '--delay', type=float, default=0.25, help="Delay between calls")
    opts = cmdline.parse_args(sys.argv[1:])

    l = LFO(opts.period, pw=opts.pulsewidth)
    while True:
        print(f'{l.t=:12.8}  {l.normalized=:12.8}  {l.sine=:12.8}  {l.triangle=:12.8}  {l.sawtooth=:12.8}  {l.square=:12.8} {l.pw=}')
        sleep(opts.delay)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
