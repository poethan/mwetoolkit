<h2>XML corpus</h2>

<!-- Short description -->
<p>A textual corpus represented in XML.</p>

<h3>Characteristics</h3>

<p>See the generic <a href="PHITE.php?sitesig=MWE&page=MWE_060_File_types">XML description</a>.</p>


<h3>Details</h3>

<p>The root element of a corpus XML file is called <tt>&lt;corpus&gt;</tt> 
A corpus file is a list of sentences delimited by tags <tt>&lt;s&gt;</tt> and 
<tt>&lt;/s&gt;</tt>. Each sentence must have a unique numerical ID, generally 
starting from 1, indicated as attribute <tt>s_id="..."</tt>. A sentence contains 
a list of words. Each word is an empty XML element <tt>&lt;w/&gt;</tt> with 4 
optional attributes: </p>
<ul>
<li><tt>surface</tt> : surface form, word as it occurs in running text.</li>
<li><tt>lemma</tt> : canonical word form, e.g. infinitive for verbs and singular for nouns</li>
<li><tt>pos</tt> : part of speech, that is, morphosyntactic categories like NOUN, ADVERB, etc.</li>
<li><tt>syn</tt> : dependency syntax in the form of a colon-separated pair REL:HEAD, where REL is the nature of the suntactic relation and HEAD is the position of the governor</li>
</ul>

<p>
Each word is implicitly numbered according to its position, starting at 1. The HEAD information in syn attribute uses this number to indicate the position of the head. REL names should not contain colons. An absent attribute should be ommited, an attribute value should never be empty. 
</p>

<p>An example of corpus file would have the following structure:</p>

<pre>
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE corpus SYSTEM "dtd/mwetoolkit-corpus.dtd"&gt;
&lt;corpus&gt;
&lt;s s_id="1"&gt;
  &lt;w surface="X" lemma="X" pos="X" syn="X:2" /&gt;
  ...
&lt;/s&gt;
...
&lt;/corpus&gt;
</pre>

<h3>Example</h3>

<p>You can have a look at a sample <a
href="http://sourceforge.net/p/mwetoolkit/code/HEAD/tree/test/filetype-samples/corpus.xml">corpus</a>
file.</p>

<hr/>
