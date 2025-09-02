======================
Detailed Documentation
======================

Different Browsers
------------------

HTTP Browser
~~~~~~~~~~~~

The ``p01.testbrowser.browser`` module exposes a ``Browser`` class that
simulates a web browser similar to Mozilla Firefox or IE.

  >>> from p01.testbrowser.browser import Browser
  >>> browser = Browser()
  >>> browser
  <Browser url:None>

This version of the browser object can be used to access any web site just as
you would do using a normal web browser.

WSGI Test Browser
~~~~~~~~~~~~~~~~~

General usage
+++++++++++++

There is also a special version of the ``Browser`` class which uses
`WebTest`_ and can be used to do functional testing of WSGI
applications. It can be imported from ``p01.testbrowser.testing``:

  >>> from p01.testbrowser.tests.helper import demo_app
  >>> demo_app
  <function demo_app at ...>

  >>> browser = Browser('http://localhost/', wsgi_app=demo_app)
  >>> browser
  <Browser url:http://localhost/>

  >>> print(browser.body)
  Hello world!
  ... 

.. _`WebTest`: http://pypi.python.org/pypi/WebTest

You can also use it with zope layers if you

* write a subclass of ``p01.testbrowser.testing.Layer`` and override the
  ``make_wsgi_app`` method, then

* use an instance of the class as the test layer of your test.

Example:

  >>> import p01.testbrowser.testing
  >>> class SimpleLayer(p01.testbrowser.testing.Layer):
  ...     def make_wsgi_app(self):
  ...         return simple_app

Where ``simple_app`` is the callable of your WSGI application.

Testing a Zope 2/Zope 3/Bluebream WSGI application
++++++++++++++++++++++++++++++++++++++++++++++++++

When testing a Zope 2/Zope 3/Bluebream WSGI application you should wrap your
WSGI application under test into
``p01.testbrowser.testing.AuthorizationMiddleware`` as all these application
servers expect basic authentication headers to be base64 encoded. This
middleware handles this for you.

Example when using the layer:

  >>> import p01.testbrowser.testing
  >>> class ZopeSimpleLayer(p01.testbrowser.testing.Layer):
  ...     def make_wsgi_app(self):
  ...         return p01.testbrowser.testing.AuthorizationMiddleware(
  ...             simple_app)

There is also a BrowserLayer in `zope.app.testing.testlayer`_ which does this
for you and includes a ``TransactionMiddleware``, too, which could be handy
when testing a ZODB based application.

.. _`zope.app.wsgi.testlayer` : http://pypi.python.org/pypi/zope.app.wsgi


Bowser Usage
------------

We will test this browser against a WSGI test application:

  >>> from p01.testbrowser.ftests.wsgitestapp import WSGITestApplication
  >>> wsgi_app = WSGITestApplication()

An initial page to load can be passed to the ``Browser`` constructor:

  >>> browser = Browser('http://localhost/@@/testbrowser/simple.html', wsgi_app=wsgi_app)
  >>> browser.url
  'http://localhost/@@/testbrowser/simple.html'

The browser can send arbitrary headers; this is helpful for setting the
"Authorization" header or a language value, so that your tests format values
the way you expect in your tests, if you rely on zope.i18n locale-based
formatting or a similar approach.

  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.addHeader('Accept-Language', 'en-US')

An existing browser instance can also `open` web pages:

  >>> browser.open('http://localhost/@@/testbrowser/simple.html')
  >>> browser.url
  'http://localhost/@@/testbrowser/simple.html'

Once you have opened a web page initially, best practice for writing
testbrowser doctests suggests using 'click' to navigate further (as discussed
below), except in unusual circumstances.

The test browser complies with the IBrowser interface; see
``p01.testbrowser.interfaces`` for full details on the interface.

  >>> from p01.testbrowser import interfaces
  >>> from zope.interface.verify import verifyObject
  >>> verifyObject(interfaces.IBrowser, browser)
  True


Page Contents
-------------

The contents of the current page are available:

  >>> print(browser.contents)
  <html>
    <head>
      <title>Simple Page</title>
    </head>
    <body>
      <h1>Simple Page</h1>
    </body>
  </html>

Making assertions about page contents is easy.

  >>> '<h1>Simple Page</h1>' in browser.contents
  True

Utilizing the doctest facilities, it also possible to do:

  >>> browser.contents
  '...<h1>Simple Page</h1>...'

Note: Unfortunately, ellipsis (...) cannot be used at the beginning of the
output (this is a limitation of doctest).



Checking for HTML
-----------------

Not all URLs return HTML.  Of course our simple page does:

  >>> browser.open('http://localhost/@@/testbrowser/simple.html')
  >>> browser.isHtml
  True

But if we load an image (or other binary file), we do not get HTML:

  >>> browser.open('http://localhost/@@/testbrowser/zope3logo.gif')
  >>> browser.isHtml
  False



HTML Page Title
----------------

Another useful helper property is the title:

  >>> browser.open('http://localhost/@@/testbrowser/simple.html')
  >>> browser.title
  'Simple Page'

If a page does not provide a title, it is simply ``None``:

  >>> browser.open('http://localhost/@@/testbrowser/notitle.html')
  >>> browser.title

However, if the output is not HTML, then an error will occur trying to access
the title:

  >>> browser.open('http://localhost/@@/testbrowser/zope3logo.gif')
  >>> browser.title is None
  True


Headers
-------

As you can see, the `contents` of the browser does not return any HTTP
headers.  The headers are accessible via a separate attribute, which is an
``httplib.HTTPMessage`` instance (httplib is a part of Python's standard
library):

  >>> browser.open('http://localhost/@@/testbrowser/simple.html')
  >>> browser.headers
  <httplib.HTTPMessage instance...>

The headers can be accessed as a string:

  >>> print(browser.headers)
  Status: 200 OK
  Content-Length: 123
  Content-Type: text/html;charset=utf-8

Or as a mapping:

  >>> browser.headers['content-type']
  'text/html;charset=utf-8'


Cookies
-------

When a Set-Cookie header is available, it can be found in the headers, as seen
above.  Here, we use a view that will make the server set cookies with the
values we provide.

  >>> browser.open('http://localhost/set_cookie.html?name=foo&value=bar')
  >>> browser.headers['set-cookie'].replace(';', '')
  'foo=bar'

