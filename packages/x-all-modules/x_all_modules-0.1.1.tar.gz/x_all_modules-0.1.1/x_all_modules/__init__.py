import sys

# ========= UNIVERSAL MODULES =========
import math; x_math = math
import random; x_random = random
import os; x_os = os
import re; x_re = re
import json; x_json = json
import time; x_time = time
import datetime; x_datetime = datetime
import statistics; x_statistics = statistics
import itertools; x_itertools = itertools
import functools; x_functools = functools
import operator; x_operator = operator
import decimal; x_decimal = decimal
import fractions; x_fractions = fractions
import hashlib; x_hashlib = hashlib
import hmac; x_hmac = hmac
import base64; x_base64 = base64
import binascii; x_binascii = binascii
import uuid; x_uuid = uuid
import secrets; x_secrets = secrets
import string; x_string = string
import typing; x_typing = typing
import collections; x_collections = collections
import heapq; x_heapq = heapq
import array; x_array = array
import bisect; x_bisect = bisect
import struct; x_struct = struct
import io; x_io = io
import pathlib; x_pathlib = pathlib
import shutil; x_shutil = shutil
import glob; x_glob = glob
import tempfile; x_tempfile = tempfile
import zipfile; x_zipfile = zipfile
import tarfile; x_tarfile = tarfile
import gzip; x_gzip = gzip
import bz2; x_bz2 = bz2
import lzma; x_lzma = lzma
import socket; x_socket = socket
import ssl; x_ssl = ssl
import http; x_http = http
import urllib; x_urllib = urllib
import email; x_email = email
import logging; x_logging = logging
import warnings; x_warnings = warnings
import contextlib; x_contextlib = contextlib
import traceback; x_traceback = traceback
import inspect; x_inspect = inspect
import ast; x_ast = ast
import dis; x_dis = dis
import tokenize; x_tokenize = tokenize
import keyword; x_keyword = keyword
import builtins; x_builtins = builtins
import types; x_types = types
import enum; x_enum = enum
import threading; x_threading = threading
import multiprocessing; x_multiprocessing = multiprocessing
import queue; x_queue = queue
import asyncio; x_asyncio = asyncio
import concurrent; x_concurrent = concurrent
import weakref; x_weakref = weakref
import copy; x_copy = copy
import pickle; x_pickle = pickle
import pprint; x_pprint = pprint
import locale; x_locale = locale
import sysconfig; x_sysconfig = sysconfig
import importlib; x_importlib = importlib
import pkgutil; x_pkgutil = pkgutil
import site; x_site = site
import platform; x_platform = platform
import calendar; x_calendar = calendar
import timeit; x_timeit = timeit
import difflib; x_difflib = difflib
import filecmp; x_filecmp = filecmp
import cmd; x_cmd = cmd
import argparse; x_argparse = argparse
import getopt; x_getopt = getopt
import pdb; x_pdb = pdb
import doctest; x_doctest = doctest
import unittest; x_unittest = unittest
import venv; x_venv = venv
import sqlite3; x_sqlite3 = sqlite3
import xml; x_xml = xml
import html; x_html = html
import csv; x_csv = csv
import configparser; x_configparser = configparser
import ctypes; x_ctypes = ctypes
import imaplib; x_imaplib = imaplib
import smtplib; x_smtplib = smtplib
import mailbox; x_mailbox = mailbox
import getopt; x_getopt = getopt
import numbers; x_numbers = numbers
import reprlib; x_reprlib = reprlib
import fractions; x_fractions = fractions

# ========= OPTIONAL INTERNALS (try/except) =========
try:
    import _weakref; x__weakref = _weakref
except ImportError:
    x__weakref = None

try:
    import _weakrefset; x__weakrefset = _weakrefset
except ImportError:
    x__weakrefset = None

try:
    import _opcode_metadata; x__opcode_metadata = _opcode_metadata
except ImportError:
    x__opcode_metadata = None

try:
    import _lzma; x__lzma = _lzma
except ImportError:
    x__lzma = None

try:
    import _threading_local; x__threading_local = _threading_local
except ImportError:
    x__threading_local = None

try:
    import _interpreters; x__interpreters = _interpreters
except ImportError:
    x__interpreters = None

try:
    import _imp; x__imp = _imp
except ImportError:
    x__imp = None

try:
    import _io; x__io = _io
except ImportError:
    x__io = None

try:
    import _frozen_importlib; x__frozen_importlib = _frozen_importlib
except ImportError:
    x__frozen_importlib = None

try:
    import _frozen_importlib_external; x__frozen_importlib_external = _frozen_importlib_external
except ImportError:
    x__frozen_importlib_external = None

try:
    import _pydatetime; x__pydatetime = _pydatetime
except ImportError:
    x__pydatetime = None

try:
    import _pydecimal; x__pydecimal = _pydecimal
except ImportError:
    x__pydecimal = None

try:
    import _strptime; x__strptime = _strptime
except ImportError:
    x__strptime = None

try:
    import _zoneinfo; x__zoneinfo = _zoneinfo
except ImportError:
    x__zoneinfo = None

try:
    import _warnings; x__warnings = _warnings
except ImportError:
    x__warnings = None

try:
    import _thread; x__thread = _thread
except ImportError:
    x__thread = None

# ========= OS-SPECIFIC =========
if sys.platform == "win32":
    try:
        import winreg; x_winreg = winreg
    except ImportError:
        x_winreg = None
    try:
        import winsound; x_winsound = winsound
    except ImportError:
        x_winsound = None
    try:
        import msvcrt; x_msvcrt = msvcrt
    except ImportError:
        x_msvcrt = None

elif sys.platform.startswith("linux"):
    try:
        import fcntl; x_fcntl = fcntl
    except ImportError:
        x_fcntl = None
    try:
        import grp; x_grp = grp
    except ImportError:
        x_grp = None
    try:
        import termios; x_termios = termios
    except ImportError:
        x_termios = None

elif sys.platform == "darwin":  # macOS
    try:
        import _osx_support; x__osx_support = _osx_support
    except ImportError:
        x__osx_support = None
