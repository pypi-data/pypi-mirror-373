#!/usr/bin/env python3
"""A python port of https://github.com/jonathanschilling/irb.

This is in turn inspired by https://github.com/tomsoftware/Irbis-File-Format.

Do not expect 'optimized' python code. The java one was not neither...
"""
import bz2
import copy
import datetime
import os
import pickle
import struct
import sys
from argparse import ArgumentParser
from collections.abc import Iterable
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OLE_TIME_ZERO = datetime.datetime(1899, 12, 30, 0, 0, 0)


def ole2datetime(oledt):
    """Convert OLE_TIME to python datetime."""
    return OLE_TIME_ZERO + datetime.timedelta(days=float(oledt))


def is_iterable(obj):
    """Tell if an object is iterable. Strings are not considered iterables."""
    if isinstance(obj, Iterable):
        if isinstance(obj, str) or isinstance(obj, bytes):
            return False
        else:
            return True
    else:
        return False


class BinaryFile(object):
    """Encapsulates a binary file."""

    def __init__(self, ifile):
        """Initialize from a file-like object."""
        self.ifile = ifile

        # Figure out the file size.
        old_pos = self.ifile.tell()
        self.ifile.seek(0, os.SEEK_END)
        self.end = self.ifile.tell()
        self.ifile.seek(old_pos)

    def get_from_file(self, fmt, offset=-1):
        """Get data from a binary file.

        Args:
        ----
            fmt: The format (see struct)
            offset (int, optional): THe offset in the file.
                                    Defaults to -1, which ignores the offset.

        Return:
        ------
            array: The output data

        """
        if offset > 0:
            self.ifile.seek(offset)

        sz = struct.calcsize(fmt)
        dt = self.ifile.read(sz)
        return struct.unpack(fmt, dt)

    def read(self, n):
        """Read bytes from file."""
        return self.ifile.read(n)

    def seek(self, pos=0, whence=os.SEEK_SET):
        """Delegate teh seek functionality."""
        return self.ifile.seek(pos, whence)

    def tell(self):
        """Delegate the tell funcionality."""
        return self.ifile.tell()

    def __getValue(self, n, offset, fmt1, fmt2):
        """Get values from file."""
        if n == 1:
            return self.get_from_file(fmt1, offset)[0]
        else:
            return self.get_from_file(fmt2.format(n), offset)

    def getInt(self, n=1, offset=-1):
        """Get an int."""
        return self.__getValue(n, offset, "<i", "<{}i")

    def getShort(self, n=1, offset=-1):
        """Get a short."""
        return self.__getValue(n, offset, "<h", "<{}h")

    def getFloat(self, n=1, offset=-1):
        """Get a float."""
        return self.__getValue(n, offset, "<f", "<{}f")

    def getDouble(self, n=1, offset=-1):
        """Get a float."""
        return self.__getValue(n, offset, "<d", "<{}d")

    def getUChar(self, n=1, offset=-1):
        """Get an unsigned char."""
        return self.__getValue(n, offset, "<B", "<{}B")

    def getString(self, n, offset=-1):
        """Get a string array."""
        out = self.get_from_file("<{}c".format(n), offset)
        ifirst = out.index(b'\x00')
        return b"".join(out[:ifirst])


class HeaderBlock(object):
    """A header block in the IRB file."""

    UNKNOWN, EMPTY, IMAGE, PREVIEW, TEXT_INFO, HEADER, AUDIO = (
        -1, 0, 1, 2, 3, 4, 7)

    header_name = {
        UNKNOWN: "Unknown",
        EMPTY: "Empty",
        IMAGE: "Image",
        PREVIEW: "Preview",
        TEXT_INFO: "Text Info",
        HEADER: "Header",
        AUDIO: "Audio"
    }

    def __init__(self, ifile):
        """Initialize the object.

        Args:
        ----
            ifile: The input file

        """
        self.ifile = ifile
        self.where = ifile.tell()
        self.type = ifile.getInt()
        self.word2 = ifile.getInt()
        self.frameIndex = ifile.getInt()
        self.offset = ifile.getInt()
        self.size = ifile.getInt()

        # head has fixed size of 0x6C0
        # but check against headerSize...
        headerSize = 0x6C0
        if (headerSize > self.size):
            headerSize = self.size

        # headerOffset = 0

        self.imageOffset = headerSize
        self.imageSize = self.size - self.imageOffset

        self.word6 = ifile.getInt()
        self.word7 = ifile.getInt()
        self.word8 = ifile.getInt()
        self.end = ifile.tell()

        if self.end - self.where != 32:
            raise RuntimeError("byte counting error in parsing of HeaderBlock")

    def get_name(self):
        """Return the header type as string."""
        return HeaderBlock.header_name[self.type]


