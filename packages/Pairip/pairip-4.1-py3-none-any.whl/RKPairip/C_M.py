class CM:
    def __init__(self):
        # ---------------- Multiprocess / Multiprocessing ----------------
        try:
            mp = __import__('multiprocess')
        except ImportError:
            mp = __import__('multiprocessing')

        # ---------------- Libraries Import ----------------
        self.os, self.sys, self.shutil, self.subprocess, self.re, self.time, self.glob, self.zlib, self.pickle, self.zipfile, self.base64, self.binascii, self.hashlib, self.argparse, self.json, self.struct, self.tempfile, self.datetime, self.Pool, self.cpu_count, self.Manager = __import__('os'), __import__('sys'), __import__('shutil'), __import__('subprocess'), __import__('re'), __import__('time'), __import__('glob'), __import__('zlib'), __import__('pickle'), __import__('zipfile'), __import__('base64'), __import__('binascii'), __import__('hashlib'), __import__('argparse'), __import__('json'), __import__('struct'), __import__('tempfile'), __import__('datetime').datetime, mp.Pool, mp.cpu_count, mp.Manager

        # ---------------- Color Codes ----------------
        self.y, self.c, self.g, self.pr, self.lb, self.r, self.rd, self.rkj, self.rkk, self.cp, self.pn, self.cb = '\033[1m\033[33m', '\033[1m\033[96m', '\033[1m\033[92m', '\033[1m\033[35m', '\033[1m\033[94m', '\033[0m', '\033[1m\033[91m', '\033[1m\033[38;5;202m', '\033[1m\033[38;5;27m', '\033[1m\033[35m', '\033[1m\033[38;5;201m', '\033[1m\033[34m'