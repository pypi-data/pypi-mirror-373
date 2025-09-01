
Spiki
#####

Spiki is a processor for SpeechMark_ content.

It can be used to generate static websites, blogs and other online literature.
Unlike template-based generators, Spiki uses TOML files to define the structure of output documents.

Spiki is at an early stage of development, but here's an example of how to use it::

    $ cd spiki
    $ python -m spiki.main =spiki/examples/basic/spiki.cli

SpeechMark
##########

:Author: D E Haynes
:Licence: `CC BY-NC-ND <https://creativecommons.org/licenses/by-nc-nd/4.0/>`_ Attribution-NonCommercial-NoDerivs

SpeechMark is a convention for markup of authored text.
It is designed for capturing dialogue, attributing speech, and writing screenplay directions.
This document explains the syntax, and shows how it should be rendered in HTML5.

Python library
==============

From the command line::

    echo "Hello, World!" | python -m spiki.speechmark

    <blockquote>
    <p>
    Hello, World!
    </p>
    </blockquote>

Parsing text programmatically::

    from spiki.speechmark import SpeechMark

    text = '''
    <PHONE.announcing@GUEST,STAFF> Ring riiing!
    <GUEST:thinks> I wonder if anyone is going to answer that phone.
    '''.strip()

    sm = SpeechMark()
    sm.loads(text)

... produces this HTML5 output::

    <blockquote cite="&lt;PHONE.announcing@GUEST,STAFF&gt;">
    <cite data-role="PHONE" data-directives=".announcing@GUEST,STAFF">PHONE</cite>
    <p>
     Ring riiing!
    </p>
    </blockquote>
    <blockquote cite="&lt;GUEST:thinks&gt;">
    <cite data-role="GUEST" data-mode=":thinks">GUEST</cite>
    <p>
     I wonder if anyone is going to answer that phone.
    </p>
    </blockquote>

SpeechMark takes inspiration from other markup systems already in common use, eg:

* `Markdown <https://commonmark.org/>`_
* `reStructuredText <https://docutils.sourceforge.io/rst.html>`_

I tried both these systems prior to creating SpeechMark. I found I needed some features which
Markdown didn't have. On the hand, RST proved to be overkill for my particular purpose.

Philosophy
==========

SpeechMark syntax is deliberately constrained to be simple and unambiguous.
This is to permit fast and efficient processing of many small pieces of text over an extended period of time.

SpeechMark does not concern itself with document structure. There are no titles, sections or breaks.
Rather, the input is expected to be a stream of text fragments.

The specification intends to be lossless, so that every non-whitespace feature of the original text
may be retrieved from the output. It should be possible to round-trip your SpeechMark scripts into
HTML5 and back again.

Features
========

SpeechMark has the basic elements you see in other markup systems, ie:

    * Emphasis_
    * Hyperlinks_
    * Comments_
    * Lists_

There is one feature very specific to SpeechMark:

    * Cues_

SpeechMark doesn't try to do everything. To integrate it into an application, you may
need:

    * Preprocessing_
    * Postprocessing_

Emphasis
--------

SpeechMark supports three flavours of emphasis.

* Surround text by asterisks ``*like this*`` to generate ``<em>`` tags.
* Use underscores ``_like this_`` to generate ``<strong>`` tags.
* Use backticks ```like this``` to generate ``<code>`` tags.

Hyperlinks
----------