class IRBPreview(object):
    """A preview in the IRB file."""

    def __init__(self, block):
        """Initialize.

        Args:
            block: the block with the information.

        """
        self.block = block
        old_position = block.ifile.tell()



        block.ifile.seek(old_position)


class IRBImage(object):
    """An image in the IRBis file."""

    FLAGS_OFFSET = 1084
    CELSIUS_OFFSET = 273.15

    def __init__(self, block):
        """Initialize.

        Args:
            ifile: The input file
            block: The block with the information.

        """
        self.block = block
        ifile = block.ifile
        old_position = ifile.tell()

        # GEt to the correct position in buffer
        ifile.seek(block.offset)
        self.bytesPerPixel = ifile.getShort()
        self.compressed = ifile.getShort()
        self.width = ifile.getShort()
        self.height = ifile.getShort()

        zero = ifile.getInt()
        zero = ifile.getShort()

        widthM1 = ifile.getShort()
        if self.width-1 != widthM1:
            print("width-1 check failed")

        zero = ifile.getShort()
        heightM1 = ifile.getShort()
        if self.height - 1 != heightM1:
            print("height-1 check failed")

        zero = ifile.getShort()  # -32768 VarioCAM
        zero = ifile.getShort()

        # Get other parameters
        self.emissivity = ifile.getFloat()
        self.distance = ifile.getFloat()
        self.envTemp = ifile.getFloat()

        zero = ifile.getShort()
        zero = ifile.getShort()  # -32768 VarioCAM

        self.pathTemp = ifile.getFloat()

        zero = ifile.getShort()  # 0x65 for variocam
        zero = ifile.getShort()  # 16256 for VarioCAM

        self.centerWavelength = ifile.getFloat()

        zero = ifile.getShort()
        zero = ifile.getShort()
        zero = ifile.getShort()
        zero = ifile.getShort()

        if self.width > 10000 or self.height > 10000:
            raise RuntimeError("Image size out of range ({}x{})".format(
                self.width, self.height))

        flagsPosition = block.offset + IRBImage.FLAGS_OFFSET
        self.readImageFlags(flagsPosition)

        # TODO: is this HeaderBlock.headerSize ?
        self.data_offset = 0x6C0
        self.palette_offset = 60
        self.offset = block.offset
        self._image = None
        # self.readImageData(ifile)

        ifile.seek(old_position)

    def __getstate__(self):
        """Select memeber that will not be pickled."""
        state = self.__dict__.copy()
        del state['block']
        return state

    def __setstate__(self, state):
        """Restore block."""
        self.__dict__.update(state)
        self.block = None

    def readImageFlags(self, position):
        """Read Image Flags."""
        ifile = self.block.ifile
        old_position = ifile.tell()

        self.calibRangeMin = ifile.getFloat(offset=position+92)
        self.calibRangeMax = ifile.getFloat(offset=position+96)
        self.device = ifile.getString(12, position+142)
        self.deviceSN = ifile.getString(16, position+450)
        self.optics = ifile.getString(32, position+202)
        self.opticsResolution = ifile.getString(32, position+234)
        self.opticsText = ifile.getString(48, position+554)

        self.shortRangeStartErr = ifile.getFloat(offset=position+532)
        self.shotRangeSize = ifile.getFloat(offset=position+536)

        self.timeStampRaw = ifile.getDouble(offset=position+540)
        self.timestampMillisecond = ifile.getInt(offset=position+548)
        self.timestamp = ole2datetime(self.timeStampRaw)

        ifile.seek(old_position)

    def readImageData(self):
        """Get Image data."""
        ifile = self.block.ifile
        offset = self.offset
        data_offset = self.data_offset
        palette_offset = self.palette_offset
        dataSize = self.width * self.height
        self._image = np.zeros(dataSize)
        matrixDataPos = 0
        v1_pos = data_offset
        v2_pos = v1_pos + dataSize
        v1 = 0
        v2 = 0
        v2_count = 0

        # Read Palette
        self.readPalette(ifile, offset + palette_offset)

        # Read the data
        v1_data = ifile.getUChar(n=dataSize, offset=offset+data_offset)

        if self.compressed:
            # Compression
            # Read Data
            n2 = self.block.size-data_offset-dataSize
            v2_data = ifile.getUChar(n=n2)
            v2_pos = 0

            for i in range(dataSize):
                if v2_count < 1:
                    v2_count = v2_data[v2_pos]
                    v2 = v2_data[v2_pos+1]
                    if v2 < 0:
                        v2 += 256
                    P1 = self.palette[(v2+1) % 256]
                    P2 = self.palette[v2]
                    v2_pos += 2

                v2_count -= 1

                v1 = v1_data[i]
                if v1 < 0:
                    v1 += 256

                f = v1/256.0

                # linear interpolation betweeen eighboring palette entries
                v = P1*f + P2*(1.0-f)
                if v < 0.0:
                    v = 0.0

                self._image[matrixDataPos] = v
                matrixDataPos += 1

        else:
            # No compression
            for i in range(dataSize):
                v1 = v2_data[v1_pos]
                v2 = v2_data[v1_pos+1]
                P1 = self.palette[v2+1]
                P2 = self.palette[v2]
                v1_pos += 2

                f = v1/256.0

                # linear interpolation betweeen eighboring palette entries
                v = P1*f + P2*(1.0-f)
                if v < 0.0:
                    v = 0.0

                self._image[matrixDataPos] = v
                matrixDataPos += 1

        self._image -= IRBImage.CELSIUS_OFFSET
        self._image = self.image.reshape(self.height, self.width)
        self._image = np.flipud(self._image)

    def readPalette(self, ifile, offset):
        """Read palette from input buffer."""
        old_position = ifile.tell()
        ifile.seek(offset)
        self.palette = np.array(ifile.getFloat(n=256))
        ifile.seek(old_position)

    def __getImage(self):
        """Get image."""
        if self._image is None:
            self.readImageData()

        return self._image

    def __setImage(self, val):
        """Set the image."""
        self._image = val

    def __delImage(self):
        """Delete the imafe"""
        del self._image

    # Get image
    image = property(lambda self: self.__getImage(),
                     lambda self, val: self.__setImage(val),
                     lambda self: self.__delImage())