It is also available in the browser's ``cookies`` attribute.  This is
an extended mapping interface that allows getting, setting, and deleting the
cookies that the browser is remembering *for the current url*.  Here are
a few examples.

  >>> browser.cookies['foo']
  'bar'
  >>> browser.cookies.keys()
  ['foo']
  >>> list(browser.cookies.values())
  ['bar']
  >>> list(browser.cookies.items())
  [('foo', 'bar')]
  >>> 'foo' in browser.cookies
  True
  >>> 'bar' in browser.cookies
  False
  >>> len(browser.cookies)
  1

  >>> print(dict(browser.cookies))
  {'foo': 'bar'}

  >>> key = 'sha'
  >>> browser.cookies[key] = 'zam'
  >>> len(browser.cookies)
  2
  >>> sorted(browser.cookies.items())
  [('foo', 'bar'), ('sha', 'zam')]
  >>> browser.open('http://localhost/get_cookie.html')
  >>> print(browser.headers.get('set-cookie'))
  None
  >>> print(browser.contents) # server got the cookie change
  foo: bar
  sha: zam
  >>> sorted(browser.cookies.items())
  [('foo', 'bar'), ('sha', 'zam')]
  >>> browser.cookies.clearAll()
  >>> len(browser.cookies)
  0

Many more examples, and a discussion of the additional methods available, can
be found in cookies.txt.


Navigation and Link Objectsname

-------------------------------

If you want to simulate clicking on a link, get the link and `click` on it.
In the `navigate.html` file there are several links set up to demonstrate the
capabilities of the link objects and their `click` method.

The simplest way to get a link is via the anchor text.  In other words
the text you would see in a browser (text and url searches are substring
searches):

  >>> browser.open('http://localhost/@@/testbrowser/navigate.html')
  >>> browser.contents
  '...<a href="navigate.html?message=By+Link+Text">Link Text</a>...'
  >>> link = browser.getLink('Link Text')
  >>> link
  <Link text='Link Text'
    url='http://localhost/@@/testbrowser/navigate.html?message=By+Link+Text'>

Link objects comply with the ILink interface.

  >>> verifyObject(interfaces.ILink, link)
  True

Links expose several attributes for easy access.

  >>> link.text
  'Link Text'
  >>> link.tag # links can also be image maps.
  'a'
  >>> link.url # it's normalized
  'http://localhost/@@/testbrowser/navigate.html?message=By+Link+Text'
  >>> dict(link.attrs)
  {'href': 'navigate.html?message=By+Link+Text'}

Links can be "clicked" and the browser will navigate to the referenced URL.

  >>> link.click()
  >>> browser.url
  'http://localhost/@@/testbrowser/navigate.html?message=By+Link+Text'
  >>> browser.contents
  '...Message: <em>By Link Text</em>...'

When finding a link by its text, whitespace is normalized.

  >>> browser.open('http://localhost/@@/testbrowser/navigate.html')
  >>> browser.contents
  '...> Link Text\n    with     Whitespace Normalization (and parens) </...'
  >>> link = browser.getLink('Link Text with Whitespace Normalization '
  ...                        '(and parens)')
  >>> link
  <Link text='Link Text with Whitespace Normalization (and parens)'...>
  >>> link.text
  'Link Text with Whitespace Normalization (and parens)'
  >>> link.click()
  >>> browser.url
  'http://localhost/@@/testbrowser/navigate.html?message=By+Link+Text+with+Normalization'
  >>> browser.contents
  '...Message: <em>By Link Text with Normalization</em>...'

When a link text matches more than one link, by default the first one is
chosen. You can, however, specify the index of the link and thus retrieve a
later matching link:

  >>> browser.getLink('Link Text')
  <Link text='Link Text' ...>

  >>> browser.getLink('Link Text', index=1)
  <Link text='Link Text with Whitespace Normalization (and parens)' ...>

Note that clicking a link object after its browser page has expired will
generate an error.

  >>> link.click()
  Traceback (most recent call last):
  ... 
  ExpiredError

You can also find the link by its URL,

  >>> browser.open('http://localhost/@@/testbrowser/navigate.html')
  >>> browser.contents
  '...<a href="navigate.html?message=By+URL">Using the URL</a>...'

  >>> browser.getLink(url='?message=By+URL').click()
  >>> browser.url
  'http://localhost/@@/testbrowser/navigate.html?message=By+URL'
  >>> browser.contents
  '...Message: <em>By URL</em>...'

or its id:

  >>> browser.open('http://localhost/@@/testbrowser/navigate.html')
  >>> browser.contents
  '...<a href="navigate.html?message=By+Id"
  id="anchorid">By Anchor Id</a>...'

  >>> browser.getLink(id='anchorid').click()
  >>> browser.url
  'http://localhost/@@/testbrowser/navigate.html?message=By+Id'
  >>> browser.contents
  '...Message: <em>By Id</em>...'

You thought we were done here? Not so quickly.  The `getLink` method also
supports image maps, though not by specifying the coordinates, but using the
area's id:

  >>> browser.open('http://localhost/@@/testbrowser/navigate.html')
  >>> link = browser.getLink(id='zope3')
  >>> link.tag
  'area'
  >>> link.click()
  >>> browser.url
  'http://localhost/@@/testbrowser/navigate.html?message=Zope+3+Name'
  >>> browser.contents
  '...Message: <em>Zope 3 Name</em>...'

Getting a nonexistent link raises an exception.

  >>> browser.open('http://localhost/@@/testbrowser/navigate.html')
  >>> browser.getLink('This does not exist')
  Traceback (most recent call last):
  ... 
  LinkNotFoundError

A convenience method is provided to follow links; this uses the same
arguments as `getLink`, but clicks on the link instead of returning the
link object.

  >>> browser.open('http://localhost/@@/testbrowser/navigate.html')
  >>> browser.contents
  '...<a href="navigate.html?message=By+Link+Text">Link Text</a>...'
  >>> browser.follow('Link Text')
  >>> browser.url
  'http://localhost/@@/testbrowser/navigate.html?message=By+Link+Text'
  >>> browser.contents
  '...Message: <em>By Link Text</em>...'

  >>> browser.open('http://localhost/@@/testbrowser/navigate.html')
  >>> browser.follow(url='?message=By+URL')
  >>> browser.url
  'http://localhost/@@/testbrowser/navigate.html?message=By+URL'
  >>> browser.contents
  '...Message: <em>By URL</em>...'

  >>> browser.open('http://localhost/@@/testbrowser/navigate.html')
  >>> browser.follow(id='zope3')
  >>> browser.url
  'http://localhost/@@/testbrowser/navigate.html?message=Zope+3+Name'
  >>> browser.contents
  '...Message: <em>Zope 3 Name</em>...'

Attempting to follow links that don't exist raises the same exception as
asking for the link object:

  >>> browser.follow('This does not exist')
  Traceback (most recent call last):
  ... 
  LinkNotFoundError


Other Navigation
----------------

Like in any normal browser, you can reload a page:

  >>> browser.open('http://localhost/@@/testbrowser/simple.html')
  >>> browser.url
  'http://localhost/@@/testbrowser/simple.html'
  >>> browser.reload()
  >>> browser.url
  'http://localhost/@@/testbrowser/simple.html'

You can also go back:

  >>> browser.open('http://localhost/@@/testbrowser/notitle.html')
  >>> browser.url
  'http://localhost/@@/testbrowser/notitle.html'
  >>> browser.goBack()
  >>> browser.url
  'http://localhost/@@/testbrowser/simple.html'