Hyperlinks have two components; the label and the URL.
The label appears first within square brackets, followed by the URL in parentheses::

    [SpeechMark](https://github.com/thuswise/spiki)

Comments
--------

The `#` character denotes a comment. It must be the first character on a line::

    # Comments aren't ignored. They get converted to HTML (<!-- -->)

Lists
-----

Unordered lists
```````````````

The `+` character creates a list item of the text which follows it, like so::

    + Beef
    + Lamb
    + Fish


Ordered lists
`````````````
Using digits and a dot before text will give you an ordered list::

    1. Beef
    2. Lamb
    3. Fish

Cues
----

A cue marks the start of a new block of dialogue. Is is denoted by angled brackets::

    <>  Once upon a time, far far away...

Cues are flexible structures. They have a number of features you can use all together, or
you can leave them empty.

A cue may contain information about the speaker of the dialogue, and how they deliver it.

The most basic of these is the **role**. This is the named origin of the lines of dialogue.
It is recommended that you state the role in upper case letters, eg: GUEST, STAFF.
Inanimate objects can speak too of course. Eg: KETTLE, and PHONE::

    <PHONE> Ring riiing!

The **mode** declares the form in which the act of speech is delivered.
Although it's the most common, *says* is just one of many possible modes of speech.
There are others you might want to use, like *whispers* or *thinks*.
The mode is separated by a colon::

    <GUEST:thinks> I wonder if anyone is going to answer that phone.

Capturing the mode of speech enables different presentation options,
eg: character animations to match the delivery.
Modes of speech should be stated in the simple present, third person form.

**Directives** indicate that there are specific side-effects to the delivery of the dialogue.
They may be used to fire transitions in a state machine, specifying that the speech achieves
progress according to some social protocol.

It's recommended that these directives be stated as present participles
such as *promising* or *declining*::

    <PHONE.announcing> Ring riiing!

Directives, being transitive in nature, sometimes demand objects to their action. So you may
specify the recipient roles of the directive if necessary too::

    <PHONE.announcing@GUEST,STAFF> Ring riiing!

**Parameters** are key-value pairs which modify the presentation of the dialogue. SpeechMark borrows the
Web URL syntax for parameters (first a '?', with '&' as the delimiter).

Their meaning is specific to the application. For example, it might be necessary to specify
some exact timing for the revealing of the text::

    <?pause=3&dwell=0.4>

        Above, there is the sound of footsteps.

        Of snagging on a threadbare carpet.

        Then shuffling down the ancient stairs.

SpeechMark recognises the concept of **fragments**, which also come from URLs. That's the part after a '#'
symbol. You can use the fragment to refer to items in a list::

    <STAFF.proposing#3> What will you have, sir? The special is fish today.

        1. Order the Beef Wellington
        2. Go for the Shepherd's Pie
        3. Try the Dover Sole

Preprocessing
=============

Whitespace
----------

A SpeechMark parser expects certain delimiters to appear only at the beginning of a line.
Therefore, if your marked-up text has been loaded from a file or data structure, you may need to
remove any common indentation and trim the lines of whitespace characters.

Variable substitution
---------------------

It would be very handy for dialogue to reference some objects in scope.
That would allow us to make use of their attributes, eg: ``GUEST.surname``.

Unfortunately, the syntax for variable substitution is language dependent.
Equally the mode of attribute access is application dependent.
Should it be ``GUEST.surname`` or ``GUEST['surname']``?

SpeechMark therefore does not provide this ability, and it must be performed prior to parsing.
Here's an example using Python string formatting, where the context variables are dictionaries::

    <GUEST> I'll have the Fish, please.

    <STAFF> Very good, {GUEST['honorific']} {GUEST['surname']}.


Postprocessing
==============

Pruning
-------

SpeechMark tries not to throw anything away. You might not want that behaviour. Specifically,
you may prefer to remove lines of comment from the HTML5 output.

Since the output is line-based, it's a simple matter to strip out those lines using your favourite programming
language or command line tools.

Extending
---------

SpeechMark does not support extensions. There is no syntax to create custom tags.

However, if you need to transform the output before it gets to the web, you could utilise the
``<code>`` tag for that purpose.

Suppose you have a menu you've defined as a list::

    + `button`[Map](/api/map)
    + `button`[Inventory](/api/inventory)

Here is part of that output::

    <li><p><code>button</code><a href="/api/map">Map</a></p></li>

This could be sufficient to trigger a ``button`` function in your postprocessor which replaces
the bare link with a ``<form>`` and ``<input>`` controls to pop up the map.

Specification
=============

1. General
----------

1.1
```

SpeechMark input must be line-based text, and should have UTF-8 encoding.

1.2
```

Inline markup must consist of pairs of matching delimiters. There must be no line break within them;
all inline markup must terminate on the same line where it begins. Delimiters may not contain other
delimiter pairs. There is no nested markup.

1.3
```

The generated output must be one or more HTML5 ``blockquote`` elements.
All elements must be explicitly terminated.

1.4
```

All output must be placed within blocks. Each block may begin with a cite element. A block may contain one
or more paragraphs. A block may contain a list. Every list item must contain a paragraph.



2. Emphasis
-----------


2.01
````

Emphasis is added using pairs of asterisks.


Single instance::

    *Definitely!*

HTML5 output::

    <blockquote>
    <p><em>Definitely!</em></p>
    </blockquote>


2.02
````

There may be multiple emphasized phrases on a line.


Multiple instances::

    *Definitely* *Definitely!*

HTML5 output::

    <blockquote>
    <p><em>Definitely</em> <em>Definitely!</em></p>
    </blockquote>


2.03
````

Strong text is denoted with underscores.


Single instance::

    _Warning!_

HTML5 output::

    <blockquote>
    <p><strong>Warning!</strong></p>
    </blockquote>


2.04
````

There may be multiple snippets of significant text on one line.


Multiple instances::

    _Warning_ _Warning_!

HTML5 output::

    <blockquote>
    <p><strong>Warning</strong> <strong>Warning</strong>!</p>
    </blockquote>


2.05
````

Code snippets are defined between backticks.


Single instance::

    `git log`

HTML5 output::

    <blockquote>
    <p><code>git log</code></p>
    </blockquote>


2.06
````

There may be multiple code snippets on a line.


Multiple instances::

    `git` `log`

HTML5 output::

    <blockquote>
    <p><code>git</code> <code>log</code></p>
    </blockquote>



3. Hyperlinks
-------------


3.01
````

Hyperlinks are defined by placing link text within square brackets and the link destination
in parentheses. There must be no space between them.
See also https://spec.commonmark.org/0.30/#example-482.


Single instance::

    [Python](https://python.org)

HTML5 output::

    <blockquote>
    <p><a href="https://python.org">Python</a></p>
    </blockquote>


3.02
````

There may be multiple hyperlinks on a line.


Multiple instances::

    [Python](https://python.org) [PyPI](https://pypi.org)

HTML5 output::

    <blockquote>
    <p><a href="https://python.org">Python</a> <a href="https://pypi.org">PyPI</a></p>
    </blockquote>



4. Comments
-----------


4.01
````

Any line beginning with a "#" is a comment.
It is output in its entirety (including delimiter) as an HTML comment.


Single instance::

    # TODO

HTML5 output::

    <blockquote>
    <!-- # TODO -->
    </blockquote>



5. Lists
--------


5.01
````

A line beginning with a '+' character constitutes an
item in an unordered list.


Single list::

    + Hat
    + Gloves


HTML5 output::

    <blockquote>
    <ul>
    <li><p>Hat</p></li>
    <li><p>Gloves</p></li>
    </ul>
    </blockquote>


5.02
````

Ordered lists have lines which begin with one or more digits. Then a dot, and at least one space.


Single list::

    1. Hat
    2. Gloves


HTML5 output::

    <blockquote>
    <ol>
    <li id="1"><p>Hat</p></li>
    <li id="2"><p>Gloves</p></li>
    </ol>
    </blockquote>


5.03
````

Ordered list numbering is exactly as declared. No normalization is performed.


Single list::

    01. Hat
    02. Gloves


HTML5 output::

    <blockquote>
    <ol>
    <li id="01"><p>Hat</p></li>
    <li id="02"><p>Gloves</p></li>
    </ol>
    </blockquote>



6. Cues
-------

A cue mark generates a new block.

6.01
````

A cue mark must appear at the start of a line. No whitespace is allowed in a cue mark.
A generated ``blockquote`` tag may store the original cue string in its ``cite`` attribute.
The string must be appropriately escaped.


6.02
````

All components of a cue are optional.


Anonymous cue::

    <> Once upon a time, far, far away...

HTML5 output::

    <blockquote cite="&lt;&gt;">
    <p>Once upon a time, far, far away...</p>
    </blockquote>


6.03
````

It is recommended that roles be stated in upper case.
When a role is stated, a ``cite`` element must be generated.
The value of the role must be stored in the ``data-role`` attribute of the cite tag.
The role value must be appropriately escaped.


Role only::

    <PHONE> Ring riiing!

HTML5 output::

    <blockquote cite="&lt;PHONE&gt;">
    <cite data-role="PHONE">PHONE</cite>
    <p>Ring riiing!</p>
    </blockquote>


6.04
````

A mode is preceded by a colon. It is stated after any role.
When a mode is stated, a ``cite`` element must be generated.
The value of the mode must be stored in the ``data-mode`` attribute of the cite tag.
The mode value retains its delimiter. The mode value must be appropriately escaped.
Modes of speech should be stated in the third person simple present form.


Role with mode::

    <GUEST:thinks> I wonder if anyone is going to answer that phone.

HTML5 output::

    <blockquote cite="&lt;GUEST:thinks&gt;">
    <cite data-role="GUEST" data-mode=":thinks">GUEST</cite>
    <p>I wonder if anyone is going to answer that phone.</p>
    </blockquote>


6.05
````

There may be multiple directives, each preceded by a dot. They are stated after any role.
When a directive is stated, a ``cite`` element must be generated.
The directives must be stored in the ``data-directives`` attribute of the cite tag.
They retain their delimiters. The directives value must be appropriately escaped.
Directives should be stated as present participles.


Role with directive::

    <PHONE.announcing> Ring riiing!

HTML5 output::

    <blockquote cite="&lt;PHONE.announcing&gt;">
    <cite data-role="PHONE" data-directives=".announcing">PHONE</cite>
    <p>Ring riiing!</p>
    </blockquote>


6.06
````

When a directive is stated, a recipient list may follow it. A recipient list begins with a ``@`` symbol.
The items in the list are separated by commas.
The recipients must be stored in the ``data-directives`` attribute of the cite tag.
They retain their delimiters. The directives value must be appropriately escaped.
Recipients should be stated elsewhere as roles.


Role with directive and recipients::

    <PHONE.announcing@GUEST,STAFF> Ring riiing!

HTML5 output::

    <blockquote cite="&lt;PHONE.announcing@GUEST,STAFF&gt;">
    <cite data-role="PHONE" data-directives=".announcing@GUEST,STAFF">PHONE</cite>
    <p>Ring riiing!</p>
    </blockquote>


6.07
````

A parameter list begins with a ``?`` symbol. It consists of ``key=value`` pairs separated by ampersands.
Should a directive be stated, any parameter list must come after it.
The parameters must be stored in the ``data-parameters`` attribute of the cite tag.
They retain their delimiters. The parameters value must be appropriately escaped.


Parameters only::

    <?pause=3&dwell=0.4> Above, there is the sound of footsteps.

HTML5 output::

    <blockquote cite="&lt;?pause=3&amp;dwell=0.4&gt;">
    <cite data-parameters="?pause=3&amp;dwell=0.4"></cite>
    <p>Above, there is the sound of footsteps.</p>
    </blockquote>


6.08
````

There may be multiple fragments. The first begins with a ``#`` symbol.
All semantics are those of `Web URLs <https://url.spec.whatwg.org>`_.
The fragments appear at the end of any cue mark.
The fragments must be stored in the ``data-fragments`` attribute of the cite tag.
They retain all delimiters. The fragments value must be appropriately escaped.


Role with directive and fragment::

    <STAFF.proposing#3> What will you have, sir? The special is fish today.
        1. Order the Beef Wellington
        2. Go for the Shepherd's Pie
        3. Try the Dover Sole


HTML5 output::

    <blockquote cite="&lt;STAFF.proposing#3&gt;">
    <cite data-role="STAFF" data-directives=".proposing" data-fragments="#3">STAFF</cite>
    <p>What will you have, sir? The special is fish today.</p>
    <ol>
    <li id="1"><p>Order the Beef Wellington</p></li>
    <li id="2"><p>Go for the Shepherd's Pie</p></li>
    <li id="3"><p>Try the Dover Sole</p></li>
    </ol>
    </blockquote>