class IRBFile(object):
    """An IRB file.

    Read a file or list of files and store the different blocks and immages.

    Examples
    --------
        An IRB file is opened like this:

            irbf = IRBFile.open_file( file )

        This wull get just the header information, but not yet the full heavy
        load of values per pixel. These will only be loaded when access is
        requested.

        One can iterate over the images or frames using
            irbf.images()

        That will return an iterator. An example of use:

            for i, img in enumerate(irbf.images()):
                values_i = img.image ...

        One can access a given image by its index:
            img = irbf.getImage(i)

        The total nubmer of images of frams available is given by
            irbf.n_images()

    """

    def __init__(self, fname, concatenate=False):
        """Initialize.

        Args:
        ----
            fname: Path of input file or list of files.

        """
        self.concatenate = concatenate
        self.imgList = []
        self.previewList = []
        self.blocks = []
        self.ifiles = []
        self.file_images = []
        self.current_file = 0

        if not is_iterable(fname):
            fname = [fname]

        for fnam in fname:
            fb = open(fnam, 'rb')
            ifile = BinaryFile(fb)
            if not concatenate:
                self.imgList = []

            self.parseHeader(ifile)
            self.ifiles.append(ifile)
            self.file_images.append(self.imgList)

        self.set_file(self.current_file)

    def __getstate__(self):
        """Select memeber that will not be pickled."""
        state = self.__dict__.copy()
        del state['blocks']
        del state['ifiles']
        return state

    def __setstate__(self, state):
        """Restore block."""
        self.__dict__.update(state)
        self.blocks = []
        self.ifiles = []

    # number of files
    nfiles = property(lambda self: len(self.ifiles))

    # number of images
    nimages = property(lambda self: len(self.imgList))

    def parseHeader(self, ifile):
        """Read the header."""
        magic = ifile.read(5)
        # if magic[1:-1] != "IRB":
        #    print("Not an IRB file")

        # GEt the file type
        self.fileType = ifile.read(8)
        if b"IRBIS" in self.fileType:
            self.is_sequence = True
        else:
            self.is_sequence = False

        # GEt Second filetype (ignored)
        tmp = ifile.read(8)

        flag1 = ifile.getInt()
        blockOffset = ifile.getInt()
        blockCount = ifile.getInt()

        # Get the blocks
        ifile.seek(blockOffset)
        for iblk in range(blockCount):
            block = HeaderBlock(ifile)
            if block.type != HeaderBlock.EMPTY:
                self.blocks.append(block)

        for block in self.blocks:
            if block.type == HeaderBlock.IMAGE:
                image = IRBImage(block)
                self.imgList.append(image)
            elif block.type == HeaderBlock.PREVIEW:
                image = IRBPreview(block)
                self.previewList.append(image)

        if self.is_sequence:
            offset = -1
            for block in self.blocks:
                if block.type == HeaderBlock.HEADER:
                    offset = block.offset

            ifile.seek(offset)
            while True:
                space_left = ifile.end - ifile.tell()
                if space_left < 32:
                    break

                block = HeaderBlock(ifile)
                if block.type == HeaderBlock.IMAGE:
                    if block.offset + block.imageSize > ifile.end:
                        break

                    image = IRBImage(block)
                    self.imgList.append(image)

                elif block.type == HeaderBlock.HEADER:
                    offset = block.offset
                    ifile.seek(offset)

                elif block.type == HeaderBlock.TEXT_INFO:
                    pass

    def set_concatenate(self, val):
        """Set the 'concatenate' mode.

        If trye Files are read one after the other, if False, fileas are read in parallel.
        """
        if self.concatenate == val:
            return

        self.concatenate = val
        self.imgList = []
        for i in range(self.nfiles):
            for im in self.file_images[i]:
                self.imgList.append(im)

    def set_file(self, i):
        """Selects i-th file.

        This will select the images from that file.

        Args:
            i: the index of the file.
        """
        if i < 0 or i > self.nfiles:
            raise IndexError

        self.current_file = i
        self.imgList = self.file_images[i]

    def getImage_timestamp(self, i):
        """Return timestamp of i-th image."""
        return self.imgList[i].timestamp

    def getImage(self, i):
        """Get i-th image in current file.

        Use set_file to change to another IRBfile.
        """
        if i > self.nimages:
            return None

        if self.imgList[i].image is None:
            self.imgList[i].readImageData()

        return self.imgList[i]

    def images(self, first=0, nframes=-1):
        """Generator to loop on images in current file."""
        nyield = 0
        if self.concatenate:
            for i, im in enumerate(self.imgList):
                if i < first:
                    continue

                if nframes > 0 and nyield >= nframes:
                    break

                nyield += 1
                yield [im]
        else:
            for i, im in enumerate(zip(*self.file_images)):
                if i < first:
                    continue

                if nframes > 0 and nyield >= nframes:
                    break

                nyield += 1
                yield im

    def append_average(self, nframes=-1, debug=False):
        """Append the average of all images to the list of images.

        Args:
        ----
            debug (bool, optional): True for debugging. Defaults to False.

        Raises
        ------
            RuntimeError: Will raise a RunTimeError if IRBfile is empty.

        """
        # Get all images
        out = []
        for ifile in range(self.nfiles):
            self.set_file(ifile)
            list_values = []
            if nframes < 0:
                nframes = self.nimages

            img = None
            for i in range(self.nimages):
                img = self.getImage(i)
                if debug:
                    print('Image: ', i, )  # ' - Size: ',img.height,' x ', img.width)

                values_i = img.image
                list_values.append(values_i)
                if i >= nframes:
                    break

            if len(list_values) == 0:
                continue

            # and compute the average
            values_average = np.mean(list_values, axis=0)

            # Append the average to the list
            # Copy data from last image for average_image, some info will be replaced
            avg_img = copy.copy(img)
            self.imgList.append(avg_img)

            # Replace values of last img with values for average_image
            # avg_img.block.end        = 0  # Unsure what this is...
            # avg_img.block.frameIndex += 1  # Correct
            # avg_img.block.ifile.end = 0  # ifile is a bit weird to understand, but the only obviious difference is end
            # avg_img.block.imageSize = 0  # Unsure what this is...
            # avg_img.block.offset    = 0  # Unsure what this is...
            # avg_img.block.size      = 0  # Unsure what this is...
            # avg_img.block.where     = 0 # Unsure what this is...
            # avg_img.offset          = 0 # Unsure what this is... 98: 8769050, 99: 88362978
            # avg_img.palette         = np.zeros(256,) # Unsure what this is...
            # avg_img.timeStampRaw = img.timeStampRaw # currently the timestamp of the last image/frame
            # avg_img.timestamp    = img.timestamp # currently the timestamp of the last image/frame
            # avg_img.timestampMillisecond = img.timestampMillisecond # currently the timestamp of the last image/frame
            avg_img.image = values_average  # Here go the new values
            self.has_average = True

            # Hope I found them all!
            print('Average calculated!')

            if debug:
                x = 0
                y = 0
                xy_average = np.mean([frame[x, y]for frame in list_values])

                print('Average on pixel ', x, ' , ', y, ' is ', xy_average)
                print('The pixel ', x, ' , ', y, ' is in values_average is ', values_average[x, y])

            out.append(avg_img)

        if len(out) != self.nfiles:
            raise RuntimeError("No images found to compute the average")

        return out

    def save(self, fname):
        """Save teh list of images in pickle format."""
        # Be sure that all images are loaded.
        for i in range(self.nimages):
            if self.imgList[i].image is None:
                self.imgList[i].readImageData()

        with bz2.BZ2File(fname, 'w') as ofile:
            pickle.dump(self, ofile)

    @staticmethod
    def load(fname):
        """Load an IRBFile objecr."""
        out = None
        with bz2.BZ2File(fname, 'rb') as ifile:
            out = pickle.load(ifile)

        return out