Controls
--------

One of the most important features of the browser is the ability to inspect
and fill in values for the controls of input forms.  To do so, let's first open
a page that has a bunch of controls:

  >>> browser.open('http://localhost/@@/testbrowser/controls.html')
  >>> print(browser.contents)
  <html>
    <body>
      <h1>Controls Tests</h1>
      <form action="controls.html" method="get">
        <div>
          <label for="text-value">Text Control</label>
          <em></em>
          <input type="text" name="text-value" id="text-value" value="Some Text" />
        </div>
        <div>
          <label for="password-value">Password Control</label>
          <em></em>
          <input type="password" name="password-value" id="password-value"
                 value="Password" />
        </div>
        <div>
          <label for="hidden-value">Hidden Control</label> (label: hee hee)
          <em></em>
          <input type="hidden" name="hidden-value" id="hidden-value"
                 value="Hidden" />
        </div>
        <div>
          <label for="textarea-value">Text Area Control</label>
          <em></em>
          <textarea name="textarea-value" id="textarea-value">
            Text inside
            area!
          </textarea>
        </div>
        <div>
          <label for="file-value">File Control</label>
          <em></em>
          <input type="file" name="file-value" id="file-value" />
        </div>
        <div>
          <label for="single-select-value">Single Select Control</label>
          <em></em>
          <select name="single-select-value" id="single-select-value">
            <option value="1">Uno</option>
            <option value="2">Dos</option>
            <option value="3" label="Third">Tres</option>
          </select>
        </div>
        <div>
          <label for="multi-select-value">Multiple Select Control</label>
          <em></em>
          <select name="multi-select-value" id="multi-select-value"
                  multiple="multiple">
            <option value="1">Un</option>
            <option value="2">Deux</option>
            <option value="3" label="Third">Trois</option>
          </select>
        </div>
        <div>
          <em></em>
          <input type="checkbox" name="single-unvalued-checkbox-value"
                 id="single-unvalued-checkbox" checked="checked" />
          <label for="single-unvalued-checkbox">Single Unvalued Checkbox</label>
        </div>
        <div>
          <em></em>
          <input type="checkbox" name="single-disabled-unvalued-checkbox-value"
                 id="single-disabled-unvalued-checkbox" checked="checked"
                 disabled="disabled" />
          <label for="single-disabled-unvalued-checkbox">
            Single Disabled Unvalued Checkbox
          </label>
        </div>
        <div>
          <em></em>
          <label><input type="checkbox" name="single-valued-checkbox-value"
                        value="1" checked="checked" />Single Valued Checkbox
          </label>
        </div>
        <div>
          (Multi checkbox: options have the labels)
          <em></em>
          <label><input type="checkbox" name="multi-checkbox-value" value="1"
                        checked="checked" /> One</label>
          <input type="checkbox" name="multi-checkbox-value" value="2"
                 id="multi-checkbox-value-2" />
          <label for="multi-checkbox-value-2">Two</label>
          <label><input type="checkbox" name="multi-checkbox-value" value="3"
                        id="multi-checkbox-value-3" checked="checked" />Three
          </label>
          <label for="multi-checkbox-value-3">Third</label>
        </div>
        <div>
          (Radio: options have the labels)
          <em></em>
          <label><input type="radio" name="radio-value" value="1" />Ein</label>
          <input type="radio" name="radio-value" id="radio-value-2" value="2"
                 checked="checked" />
          <label for="radio-value-2">Zwei</label>
          <label><input type="radio" name="radio-value" id="radio-value-3"
                        value="3" /> Drei</label>
          <label for="radio-value-3">Third</label>
        </div>
        <div>
          <label for="image-value">Image Control</label>
          <em></em>
          <em></em>
          <input type="image" name="image-value" id="image-value"
                 src="zope3logo.gif" />
        </div>
        <div>
          <label for="submit-value">Standard Submit Control</label>
    <em></em>
          <input type="submit" name="submit-value" id="submit-value" value="Submit This" />
        </div>
        <div>
          <label for="ambiguous-control-name">Ambiguous Control</label>
          <input type="text" name="ambiguous-control-name"
                 id="ambiguous-control-name" value="First" />
        </div>
        <div>
          <label for="ambiguous-control-name">Ambiguous Control</label>
          <input type="text" name="ambiguous-control-name"
                 id="ambiguous-control-name" value="Second" />
        </div>
        <div>
          <label for="label-needs-normalization">  The Label
            Needs Whitespace Normalization
            Badly  </label>
          <input type="text" name="label-needs-normalization"
                 id="label-needs-normalization" />
        </div>
        <div>
          <label for="non-word-characters">*[non word characters should not
            confuse]</label>
          <input type="text" name="non-word-characters"
                 id="non-word-characters" />
        </div>
        <div>
          <label for="two-labels">Multiple labels really</label>
          <label for="two-labels">really are possible</label>
          <input type="text" name="two-labels"
                 id="two-labels" />
        </div>
        <div>
          <label>Labels can be connected by containing their respective fields
            <input type="text" name="contained-in-label" />
          </label>
        </div>
        <div>
          If you have a select field with a label that overlaps with one of its
          options' labels, that is ambiguous.
          <label for="ambiguous-subcontrol">Sub-control Ambiguity</label>
          <select name="ambiguous-subcontrol" id="ambiguous-subcontrol">
            <option value="">(none)</option>
            <option value="ambiguous">Sub-control Ambiguity Exemplified</option>
          </select>
        </div>
      </form>
    </body>
  </html>
  <BLANKLINE>

Obtaining a Control
~~~~~~~~~~~~~~~~~~~

You look up browser controls with the 'getControl' method.  The default first
argument is 'label', and looks up the form on the basis of any associated
label.

  >>> control = browser.getControl('Text Control')
  >>> control
  <TextControl name='text-value' id='text-value'>

