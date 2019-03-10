#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  (c) Sébastien Béchet 2014

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License Version 3 as
#  published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

import sys
from collections import OrderedDict

# import pdb
# breakpoint: pdb.set_trace()


# Only MGC at this time
class Crd(object):
    filename = ""
    signature = "MGC"
    quantity = 0
    entries = {}

    def __init__(self):
        self.filename = ""
        self.signature = "MGC"
        self.quantity = 0
        self.entries = {}

    def open(self, filename):
        self.filename = filename
        f = open(filename, "rb")
        try:
            self.signature = f.read(3)
            if self.signature != b'MGC':
                return False
            self.quantity = int.from_bytes(f.read(2), byteorder='little')
            for i in range(self.quantity):
                f.seek(6, 1)
                pos = int.from_bytes(f.read(4), byteorder='little')
                f.seek(1, 1)
                text = f.read(40)
                text = text.decode('cp1252')
                text = text.split('\0', 1)[0]
                self.entries[text.strip().title()] = pos
                f.seek(1, 1)
            for key, seek in self.entries.items():
                f.seek(seek, 0)
                lob = int.from_bytes(f.read(2), byteorder='little')
                if lob == 0:
                    lot = int.from_bytes(f.read(2), byteorder='little')
                    value = f.read(lot)
                    value = value.decode('cp1252')
                    value = value.replace('\r\n', '\n')
                    self.entries[key] = value.strip()
                else:
                    print('erreur lob=', lob, ' pour un seek=', seek)
        finally:
            f.close()

    def toHtml(self):
        entries2 = OrderedDict(sorted(self.entries.items()))
        text = '<!DOCTYPE html>'
        text += '<html lang="fr">'
        text += '<head>'
        text += '<meta charset="utf-8">'
        text += '<title>' + self.filename + '</title>'
        text += '</head>'
        text += '<body>'
        for key, value in entries2.items():
            text += '<h1>' + key + '</h1>'
            text += '<pre>' + value + '</pre>'
        text += '</body></html>'
        return text

    def toMarkdown(self):
        entries2 = OrderedDict(sorted(self.entries.items()))
        text = ''
        for key, value in entries2.items():
            text += '# ' + key + '\n\n'
            text += '```\n' + value + '\n```' + '\n\n\n'
        return text


if __name__ == '__main__':
    tout = {}
    if len(sys.argv) < 2:
        print('Usage : ', sys.argv[0], ' <filename.crd> ...')
    else:
        nb = len(sys.argv) - 1
        for i in range(nb):
            crd = Crd()
            crd.open(sys.argv[i + 1])
            tout.update(crd.entries)
        crd = Crd()
        crd.entries = tout
        print(crd.toMarkdown())