def open_file(fname, concat=False):
    """Opens a file an returns a IRBFile instance.

    Args:
    ----
        fname: Path of input file or list of files.

    """
    irbf = None
    if is_iterable(fname):
        # we assume it is a list of IRB files...
        try:
            if concat:
                irbf = IRBFile(fname)
                return irbf
            else:
                out = []
                for f in fname:
                    irbf = IRBFile(f)
                    out.append(irbf)
                
                if len(out) == 1:
                    out = out[0]
                    
                return out

        except FileNotFoundError as eee:
            print(eee)

    else:
        # it is a single file path. Check that it exists.
        ifile = Path(fname).expanduser().resolve()
        if not ifile.exists():
            print("Input file does not exist.")
            return None

        suffix = ifile.suffix.lower()
        if suffix == ".irb":
            irbf = IRBFile(fname)

        else:
            try:
                irbf = IRBFile.load(fname)
            except Exception as eee:
                print(eee)
                irbf = None

    return irbf


def main():
    """Example of use of IRBFile.

       Shows all the images in a file.

    """
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--save", action="store_true",
                        default=False,
                        help="save all figures")
    options = parser.parse_args()
    if len(options.files) == 0:
        print("I need an input file")
        sys.exit()

    IRfile = IRBFile(options.files)
    nimgs = IRfile.nimages
    print("Number of images: {}".format(nimgs))

    fig = None
    nimg = 0
    ratio = -1
    for ximg in IRfile.images():
        img = ximg[0]
        tmin = np.min(img.image)
        print("Tmin {:1f} - {}x{}".format(tmin, img.width, img.height))
        if ratio < 0:
            ratio = float(img.width)/float(img.height)

        plt.clf()
        plt.gca().clear()
        pcm = plt.imshow(img.image, origin='lower', cmap="jet")
        plt.gca().set_title("Min T. {:.1f} - {}".format(tmin, img.timestamp))
        plt.colorbar(pcm, ax=plt.gca())
        plt.draw()
        if options.save:
            if fig is None:
                fig = plt.gcf()
                fig.set_size_inches(6*ratio, 6)

            fig.savefig('fig_{}.png'.format(nimg), dpi=300)
            nimg += 1

        plt.pause(0.00001)

    plt.show()

if __name__ == "__main__":
    main()