If you request a control that doesn't exist, the code raises a LookupError:

  >>> browser.getControl('Does Not Exist')
  Traceback (most recent call last):
  ... 
  LookupError: label 'Does Not Exist'
  Available items:
    <TextControl name='text-value' id='text-value'>
    <PasswordControl name='password-value' id='password-value'>
    <HiddenControl name='hidden-value' id='hidden-value'>
    <TextAreaControl name='textarea-value' id='textarea-value'>
    <FileControl name='file-value' id='file-value'>
    <SelectListControl name='single-select-value'>
    <SelectControl name='single-select-value' value='1' selected='selected'>
    <SelectControl name='single-select-value' value='2'>
    <SelectControl name='single-select-value' value='3'>
    <SelectListControl name='multi-select-value'>
    <SelectControl name='multi-select-value' value='1'>
    <SelectControl name='multi-select-value' value='2'>
    <SelectControl name='multi-select-value' value='3'>
    <CheckboxListControl name='single-unvalued-checkbox-value'>
    <CheckboxControl name='single-unvalued-checkbox-value' id='single-unvalued-checkbox' value='on' checked='checked'>
    <CheckboxListControl name='single-disabled-unvalued-checkbox-value'>
    <CheckboxControl name='single-disabled-unvalued-checkbox-value' id='single-disabled-unvalued-checkbox' value='on' checked='checked'>
    <CheckboxListControl name='single-valued-checkbox-value'>
    <CheckboxControl name='single-valued-checkbox-value' value='1' checked='checked'>
    <CheckboxListControl name='multi-checkbox-value'>
    <CheckboxControl name='multi-checkbox-value' value='1' checked='checked'>
    <CheckboxControl name='multi-checkbox-value' id='multi-checkbox-value-2' value='2'>
    <CheckboxControl name='multi-checkbox-value' id='multi-checkbox-value-3' value='3' checked='checked'>
    <RadioListControl name='radio-value'>
    <RadioControl name='radio-value' value='1'>
    <RadioControl name='radio-value' id='radio-value-2' value='2' checked="checked">
    <RadioControl name='radio-value' id='radio-value-3' value='3'>
    <ImageControl name='image-value' id='image-value'>
    <SubmitControl name='submit-value' id='submit-value'>
    <TextControl name='ambiguous-control-name' id='ambiguous-control-name'>
    <TextControl name='ambiguous-control-name' id='ambiguous-control-name'>
    <TextControl name='label-needs-normalization' id='label-needs-normalization'>
    <TextControl name='non-word-characters' id='non-word-characters'>
    <TextControl name='two-labels' id='two-labels'>
    <TextControl name='contained-in-label'>
    <SelectListControl name='ambiguous-subcontrol'>
    <SelectControl name='ambiguous-subcontrol' value='' selected='selected'>
    <SelectControl name='ambiguous-subcontrol' value='ambiguous'>

If you request a control with an ambiguous lookup, the code raises an
AmbiguityError.

  >>> browser.getControl('Ambiguous Control')
  Traceback (most recent call last):
  ... 
  AmbiguityError: label 'Ambiguous Control' matches:
    <TextControl name='ambiguous-control-name' id='ambiguous-control-name'>
    <TextControl name='ambiguous-control-name' id='ambiguous-control-name'>

This is also true if an option in a control is ambiguous in relation to
the control itself.

  >>> browser.getControl('Sub-control Ambiguity')
  Traceback (most recent call last):
  ... 
  AmbiguityError: label 'Sub-control Ambiguity' matches:
    <SelectListControl name='ambiguous-subcontrol'>
    <SelectControl name='ambiguous-subcontrol' value='ambiguous'>

Ambiguous controls may be specified using an index value.  We use the control's
value attribute to show the two controls; this attribute is properly introduced
below.

  >>> browser.getControl('Ambiguous Control', index=0)
  <TextControl name='ambiguous-control-name' id='ambiguous-control-name'>
  >>> browser.getControl('Ambiguous Control', index=0).value
  'First'

  >>> browser.getControl('Ambiguous Control', index=1).value
  'Second'

  >>> browser.getControl('Sub-control Ambiguity', index=0)
  <SelectListControl name='ambiguous-subcontrol'>

  >>> browser.getControl('Sub-control Ambiguity', index=1).optionValue
  'ambiguous'

  >>> browser.getControl('Sub-control Ambiguity', index=2)
  Traceback (most recent call last):
  ... 
  LookupError: label 'Sub-control Ambiguity'
  Index 2 out of range, available choices are 0...1
    0: <SelectListControl name='ambiguous-subcontrol'>
    1: <SelectControl name='ambiguous-subcontrol' value='ambiguous'>

Label searches are against stripped, whitespace-normalized, no-tag versions of
the text. Text applied to searches is also stripped and whitespace normalized.
The search finds results if the text search finds the whole words of your
text in a label.  Thus, for instance, a search for 'Add' will match the label
'Add a Client' but not 'Address'.  Case is honored.

  >>> browser.getControl('Label Needs Whitespace Normalization')
  <TextControl name='label-needs-normalization' id='label-needs-normalization'>
  >>> browser.getControl('label needs whitespace normalization')
  Traceback (most recent call last):
  ... 
  LookupError: label 'label needs whitespace normalization'
  ... 
  >>> browser.getControl(' Label  Needs Whitespace    ')
  <TextControl name='label-needs-normalization' id='label-needs-normalization'>
  >>> browser.getControl('Whitespace')
  <TextControl name='label-needs-normalization' id='label-needs-normalization'>
  >>> browser.getControl('hitespace')
  Traceback (most recent call last):
  ... 
  LookupError: label 'hitespace'
  ... 
  >>> browser.getControl('[non word characters should not confuse]')
  <TextControl name='non-word-characters' id='non-word-characters'>

Multiple labels can refer to the same control (simply because that is possible
in the HTML 4.0 spec).

  >>> browser.getControl('Multiple labels really')
  <TextControl name='two-labels' id='two-labels'>
  >>> browser.getControl('really are possible')
  <TextControl name='two-labels' id='two-labels'>
  >>> browser.getControl('really') # OK: ambiguous labels, but not ambiguous control
  <TextControl name='two-labels' id='two-labels'>

A label can be connected with a control using the 'for' attribute and also by
containing a control.

  >>> browser.getControl(
  ...     'Labels can be connected by containing their respective fields')
  <TextControl name='contained-in-label'>

Get also accepts one other search argument, 'name'.  Only one of 'label' and
'name' may be used at a time.  The 'name' keyword searches form field names.

  >>> browser.getControl(name='text-value')
  <TextControl name='text-value' id='text-value'>
  >>> browser.getControl(name='ambiguous-control-name')
  Traceback (most recent call last):
  ... 
  AmbiguityError: name 'ambiguous-control-name' matches:
    <TextControl name='ambiguous-control-name' id='ambiguous-control-name'>
    <TextControl name='ambiguous-control-name' id='ambiguous-control-name'>

  >>> browser.getControl(name='does-not-exist')
  Traceback (most recent call last):
  ... 
  LookupError: name 'does-not-exist'
  Available items:
    <TextControl name='text-value' id='text-value'>
    <PasswordControl name='password-value' id='password-value'>
    <HiddenControl name='hidden-value' id='hidden-value'>
    <TextAreaControl name='textarea-value' id='textarea-value'>
    <FileControl name='file-value' id='file-value'>
    <SelectListControl name='single-select-value'>
    <SelectListControl name='multi-select-value'>
    <CheckboxListControl name='single-unvalued-checkbox-value'>
    <CheckboxListControl name='single-disabled-unvalued-checkbox-value'>
    <CheckboxListControl name='single-valued-checkbox-value'>
    <CheckboxListControl name='multi-checkbox-value'>
    <RadioListControl name='radio-value'>
    <ImageControl name='image-value' id='image-value'>
    <SubmitControl name='submit-value' id='submit-value'>
    <TextControl name='ambiguous-control-name' id='ambiguous-control-name'>
    <TextControl name='ambiguous-control-name' id='ambiguous-control-name'>
    <TextControl name='label-needs-normalization' id='label-needs-normalization'>
    <TextControl name='non-word-characters' id='non-word-characters'>
    <TextControl name='two-labels' id='two-labels'>
    <TextControl name='contained-in-label'>
    <SelectListControl name='ambiguous-subcontrol'>

  >>> browser.getControl(name='ambiguous-control-name', index=1).value
  'Second'

