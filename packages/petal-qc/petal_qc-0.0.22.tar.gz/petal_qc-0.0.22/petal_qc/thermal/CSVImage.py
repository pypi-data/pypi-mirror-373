#!/usr/bin/env python3
"""Get Thenal Image from CSV file."""
import datetime
import sys

import matplotlib.pyplot as plt
import numpy as np


class CSVImage(object):
    """Read an image from CSV file."""

    def __init__(self, ifile):
        """Initialize."""
        config = open(ifile, "rb")
        in_data = False
        i = 0
        for line in config:
            if not in_data:
                if b'ImageWidth' in line:
                    ip = line.find(b'=')+1
                    self.width = int(line[ip:])

                elif b'ImageHeight' in line:
                    ip = line.find(b'=')+1
                    self.height = int(line[ip:])

                elif b'RecDate' in line:
                    recDate = line[line.find(b'=')+1:].strip()

                elif b'RecTime' in line:
                    recTime = line[line.find(b'=')+1:].strip()

                elif b'[Data]' in line:
                    recDate = recDate + b' ' + recTime
                    self.timestamp = datetime.datetime.strptime(recDate.decode('ascii'), "%d.%m.%Y %H:%M:%S", )
                    self.image = np.zeros([self.height, self.width])
                    in_data = True

            else:
                if len(line):
                    numbers = line.replace(b',', b'.').split(b';')
                    row = np.array([float(x) for x in numbers])
                    self.image[i, :] = row
                    i = i + 1

        self.image = np.flipud(self.image)

    def get_data(self):
        """Return the image."""
        return self.image


if __name__ == "__main__":
    try:
        fnam = sys.argv[1]
    except IndexError:
        print("I need an input file")
        # sys.exit()
        fnam = "/private/tmp/minus35.csv"

    img = CSVImage(fnam)
    print("{}x{}\n".format(img.width, img.height))
    fig = plt.figure(figsize=(img.width/128, img.height/128))
    fig.suptitle("CSVimage")
    plt.imshow(img.get_data(), origin='lower', cmap="jet")
    plt.colorbar()
    plt.tight_layout()
    plt.show()
