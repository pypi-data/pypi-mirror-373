"""
Global variables and helpers for forced alignment
"""

import bisect
import os
import sys
import yaml

from . import logger

# global variables

SP = "sp"
SIL = "sil"
TEMP = "temp"

EPOCHS = 5

MISSING = "missing.txt"
OOV = "OOV.txt"

CONFIG = "config.yaml"
DICT = "dict"
HMMDEFS = "hmmdefs"
MACROS = "macros"
PROTO = "proto"
VFLOORS = "vFloors"

ALIGNED = ".aligned.mlf"
SCORES = ".scores.csv"


# samplerates which appear to be HTK-compatible (all divisors of 1e7)
SAMPLERATES = [4000, 8000, 10000, 12500, 15625, 16000, 20000, 25000,
               31250, 40000, 50000, 62500, 78125, 80000, 100000, 125000,
               156250, 200000]


# helpers

def opts2cfg(filename, opts):
    """
    Convert dictionary of key-value pairs to an HTK config file
    """
    with open(filename, "w") as sink:
        for (setting, value) in opts.items():
            print("{!s} = {!s}".format(setting, value), file=sink)


def mkdir_p(dirname):
    """
    Create a directory, recursively if necessary, and suceed
    silently if it already exists
    """
    os.makedirs(dirname, exist_ok=True)


def splitname(fullname):
    """
    Split a filename into directory, basename, and extension
    """
    (dirname, filename) = os.path.split(fullname)
    (basename, ext) = os.path.splitext(filename)
    return (dirname, basename, ext)


def resolve_opts(aligner=False, configuration=None, dictionary=False, samplerate=False,
                 epochs=False, read=False, train=False, align=False, write=False):
    if configuration is None:
        logger.error("Configuration file not specified.")
        sys.exit(1)
    with open(configuration, "r") as source:
        try:
            opts = yaml.load(source, Loader=yaml.FullLoader)
        except yaml.YAMLError as err:
            logger.error("Error in configuration file: %s", err)
            sys.exit(1)

    # command line only
    if not dictionary:
        logger.error("Dictionary not specified.")
        sys.exit(1)
    opts["dictionary"] = dictionary

    if not epochs:
        epochs = EPOCHS
    opts["epochs"] = epochs

    # could be either, and the command line takes precedent.
    try:
        sr = samplerate if samplerate else opts["samplerate"]
    except KeyError:
        logger.error("Samplerate (-s) not specified.")
        sys.exit(1)

    if sr not in SAMPLERATES:
        i = bisect.bisect(SAMPLERATES, sr)
        if i == 0:
            pass
        elif i == len(SAMPLERATES):
            i = -1
        elif SAMPLERATES[i] - sr > sr - SAMPLERATES[i - 1]:
            i = i - 1
        # else keep `i` as is
        sr = SAMPLERATES[i]
        logger.warning(f"Using {sr} Hz as samplerate")

    opts["samplerate"] = sr
    return opts