Combining 'label' and 'name' raises a ValueError, as does supplying neither of
them.

  >>> browser.getControl(label='Ambiguous Control', name='ambiguous-control-name')
  Traceback (most recent call last):
  ... 
  ValueError: Supply one and only one of "label" and "name" as arguments
  >>> browser.getControl()
  Traceback (most recent call last):
  ... 
  ValueError: Supply one and only one of "label" and "name" as arguments

Radio and checkbox fields are unusual in that their labels and names may point
to different objects: names point to logical collections of radio buttons or
checkboxes, but labels may only be used for individual choices within the
logical collection.  This means that obtaining a radio button by label gets a
different object than obtaining the radio collection by name.  Select options
may also be searched by label.

  >>> browser.getControl(name='radio-value')
  <RadioListControl name='radio-value'>
  >>> browser.getControl('Zwei')
  <RadioControl name='radio-value' id='radio-value-2' value='2' checked="checked">
  >>> browser.getControl('One')
  <CheckboxControl name='multi-checkbox-value' value='1' checked='checked'>
  >>> browser.getControl('Tres')
  <SelectControl name='single-select-value' value='3'>

Characteristics of controls and subcontrols are discussed below.


Control Objects
~~~~~~~~~~~~~~~

Controls provide IControl.

  >>> ctrl = browser.getControl('Text Control')
  >>> ctrl
  <TextControl name='text-value' id='text-value'>
  >>> verifyObject(interfaces.IControl, ctrl)
  True

They have several useful attributes:

- the name as which the control is known to the form:

  >>> ctrl.name
  'text-value'

- the value of the control, which may also be set:

  >>> ctrl.value
  'Some Text'
  >>> ctrl.value = 'More Text'
  >>> ctrl.value
  'More Text'

- the type of the control:

  >>> ctrl.type
  'text'

- a flag describing whether the control is disabled:

  >>> ctrl.disabled
  False

- and a flag to tell us whether the control can have multiple values:

  >>> ctrl.multiple
  False

Additionally, controllers for select, radio, and checkbox provide IListControl.
These fields have four other attributes and an additional method:

  >>> ctrl = browser.getControl('Multiple Select Control')
  >>> ctrl
  <SelectListControl name='multi-select-value'>
  >>> ctrl.disabled
  False
  >>> ctrl.multiple
  True
  >>> verifyObject(interfaces.IListControl, ctrl)
  True

- 'options' lists all available value options.

  >>> ctrl.options
  ['1', '2', '3']

- 'displayOptions' lists all available options by label.  The 'label'
  attribute on an option has precedence over its contents, which is why
  our last option is 'Third' in the display.

  >>> ctrl.displayOptions
  ['Un', 'Deux', 'Third']

- 'displayValue' lets you get and set the displayed values of the control
  of the select box, rather than the actual values.

  >>> ctrl.value
  []
  >>> ctrl.displayValue
  []
  >>> ctrl.displayValue = ['Un', 'Deux']
  >>> ctrl.displayValue
  ['Un', 'Deux']
  >>> ctrl.value
  ['1', '2']

- 'controls' gives you a list of the subcontrol objects in the control
  (subcontrols are discussed below).

  >>> ctrl.controls
  [<SelectControl name='multi-select-value' value='1' selected='selected'>,
   <SelectControl name='multi-select-value' value='2' selected='selected'>,
   <SelectControl name='multi-select-value' value='3'>]

- The 'getControl' method lets you get subcontrols by their label or their value.

  >>> ctrl.getControl('Un')
  <SelectControl name='multi-select-value' value='1' selected='selected'>
  >>> ctrl.getControl('Deux')
  <SelectControl name='multi-select-value' value='2' selected='selected'>
  >>> ctrl.getControl('Trois') # label attribute
  <SelectControl name='multi-select-value' value='3'>
  >>> ctrl.getControl('Third') # contents
  <SelectControl name='multi-select-value' value='3'>
  >>> browser.getControl('Third') # ambiguous in the browser, so useful
  Traceback (most recent call last):
  ... 
  AmbiguityError: label 'Third' matches:
    <SelectControl name='single-select-value' value='3'>
    <SelectControl name='multi-select-value' value='3'>
    <CheckboxControl name='multi-checkbox-value' id='multi-checkbox-value-3' value='3' checked='checked'>
    <RadioControl name='radio-value' id='radio-value-3' value='3'>

Finally, submit controls provide ISubmitControl, and image controls provide
IImageSubmitControl, which extents ISubmitControl.  These both simply add a
'click' method.  For image submit controls, you may also provide a coordinates
argument, which is a tuple of (x, y).  These submit the forms, and are
demonstrated below as we examine each control individually.


ItemControl Objects
~~~~~~~~~~~~~~~~~~~

As introduced briefly above, using labels to obtain elements of a logical
radio button or checkbox collection returns item controls, which are parents.
Manipulating the value of these controls affects the parent control.

  >>> browser.getControl(name='radio-value').value
  ['2']
  >>> browser.getControl('Zwei').optionValue # read-only.
  '2'
  >>> browser.getControl('Zwei').selected
  True
  >>> verifyObject(interfaces.IItemControl, browser.getControl('Zwei'))
  True
  >>> browser.getControl('Ein').selected = True
  >>> browser.getControl('Ein').selected
  True
  >>> browser.getControl('Zwei').selected
  False
  >>> browser.getControl(name='radio-value').value
  ['1']
  >>> browser.getControl('Ein').selected = False
  >>> browser.getControl(name='radio-value').value
  []
  >>> browser.getControl('Zwei').selected = True

Checkbox collections behave similarly, as shown below.

Controls with subcontrols--


Various Controls
~~~~~~~~~~~~~~~~

The various types of controls are demonstrated here.

- Text Control

  The text control we already introduced above.

- Password Control

  >>> ctrl = browser.getControl('Password Control')
  >>> ctrl
  <PasswordControl name='password-value' id='password-value'>
  >>> verifyObject(interfaces.IControl, ctrl)
  True
  >>> ctrl.value
  'Password'
  >>> ctrl.value = 'pass now'
  >>> ctrl.value
  'pass now'
  >>> ctrl.disabled
  False
  >>> ctrl.multiple
  False

- Hidden Control

  >>> ctrl = browser.getControl(name='hidden-value')
  >>> ctrl
  <HiddenControl name='hidden-value' id='hidden-value'>
  >>> verifyObject(interfaces.IControl, ctrl)
  True
  >>> ctrl.value
  'Hidden'
  >>> ctrl.value = 'More Hidden'
  >>> ctrl.disabled
  False
  >>> ctrl.multiple
  False

