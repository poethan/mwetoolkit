#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# xml2csv.py is part of mwetoolkit
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
    This script converts a candidates file in XML (mwetoolkit-candidates.dtd)
    into a corresponding representation in the file format 
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import xml.sax
import re

from xmlhandler.genericXMLHandler import GenericXMLHandler
from util import read_options, treat_options_simplest
from xmlhandler.classes.__common import WILDCARD
     
################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python %(program)s OPTIONS <file.xml>

OPTIONS may be:

-s OR --surface
    Outputs surface forms instead of lemmas. Default false.
    
-p OR --lemmapos
    Outputs the corpus in lemma/pos format. Replaces slashes by "@SLASH@". 
    Default false.

    The <file.xml> file must be valid XML (dtd/mwetoolkit-*.dtd).
"""   
surface_instead_lemmas = False  
lemmapos = False

xml_meta = None
freq_source = 0
            
################################################################################     

def treat_meta( meta ) :
    """
    """
    global xml_meta
    string_cand = "id\tl1\tl2\tf\tf1\tf2\tN"

    #for cs in meta.corpus_sizes :
    #    string_cand = string_cand + cs.name + "\t"
    #string_cand = string_cand + "occurs\tsources\t"

    #for cs in meta.meta_tpclasses :
    #    string_cand = string_cand + cs.name + "\t"
    #for cs in meta.meta_feats :
    #    string_cand = string_cand + cs.name + "\t"  
    xml_meta = meta
        
    print string_cand.encode( 'utf-8' )       
       
################################################################################     
       
def treat_entity( entity ) :
    """
        For each `Candidate`, print the candidate ID, its POS pattern and the 
        list of occurrences one per line
        
        @param candidate The `Candidate` that is being read from the XML file.
    """
    global surface_instead_lemmas
    global lemmapos
    string_cand = ""
    if entity.id_number >= 0 :
        string_cand += str( entity.id_number )
    string_cand = string_cand.strip() + "\t"    
    
    if len(entity) != 2:
        print >>sys.stderr, "WARNING: Ignoring entity %s, of length %d!=2" % (entity.id_number, len(entity))
        return

    for w in entity :
        if lemmapos :
            string_cand += w.lemma.replace( "/", "@SLASH@" ) + "/" + w.pos + "\t"
        elif w.lemma != WILDCARD and not surface_instead_lemmas :
            string_cand += w.lemma + "\t"
        else :
            string_cand += w.surface + "\t"

    string_cand += "%f\t" % entity.freqs[freq_source].value

    try:
        for w in entity:
            string_cand += "%f\t" % w.freqs[freq_source].value
    except:
        string_cand += "0\t"
        print >>sys.stderr, "WARNING: Word frequency information missing for entity %d" % entity.id_number

    #try:
    #    occur_dict = {}
    #    sources = []
    #    for occur in entity.occurs :
    #        surfaces = []
    #        sources.extend(occur.sources)
    #        for w in occur :
    #            surfaces.append( w.surface )
    #        occur_dict[ " ".join( surfaces ) ] = True

    #    string_cand += "; ".join( occur_dict.keys() ) + "\t"
    #    string_cand += ";".join(sources) + "\t"

    #except AttributeError:
    #    # This kind of entry probably doesnt have occurs
    #    string_cand = string_cand.strip() + "\t-\t"

    #try :
    #    for feat in entity.features :
    #        string_cand += str( feat.value ) + "\t"
    #except AttributeError:
    #    # This kind of entry probably doesnt have tpclass
    #    string_cand = string_cand.strip()

    string_cand += str(xml_meta.corpus_sizes[freq_source].value)
        
    #string_cand = string_cand.strip()

    print string_cand.encode( 'utf-8' )

################################################################################     

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global surface_instead_lemmas
    global lemmapos
    mode = []
    for ( o, a ) in opts:        
        if o in ("-s", "--surface") : 
            surface_instead_lemmas = True     
        if o in ("-p", "--lemmapos") : 
            lemmapos = True                 
    treat_options_simplest( opts, arg, n_arg, usage_string )


################################################################################     
# MAIN SCRIPT

longopts = [ "verbose", "surface", "lemmapos" ]
arg = read_options( "vsp", longopts, treat_options, -1, usage_string )

try :
    parser = xml.sax.make_parser()
    handler = GenericXMLHandler( treat_meta=treat_meta,
                                 treat_entity=treat_entity,
                                 gen_xml=False )
    parser.setContentHandler( handler )
    if len( arg ) == 0 :
        parser.parse( sys.stdin )
    else :
        for a in arg :
            input_file = open( a )
            parser.parse( input_file )
            handler.gen_xml = False
            input_file.close()
            entity_counter = 0


    
except IOError, err :
    print >> sys.stderr, err
#except Exception, err :
#    print >> sys.stderr, err
#    print >> sys.stderr, "You probably provided an invalid candidates file," + \
#                         " please validate it against the DTD " + \
#                         "(dtd/mwetoolkit-candidates.dtd)"