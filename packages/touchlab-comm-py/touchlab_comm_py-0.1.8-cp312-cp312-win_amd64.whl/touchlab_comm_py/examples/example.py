#!/usr/bin/env python3

# Copyright (c) 2025 Touchlab Limited. All Rights Reserved
# Unauthorized copying or modifications of this file, via any medium is strictly prohibited.

import touchlab_comm_py as tl
import time
import argparse

def main():
    try:
        # Set up argument parser
        parser = argparse.ArgumentParser(description="Touchlab Sensor Example")
        parser.add_argument("port", type=str, help="Serial port to connect to")
        parser.add_argument("-p", "--parameter_file", type=str, help="Parameter file to load")
        args = parser.parse_args()
        if args.parameter_file is None:
            args.parameter_file = ""

        # Connect to the sensor
        com=tl.TouchlabComms()
        com.init(args.parameter_file)
        com.connect(args.port)

        # Set up frequency counting
        start = time.time()
        hz = 0.0
        count = 0
        while True:
            # Read data and print
            data = com.read()
            print(f"Rate: {hz:.1f}Hz, Triaxial Data: {data}")

            # Read raw data and print
            data_raw = com.read_raw(0)
            print(f"Rate: {hz:.1f}Hz, Raw Data: {data_raw}")

            # Calculate sensor update rate
            diff = float(time.time() - start)
            if diff > 0.5:
                hz = float(count) / diff
                count = 0
                start = time.time()
            count += 1
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