- Text Area Control

  >>> ctrl = browser.getControl('Text Area Control')
  >>> ctrl
  <TextAreaControl name='textarea-value' id='textarea-value'>
  >>> verifyObject(interfaces.IControl, ctrl)
  True
  >>> ctrl.value
  '        Text inside\n        area!\n      '
  >>> ctrl.value = 'A lot of\n text.'
  >>> ctrl.disabled
  False
  >>> ctrl.multiple
  False

- File Control

  File controls are used when a form has a file-upload field.
  To specify data, call the add_file method, passing:

  - A file-like object

  - a content type, and

  - a file name

  >>> ctrl = browser.getControl('File Control')
  >>> ctrl
  <FileControl name='file-value' id='file-value'>
  >>> verifyObject(interfaces.IControl, ctrl)
  True
  >>> ctrl.value is None
  True
  >>> import io

  >>> ctrl.add_file(io.BytesIO(b'File contents'),
  ...               'text/plain', 'test.txt')

  The file control (like the other controls) also knows if it is disabled
  or if it can have multiple values.

  >>> ctrl.disabled
  False
  >>> ctrl.multiple
  False

- Selection Control (Single-Valued)

  >>> ctrl = browser.getControl('Single Select Control')
  >>> ctrl
  <SelectListControl name='single-select-value'>
  >>> verifyObject(interfaces.IListControl, ctrl)
  True
  >>> ctrl.value
  ['1']
  >>> ctrl.value = ['2']
  >>> ctrl.disabled
  False
  >>> ctrl.multiple
  False
  >>> ctrl.options
  ['1', '2', '3']
  >>> ctrl.displayOptions
  ['Uno', 'Dos', 'Third']

  >>> ctrl.displayValue
  ['Dos']
  >>> ctrl.displayValue = ['Tres']
  >>> ctrl.displayValue
  ['Third']
  >>> ctrl.displayValue = ['Dos']
  >>> ctrl.displayValue
  ['Dos']
  >>> ctrl.displayValue = ['Third']
  >>> ctrl.displayValue
  ['Third']
  >>> ctrl.value
  ['3']

- Selection Control (Multi-Valued)

  This was already demonstrated in the introduction to control objects above.

- Checkbox Control (Single-Valued; Unvalued)

  >>> ctrl = browser.getControl(name='single-unvalued-checkbox-value')
  >>> ctrl
  <CheckboxListControl name='single-unvalued-checkbox-value'>
  >>> verifyObject(interfaces.IListControl, ctrl)
  True
  >>> ctrl.value
  True
  >>> ctrl.value = False
  >>> ctrl.disabled
  False
  >>> ctrl.multiple
  True
  >>> ctrl.options
  [True]
  >>> ctrl.displayOptions
  ['Single Unvalued Checkbox']
  >>> ctrl.displayValue
  []
  >>> verifyObject(
  ...     interfaces.IItemControl,
  ...     browser.getControl('Single Unvalued Checkbox'))
  True
  >>> browser.getControl('Single Unvalued Checkbox').optionValue
  'on'
  >>> browser.getControl('Single Unvalued Checkbox').selected
  False
  >>> ctrl.displayValue = ['Single Unvalued Checkbox']
  >>> ctrl.displayValue
  ['Single Unvalued Checkbox']

  >>> browser.getControl('Single Unvalued Checkbox')
  <CheckboxControl name='single-unvalued-checkbox-value'
                   id='single-unvalued-checkbox'
                   value='on' checked='checked'>

  >>> browser.getControl('Single Unvalued Checkbox').selected
  True

  >>> browser.getControl('Single Unvalued Checkbox').selected = False
  >>> browser.getControl('Single Unvalued Checkbox').selected
  False

Note: we must get the control againfor get the real value. Otherwise we will
get the old value stored in the control.

  >>> ctrl = browser.getControl(name='single-unvalued-checkbox-value')
  >>> ctrl.displayValue
  []

  >>> browser.getControl(
  ...     name='single-disabled-unvalued-checkbox-value').disabled
  True

- Checkbox Control (Single-Valued, Valued)

  >>> ctrl = browser.getControl(name='single-valued-checkbox-value')
  >>> ctrl
  <CheckboxListControl name='single-valued-checkbox-value'>
  >>> verifyObject(interfaces.IListControl, ctrl)
  True
  >>> ctrl.value
  ['1']
  >>> ctrl.value = []
  >>> ctrl.disabled
  False
  >>> ctrl.multiple
  True
  >>> ctrl.options
  ['1']
  >>> ctrl.displayOptions
  ['Single Valued Checkbox']
  >>> ctrl.displayValue
  []
  >>> verifyObject(
  ...     interfaces.IItemControl,
  ...     browser.getControl('Single Valued Checkbox'))
  True
  >>> browser.getControl('Single Valued Checkbox').selected
  False
  >>> browser.getControl('Single Valued Checkbox').optionValue
  '1'
  >>> ctrl.displayValue = ['Single Valued Checkbox']
  >>> ctrl.displayValue
  ['Single Valued Checkbox']
  >>> browser.getControl('Single Valued Checkbox').selected
  True
  >>> browser.getControl('Single Valued Checkbox').selected = False
  >>> browser.getControl('Single Valued Checkbox').selected
  False

Note: we must get the control againfor get the real value. Otherwise we will
get the old value stored in the control.

  >>> ctrl = browser.getControl(name='single-valued-checkbox-value')
  >>> ctrl.displayValue
  []

- Checkbox Control (Multi-Valued)

  >>> ctrl = browser.getControl(name='multi-checkbox-value')
  >>> ctrl
  <CheckboxListControl name='multi-checkbox-value'>
  >>> verifyObject(interfaces.IListControl, ctrl)
  True
  >>> ctrl.value
  ['1', '3']
  >>> ctrl.value = ['1', '2']
  >>> ctrl.disabled
  False
  >>> ctrl.multiple
  True
  >>> ctrl.options
  ['1', '2', '3']
  >>> ctrl.displayOptions
  ['One', 'Two', 'Three']
  >>> ctrl.displayValue
  ['One', 'Two']
  >>> ctrl.displayValue = ['Two']
  >>> ctrl.value
  ['2']
  >>> browser.getControl('Two').optionValue
  '2'
  >>> browser.getControl('Two').selected
  True
  >>> verifyObject(interfaces.IItemControl, browser.getControl('Two'))
  True
  >>> browser.getControl('Three').selected = True
  >>> browser.getControl('Three').selected
  True
  >>> browser.getControl('Two').selected
  True

  >>> ctrl = browser.getControl(name='multi-checkbox-value')
  >>> ctrl.value
  ['2', '3']
  >>> browser.getControl('Two').selected = False
  >>> ctrl.value
  ['3']
  >>> browser.getControl('Three').selected = False

  >>> ctrl = browser.getControl(name='multi-checkbox-value')
  >>> ctrl.value
  []

