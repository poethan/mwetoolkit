#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# xml2human.py is part of mwetoolkit
#
# mwetoolkit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mwetoolkit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mwetoolkit.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
This script implements conversion from XML format to a more
human-readable format for easier visual inspection.

For more information, call the script with no parameter and read the
usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import collections
import sys

from libs.base.mweoccur import MWEOccurrenceBuilder, MWEOccurrence
from libs.util import read_options, treat_options_simplest, verbose, error
from libs.printers import XMLPrinter, SurfacePrinter, MosesPrinter
from libs.parser_wrappers import parse, InputHandler, StopParsing
from libs.printers import AbstractPrinter


################################################################################
# GLOBALS

usage_string = """Usage:
    
python %(program)s OPTIONS <corpus.xml>

    
OPTIONS may be:

    XXX ADD OPTIONS
      
%(common_options)s
"""

limit = 10
reference_fname = None
mwe_evaluator = None


################################################################################


class PrettyPrinterHandler(InputHandler):
    def __init__(self):
        self.printer = HumanPrinter()

    def handle_sentence(self, sentence, info={}):
        self.handling("Corpus")
        self.printer.add_line(sentence.to_surface())

    def handle_pattern(self, pattern, info={}):
        self.handling("Patterns")
        self.printer.add_line(pattern.printable_pattern())

    def handle_candidate(self, candidate, info={}):
        self.handling("Candidates")
        self.printer.add_line(candidate.to_surface())

    def handling(self, handled_type):
        self.printer.handling(handled_type)


class HumanPrinter(AbstractPrinter):
    """Instances can print human-readable stuff."""
    def __init__(self):
        super(HumanPrinter, self).__init__(None)
        self.handled_type = None

    def stringify(self, obj):
        return unicode(obj)

    def add_line(self, line):
        for split_line in line.split("\n"):
            self.add("[", self.counter+1, "] ", split_line, "\n")

    def handling(self, handled_type):
        if self.handled_type == handled_type:
            self.counter += 1
            if self.counter >= limit:
                raise StopParsing
        else:
            if self.handled_type is not None:
                self.add("\n")
            self.add(handled_type, ":\n")
            self.handled_type = handled_type
            self.counter = 0

        # Corpus:
        # | FOUND A SENTENCE
        # | <libs.base.sentence.Sentence object at 0x7fc1f9354190>
        # 
        # Pattern:
        # | FOUND A PATTERN
        # | <libs.patternlib.ParsedPattern object at 0x7fc1f934add0>
        # | @_,_,_,N_,_@(?:_,_,_,N_,_@)+



###########################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """Callback function that handles the command line options of this script.
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.    
    """
    global reference_fname
    global mwe_evaluator

    treat_options_simplest(opts, arg, n_arg, usage_string)


        
################################################################################  
# MAIN SCRIPT


if __name__ == "__main__":
    longopts = []
    args = read_options("", longopts, treat_options, -1, usage_string)
    parse(args, PrettyPrinterHandler())