- Radio Control

  This is how you get a radio button based control:

  >>> ctrl = browser.getControl(name='radio-value')

  This shows the existing value of the control, as it was in the
  HTML received from the server:

  >>> ctrl.value
  ['2']

  We can then unselect it:

  >>> ctrl.value = []
  >>> ctrl.value
  []

  We can also reselect it:

  >>> ctrl.value = ['2']
  >>> ctrl.value
  ['2']

  displayValue shows the text the user would see next to the
  control:

  >>> ctrl.displayValue
  ['Zwei']

  This is just unit testing:

  >>> ctrl
  <RadioListControl name='radio-value'>
  >>> verifyObject(interfaces.IListControl, ctrl)
  True
  >>> ctrl.disabled
  False
  >>> ctrl.multiple
  False
  >>> ctrl.options
  ['1', '2', '3']
  >>> ctrl.displayOptions
  ['Ein', 'Zwei', 'Drei']
  >>> ctrl.displayValue = ['Ein']
  >>> ctrl.value
  ['1']
  >>> ctrl.displayValue
  ['Ein']

  The radio control subcontrols were illustrated above.

- Image Control

  >>> ctrl = browser.getControl(name='image-value')
  >>> ctrl
  <ImageControl name='image-value' id='image-value'>

  >>> verifyObject(interfaces.IImageSubmitControl, ctrl)
  True

  >>> ctrl.value
  ''

  >>> ctrl.disabled
  False

  >>> ctrl.multiple
  False

- Submit Control

  >>> ctrl = browser.getControl(name='submit-value')
  >>> ctrl
  <SubmitControl name='submit-value' id='submit-value'>

  >>> browser.getControl('Submit This') # value of submit button is a label
  <SubmitControl name='submit-value' id='submit-value'>

  >>> browser.getControl('Standard Submit Control') # label tag is legal
  <SubmitControl name='submit-value' id='submit-value'>

  >>> browser.getControl('Submit') # multiple labels, but same control
  <SubmitControl name='submit-value' id='submit-value'>

  >>> verifyObject(interfaces.ISubmitControl, ctrl)
  True

  >>> ctrl.value
  'Submit This'

  >>> ctrl.disabled
  False

  >>> ctrl.multiple
  False


select
Using Submitting Controls
~~~~~~~~~~~~~~~~~~~~~~~~~

Both the submit and image type should be clickable and submit the form:

  >>> browser.open('http://localhost/@@/testbrowser/controls.html')
  >>> browser.getControl('Text Control').value = 'Other Text'
  >>> browser.getControl('Text Control').value
  'Other Text'

  >>> browser.getControl('Submit') # multiple labels, but same control
  <SubmitControl name='submit-value' id='submit-value'>

  >>> browser.getControl('Submit').click()
  >>> print(browser.contents)
  <html>
  ... 
  <em>Other Text</em>
  <input type="text" name="text-value" id="text-value" value="Some Text" />
  ... 
  <em>Submit This</em>
  <input type="submit" name="submit-value" id="submit-value" value="Submit This" />
  ... 
  </html>

Note that if you click a submit object after the associated page has expired,
you will get an error.

  >>> browser.open('http://localhost/@@/testbrowser/controls.html')
  >>> ctrl = browser.getControl('Submit')
  >>> ctrl.click()
  >>> ctrl.click()
  Traceback (most recent call last):
  ... 
  ExpiredError

All the above also holds true for the image control:

  >>> browser.open('http://localhost/@@/testbrowser/controls.html')
  >>> browser.getControl('Text Control').value = 'Other Text'
  >>> browser.getControl(name='image-value')
  <ImageControl name='image-value' id='image-value'>

  >>> browser.getControl(name='image-value').click()
  >>> print(browser.contents)
  <html>
  ... 
  <em>Other Text</em>
  <input type="text" name="text-value" id="text-value" value="Some Text" />
  ... 
  <em>1</em>
  <em>1</em>
  <input type="image" name="image-value" id="image-value"
         src="zope3logo.gif" />
  ... 
  </html>

  >>> browser.open('http://localhost/@@/testbrowser/controls.html')
  >>> ctrl = browser.getControl(name='image-value')
  >>> ctrl.click()
  >>> ctrl.click()
  Traceback (most recent call last):
  ... 
  ExpiredError

But when sending an image, you can also specify the coordinate you clicked:

  >>> browser.open('http://localhost/@@/testbrowser/controls.html')
  >>> browser.getControl(name='image-value').click((50,25))
  >>> print(browser.contents)
  <html>
  ... 
  <em>50</em>
  <em>25</em>
  <input type="image" name="image-value" id="image-value"
         src="zope3logo.gif" />
  ... 
  </html>


Pages Without Controls
~~~~~~~~~~~~~~~~~~~~~~

What would happen if we tried to look up a control on a page that has none?

  >>> browser.open('http://localhost/@@/testbrowser/simple.html')
  >>> browser.getControl('anything')
  Traceback (most recent call last):
  ... 
  LookupError: label 'anything'
  There are no form items in the HTML


Forms
-----

Because pages can have multiple forms with like-named controls, it is sometimes
necessary to access forms by name or id.  The browser's `forms` attribute can
be used to do so.  The key value is the form's name or id.  If more than one
form has the same name or id, the first one will be returned.

  >>> browser.open('http://localhost/@@/testbrowser/forms.html')
  >>> form = browser.getForm(name='one')

Form instances conform to the IForm interface.

  >>> verifyObject(interfaces.IForm, form)
  True

The form exposes several attributes related to forms:

- The name of the form:

  >>> form.name
  'one'

- The id of the form:

  >>> form.id
  '1'

- The action (target URL) when the form is submitted:

  >>> form.action
  'http://localhost/@@/testbrowser/forms.html'

- The method (HTTP verb) used to transmit the form data:

  >>> form.method
  'GET'

Besides those attributes, you have also a couple of methods.  Like for the
browser, you can get control objects, but limited to the current form...

  >>> form.getControl(name='text-value')
  <TextControl name='text-value'>

  ... and submit the form.

  >>> form.submit('Submit')
  >>> print(browser.contents)
  <html>
  ... 
  <em>First Text</em>
  ... 
  </html>

Submitting also works without specifying a control, as shown below, which is
it's primary reason for existing in competition with the control submission
discussed above.

Now let me show you briefly that looking up forms is sometimes important.  In
the `forms.html` template, we have four forms all having a text control named
`text-value`.  Now, if I use the browser's `get` method,

  >>> browser.getControl(name='text-value')
  Traceback (most recent call last):
  ... 
  AmbiguityError: name 'text-value' matches:
    <TextControl name='text-value'>
    <TextControl name='text-value'>
    <TextControl name='text-value' id='text-value-3'>
    <TextControl name='text-value' id='text-value-4'>

I'll always get an ambiguous form field.  I can use the index argument, or
with the `getForm` method I can disambiguate by searching only within a given
form:

  >>> form = browser.getForm('2')
  >>> form.getControl(name='text-value').value
  'Second Text'
  >>> form.submit('Submit')
  >>> browser.contents
  '...<em>Second Text</em>...'
  >>> form = browser.getForm('2')
  >>> form.getControl('Submit').click()
  >>> browser.contents
  '...<em>Second Text</em>...'
  >>> browser.getForm('3').getControl('Text Control').value
  'Third Text'

The last form on the page does not have a name, an id, or a submit button.
Working with it is still easy, thanks to a index attribute that guarantees
order.  (Forms without submit buttons are sometimes useful for JavaScript.)

  >>> form = browser.getForm(index=3)
  >>> form.submit()
  >>> browser.contents
  '...<em>Fourth Text</em>...<em>Submitted without the submit button.</em>...'

If a form is requested that does not exists, an exception will be raised.

  >>> form = browser.getForm('does-not-exist')
  Traceback (most recent call last):
  LookupError

If the HTML page contains only one form, no arguments to `getForm` are
needed:

  >>> oneform = Browser(wsgi_app=wsgi_app)
  >>> oneform.open('http://localhost/@@/testbrowser/oneform.html')
  >>> form = oneform.getForm()

If the HTML page contains more than one form, `index` is needed to
disambiguate if no other arguments are provided:

  >>> browser.getForm()
  Traceback (most recent call last):
  ValueError: if no other arguments are given, index is required.


Submitting a posts body directly
--------------------------------

In addition to the open method, Browser has a ``post``
method that allows a request body to be supplied.  This method is particularly
helpful when testing AJAX methods.

Let's visit a page that echos some interesting values from it's request:

  >>> browser.open('http://localhost/echo.html')
  >>> print(browser.contents)
  HTTP_ACCEPT_LANGUAGE: en-US
  HTTP_CONNECTION: close
  HTTP_HOST: localhost
  HTTP_USER_AGENT: Python-urllib/2.4
  PATH_INFO: /echo.html
  REQUEST_METHOD: GET
  Body: ''

Now, we'll try a post.  The post method takes a URL, a data string,
and an optional content type.  If we just pass a string, then
a URL-encoded query string is assumed:

  >>> browser.post('http://localhost/echo.html', 'x=1&y=2')
  >>> print(browser.contents)
  CONTENT_LENGTH: 7
  CONTENT_TYPE: application/x-www-form-urlencoded
  HTTP_ACCEPT_LANGUAGE: en-US
  HTTP_CONNECTION: close
  HTTP_HOST: localhost
  HTTP_USER_AGENT: Python-urllib/2.4
  PATH_INFO: /echo.html
  REQUEST_METHOD: POST
  x: 1
  y: 2
  Body: ''

The body is empty because it is consumed to get form data.

We can pass a content-type explicitly:

  >>> browser.post('http://localhost/echo.html',
  ...              '{"x":1,"y":2}', 'application/x-javascript')
  >>> print(browser.contents)
  CONTENT_LENGTH: 13
  CONTENT_TYPE: application/x-javascript
  HTTP_ACCEPT_LANGUAGE: en-US
  HTTP_CONNECTION: close
  HTTP_HOST: localhost
  HTTP_USER_AGENT: Python-urllib/2.4
  PATH_INFO: /echo.html
  REQUEST_METHOD: POST
  Body: '{"x":1,"y":2}'

Here, the body is left in place because it isn't form data.


Performance Testing
-------------------

Browser objects keep up with how much time each request takes.  This can be
used to ensure a particular request's performance is within a tolerable range.
Be very careful using raw seconds, cross-machine differences can be huge,
pystones is usually a better choice.

  >>> browser.open('http://localhost/@@/testbrowser/simple.html')
  >>> browser.lastRequestSeconds < 10 # really big number for safety
  True
  >>> browser.lastRequestPystones < 10000 # really big number for safety
  True


Handling Errors
---------------

Often WSGI middleware or the application itself gracefully handle application
errors, such as invalid URLs:

  >>> browser.open('http://localhost/invalid')
  Traceback (most recent call last):
  ... 
  HTTPError: HTTP Error 404: Not Found

Note that the above error was thrown by ``mechanize`` and not by the
application.  For debugging purposes, however, it can be very useful to see the
original exception caused by the application.  In those cases you can set the
``handleErrors`` property of the browser to ``False``.  It is defaulted to
``True``:

  >>> browser.handleErrors
  True

So when we tell the application not to handle the errors,

  >>> browser.handleErrors = False

we get a different, internal error from the application:

  >>> browser.open('http://localhost/invalid')
  Traceback (most recent call last):
  ... 
  NotFound: /invalid

NB: Setting the handleErrors attribute to False will only change anything if
  the WSGI application obeys the wsgi.handleErrors or paste.throw_errors
  WSGI environment variables. i.e. it does not catch and handle the original
  exception when these are set appropriately.

When the testbrowser is raising HttpErrors, the errors still hit the test.
Sometimes we don't want that to happen, in situations where there are edge
cases that will cause the error to be predictably but infrequently raised.
Time is a primary cause of this.

To get around this, one can set the raiseHttpErrors to False.

  >>> browser.handleErrors = True
  >>> browser.raiseHttpErrors = False

This will cause HttpErrors not to propagate.

  >>> browser.open('http://localhost/invalid')

The headers are still there, though.

  >>> '404 Not Found' in str(browser.headers)
  True

If we don't handle the errors, and allow internal ones to propagate, however,
this flag doesn't affect things.

  >>> browser.handleErrors = False
  >>> browser.open('http://localhost/invalid')
  Traceback (most recent call last):
  ... 
  NotFound: /invalid

  >>> browser.raiseHttpErrors = True


Hand-Holding
------------

Instances of the various objects ensure that users don't set incorrect
instance attributes accidentally.

  >>> browser.nonexistant = None
  Traceback (most recent call last):
  ... 
  AttributeError: 'Browser' object has no attribute 'nonexistant'

  >>> form.nonexistant = None
  Traceback (most recent call last):
  ... 
  AttributeError: 'Form' object has no attribute 'nonexistant'

  >>> control.nonexistant = None
  Traceback (most recent call last):
  ... 
  AttributeError: 'TextControl' object has no attribute 'nonexistant'

  >>> link.nonexistant = None
  Traceback (most recent call last):
  ... 
  AttributeError: 'Link' object has no attribute 'nonexistant'


HTTPS support
-------------

Depending on the scheme of the request the variable wsgi.url_scheme will be set
correctly on the request:

  >>> browser.open('http://localhost/echo_one.html?var=wsgi.url_scheme')
  >>> print(browser.contents)
  'http'

  >>> browser.open('https://localhost/echo_one.html?var=wsgi.url_scheme')
  >>> print(browser.contents)
  'https'

see http://www.python.org/dev/peps/pep-3333/ for details.
