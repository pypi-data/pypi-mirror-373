======
README
======

This package offers a replacement for the cgi.FieldStorage implementation. It
tries to be fast.

WARNING:
Right now there are tests only for well-formed requests.
If someone has the time and resources (maybe samples) improve that!


standard_library.install_aliases()
  >>> import os
  >>> import io
  >>> from pprint import pprint
  >>> import p01.cgi
  >>> from p01.cgi import interfaces
  >>> data = os.path.abspath(os.path.join(__file__, '..', 'data'))


SimpleField
-----------

A simple field can store a name and value:

  >>> from p01.cgi.parser import SimpleField


MultiPartField
--------------

The multi part field can store multi part content including file upload data


validBoundary
-------------

Checks if a boundary specified by the request is valid.

  >>> from p01.cgi.parser import validBoundary


parseHeader
-----------

The parse header method can extract header data.
Content-type and a dictionary of options.


parseMultiParts
---------------

Let's see if we can parse some input streams:

  >>> from p01.cgi.parser import parseMultiParts
  >>> testFilePath = os.path.join(data, 'test.txt')
  >>> testFile = open(testFilePath, 'rb')

Now we can use the file pointer:

  >>> mpf = parseMultiParts(testFile)
  >>> mpf
  <MultiPartField, None>

  >>> interfaces.IMultiPartField.providedBy(mpf)
  True

  >>> mpf.list is None
  True

As you can see we will get an input stream as file content:

  >>> 'BytesIO' in str(type(mpf.file))
  True

  >>> print(mpf.file.read().decode('utf-8'))
  -----------------------------7d81772d2c0206
  Content-Disposition: form-data; name="form.widgets.upload"; filename="test.txt"
  Content-Type: text/plain
  <BLANKLINE>
  This is a test file
  <BLANKLINE>
  -----------------------------7d81772d2c0206
  Content-Disposition: form-data; name="form.buttons.add"
  <BLANKLINE>
  Add
  -----------------------------7d81772d2c0206--

And we will get the input stream as value:

  >>> _ = mpf.file.seek(0)
  >>> print(mpf.value.decode('utf-8'))
  -----------------------------7d81772d2c0206
  Content-Disposition: form-data; name="form.widgets.upload"; filename="test.txt"
  Content-Type: text/plain
  <BLANKLINE>
  This is a test file
  <BLANKLINE>
  -----------------------------7d81772d2c0206
  Content-Disposition: form-data; name="form.buttons.add"
  <BLANKLINE>
  Add
  -----------------------------7d81772d2c0206--

But this result is really useless. Since we didn't provide the right enviroment,
the parser was not able to parse the input correct. Let's try to parse again
with the right environ settings:

  >>> environ = {}
  >>> environ['REQUEST_METHOD'] = 'POST'
  >>> environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=---------------------------7d81772d2c0206'
  >>> environ['CONTENT_LENGTH'] = '321'
  >>> environ['QUERY_STRING'] = ''

  >>> _ = testFile.seek(0)
  >>> multiPartField = parseMultiParts(inputStream=testFile, environ=environ)
  >>> multiPartField.list
  [<MultiPartField, ...'form.widgets.upload': ...'test.txt'>, <MultiPartField, ...'form.buttons.add'>]

  >>> multiPartField.value
  [<MultiPartField, ...'form.widgets.upload': ...'test.txt'>, <MultiPartField, ...'form.buttons.add'>]

The first field provides the file upload name and value:

  >>> print(multiPartField.list[0].name)
  form.widgets.upload

  >>> multiPartField.list[0].value is None
  True

Of course, we didn't get a value, we need to read the file data:

  >>> multiPartField.list[0].file
  <open file '<fdopen>', mode 'w+b' at ...>

  >>> print(multiPartField.list[0].file.read())
  <BLANKLINE>
  This is a test file
  <BLANKLINE>

The second field provides the submit button name and value:

  >>> print(multiPartField.list[1].name)
  form.buttons.add

  >>> print(multiPartField.list[1].value)
  <BLANKLINE>
  Add


parseFormData in POST
---------------------

The parseFormData method uses the parseData method for 'POST' requests. Let's
use a different file and try to parse the new input stream

  >>> from p01.cgi.parser import parseFormData
  >>> multiPartFilePath = os.path.join(data, 'multipart.txt')
  >>> multiPartFile = open(multiPartFilePath, 'rb')

Now we can use the file pointer:

  >>> parseFormData('POST', inputStream=multiPartFile) is None
  True

As you can see the parseFormData method does not work without a content type
and content lenght. Setup some enviroment variable like we would get from a
valid form. But first don't forget to seek:

  >>> environ = {}
  >>> environ['REQUEST_METHOD'] = 'POST'
  >>> environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=---------------------------721837373350705526688164684'
  >>> environ['CONTENT_LENGTH'] = '558'
  >>> environ['QUERY_STRING'] = ''

Now try again:

  >>> _ = multiPartFile.seek(0)
  >>> fieldList = parseFormData('POST', inputStream=multiPartFile, environ=environ)
  >>> fieldList
  [<MultiPartField, ...'id'>, <MultiPartField, ...'title'>, <MultiPartField, ...'file': ...'test.txt'>, <MultiPartField, ...'submit'>]

A you can see the different parts contain the name value data. The first field
contains the following name, value:

  >>> print(fieldList[0].name)
  id

  >>> print(fieldList[0].value)
  <BLANKLINE>
  1234

The second title field provides an emtpy string as value:

  >>> print(fieldList[1].name)
  title

  >>> fieldList[1].value.replace('\r\n', '\n')
  '\n'

The file field doesn't contain a value, this field provides a file handle:

  >>> print(fieldList[2].name)
  file

  >>> fieldList[2].value is None
  True

  >>> fieldList[2].file
  <open file '<fdopen>', mode 'w+b' at ...>

  >>> print(fieldList[2].file.read())
  Testing 123.
  <BLANKLINE>

The last field contains the submit button name and value:

  >>> print(fieldList[3].name)
  submit

  >>> print(fieldList[3].value)
  <BLANKLINE>
   Add\x20


application/x-www-form-urlencoded
---------------------------------

  >>> urlencodedPartFilePath = os.path.join(data, 'urlencoded.txt')
  >>> urlencodedPartFile = open(urlencodedPartFilePath, 'rb')

Now we can use the file pointer:

  >>> parseFormData('POST', inputStream=urlencodedPartFile) is None
  True

As you can see the parseFormData method does not work without a content type
and content lenght. Setup some enviroment variable like we would get from a
valid form. But first don't forget to seek:

  >>> environ = {}
  >>> environ['REQUEST_METHOD'] = 'POST'
  >>> environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded; charset=iso-8859-1'
  >>> environ['CONTENT_LENGTH'] = '51'
  >>> environ['QUERY_STRING'] = ''

Now try again:

  >>> urlencodedPartFile.seek(0)
  >>> fieldList = parseFormData('POST', inputStream=urlencodedPartFile, environ=environ)
  >>> fieldList
  [<SimpleField, ...'version' = ...'1.1'>, <SimpleField, ...'operation' = ...'searchRetrieve'>, <SimpleField, ...'query' = ...'dinosaur'>]


parseFormData in GET
--------------------

With no valid environment variables we get a None as result:

  >>> parseFormData('GET', environ={}) is None
  True

As you can see the parseFormData method does not work without a QUERY_STRING.
Setup some enviroment variables like we would get from a valid form.

  >>> environ = {}
  >>> environ['REQUEST_METHOD'] = 'GET'
  >>> environ['QUERY_STRING'] = 'foobar=20&barfoo=xyz'

  >>> fieldList = parseFormData('GET', environ=environ)

Let's see the results:

  >>> fieldList
  [<SimpleField, ...'foobar' = ...'20'>, <SimpleField, ...'barfoo' = ...'xyz'>]

Check them one by one:

  >>> print(fieldList[0].value)
  20

  >>> print(fieldList[1].value)
  xyz


parseQueryString
----------------

The parse query string method can extract data from a query string
parseQueryString is used to parse urlencoded parameters.
This bunch of expressions is taken from python test/test_cgi.py

  >>> from p01.cgi.parser import parseQueryString

  >>> parseQueryString("")
  []

  >>> parseQueryString("&")
  []

  >>> parseQueryString("&&")
  []

  >>> parseQueryString("=")
  []

  >>> parseQueryString("=a")
  [(...'', ...'a')]

  >>> parseQueryString("a")
  []

  >>> parseQueryString("a=")
  []

  >>> parseQueryString("a= ")
  [(...'a', ...' ')]

  >>> parseQueryString("&a=b")
  [(...'a', ...'b')]

  >>> parseQueryString("a=a+b&b=b+c")
  [(...'a', ...'a b'), (...'b', ...'b c')]

  >>> parseQueryString("a=1&a=2")
  [(...'a', ...'1'), (...'a', ...'2')]



  >>> parseQueryString("&")
  []

  >>> parseQueryString("&&")
  []

  >>> parseQueryString(";")
  []

  >>> parseQueryString(";&;")
  []

Should the next few really be valid?

  >>> parseQueryString("=")
  []

  >>> parseQueryString("=&=")
  []

  >>> parseQueryString("=;=")
  []

This rest seem to make sense

  >>> parseQueryString("=a")
  [(...'', ...'a')]

  >>> parseQueryString("&=a")
  [(...'', ...'a')]

  >>> parseQueryString("=a&")
  [(...'', ...'a')]

  >>> parseQueryString("=&a")
  []

  >>> parseQueryString("b=a")
  [(...'b', ...'a')]

  >>> parseQueryString("b+=a")
  [(...'b ', ...'a')]

  >>> parseQueryString("a=b=a")
  [(...'a', ...'b=a')]

  >>> parseQueryString("a=+b=a")
  [(...'a', ...' b=a')]

  >>> parseQueryString("&b=a")
  [(...'b', ...'a')]

  >>> parseQueryString("b&=a")
  [(...'', ...'a')]

  >>> parseQueryString("a=a+b&b=b+c")
  [(...'a', ...'a b'), (...'b', ...'b c')]

  >>> parseQueryString("a=a+b&a=b+a")
  [(...'a', ...'a b'), (...'a', ...'b a')]

  >>> parseQueryString("x=1&y=2.0&z=2-3.%2b0")
  [(...'x', ...'1'), (...'y', ...'2.0'), (...'z', ...'2-3.+0')]

  >>> parseQueryString("x=1;y=2.0&z=2-3.%2b0")
  [(...'x', ...'1'), (...'y', ...'2.0'), (...'z', ...'2-3.+0')]

  >>> parseQueryString("Hbc5161168c542333633315dee1182227:key_store_seqid=400006&cuyer=r&view=bustomer&order_id=0bb2e248638833d48cb7fed300000f1b&expire=964546263&lobale=en-US&kid=130003.300038&ss=env")
  [(...'Hbc5161168c542333633315dee1182227:key_store_seqid', ...'400006'), (...'cuyer', ...'r'), (...'view', ...'bustomer'), (...'order_id', ...'0bb2e248638833d48cb7fed300000f1b'), (...'expire', ...'964546263'), (...'lobale', ...'en-US'), (...'kid', ...'130003.300038'), (...'ss', ...'env')]


  >>> parseQueryString("group_id=5470&set=custom&_assigned_to=31392&_status=1&_category=100&SUBMIT=Browse")
  [(...'group_id', ...'5470'), (...'set', ...'custom'), (...'_assigned_to', ...'31392'), (...'_status', ...'1'), (...'_category', ...'100'), (...'SUBMIT', ...'Browse')]


Edge cases
~~~~~~~~~~

Form data with extreme long value
---------------------------------

Let's simulate when a value is too long (over 1000 chars right now)

  >>> multiPartFilePath = os.path.join(data, 'multipart_long.txt')
  >>> multiPartFile = open(multiPartFilePath, 'rb')

As you can see the parseFormData method does not work without a content type
and content lenght. Setup some enviroment variable like we would get from a
valid form.

  >>> environ = {}
  >>> environ['REQUEST_METHOD'] = 'POST'
  >>> environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=--------------GHSKFJDLGDS7543FJKLFHRE75642756743254'
  >>> environ['CONTENT_LENGTH'] = '5550'
  >>> environ['QUERY_STRING'] = ''

  >>> fieldList = parseFormData('POST', inputStream=multiPartFile, environ=environ)
  >>> fieldList
  [<MultiPartField, ...'license'>, <MultiPartField, ...'name'>, <MultiPartField, ...'metadata_version'>, <MultiPartField, ...'author'>, <MultiPartField, ...'home_page'>, <MultiPartField, ...':action'>, <MultiPartField, ...'download_url'>, <MultiPartField, ...'summary'>, <MultiPartField, ...'author_email'>, <MultiPartField, ...'version'>, <MultiPartField, ...'platform'>, <MultiPartField, ...'description'>]

  >>> print(fieldList[11].name)
  description

  >>> print(fieldList[11].value)
  =============
  zope.sendmail
  =============
  <BLANKLINE>
  zope.sendmail is a package for email sending from Zope 3 applications.
  Email sending from Zope 3 applications works as follows:
  <BLANKLINE>
  A Zope 3 application locates a mail delivery utility
  (``IMailDelivery``) and feeds a message to it. It gets back a unique
  message ID so it can keep track of the message by subscribing to
  ``IMailEvent`` events.
  <BLANKLINE>
  The utility registers with the transaction system to make sure the
  message is only sent when the transaction commits successfully.
  (Among other things this avoids duplicate messages on
  ``ConflictErrors``.)
  <BLANKLINE>
  If the delivery utility is a ``IQueuedMailDelivery``, it puts the
  message into a queue (a Maildir mailbox in the file system). A
  separate process or thread (``IMailQueueProcessor``) watches the queue
  and delivers messages asynchronously. Since the queue is located in
  the file system, it survives Zope restarts or crashes and the mail is
  not lost.  The queue processor can implement batching to keep the
  server load low.
  <BLANKLINE>
  If the delivery utility is a ``IDirectMailDelivery``, it delivers
  messages synchronously during the transaction commit.  This is not a
  very good idea, as it makes the user wait.  Note that transaction
  commits must not fail, but that is not a problem, because mail
  delivery problems dispatch an event instead of raising an exception.
  <BLANKLINE>
  However, there is a problem -- sending events causes unknown code to
  be executed during the transaction commit phase.  There should be a
  way to start a new transaction for event processing after this one is
  commited.
  <BLANKLINE>
  An ``IMailQueueProcessor`` or ``IDirectMailDelivery`` actually
  delivers the messages by using a mailer (``IMailer``) component that
  encapsulates the delivery process.  There currently is only one
  mailer:
  <BLANKLINE>
  ``ISMTPMailer`` sends all messages to a relay host using SMTP.
  <BLANKLINE>
  If mail delivery succeeds, an ``IMailSentEvent`` is dispatched by the
  mailer.  If mail delivery fails, no exceptions are raised, but an
  `IMailErrorEvent` is dispatched by the mailer.
  <BLANKLINE>
  <BLANKLINE>
  Change history
  ~~~~~~~~~~~~~~
  <BLANKLINE>
  3.5.1 (unreleased)
  ------------------
  <BLANKLINE>
  - work around a problem when smtp quit fails, the mail was considered not
    delivered where just the quit failed
  <BLANKLINE>
  3.5.0 (2008-07-05)
  ------------------
  <BLANKLINE>
  - final release (identical with 3.5.0b2)
  <BLANKLINE>
  3.5.0b2 (2007-12-19)
  --------------------
  <BLANKLINE>
  - If the SMTP server rejects a message (for example, when the sender or
    recipient address is malformed), that email stays in the queue forever
    (https://bugs.launchpad.net/zope3/+bug/157104).
  <BLANKLINE>
  <BLANKLINE>
  3.5.0b1 (2007-11-08)
  --------------------
  <BLANKLINE>
  - Added README.txt
  - Can now talk to servers that don't implement EHLO
  - Fix bug that caused files with very long names to be created
  - Fix for https://bugs.launchpad.net/zope3/+bug/157104: move aside mail that's
    causing 5xx server responses.
  <BLANKLINE>
  <BLANKLINE>
  3.5.0a2 (2007-10-23)
  --------------------
  <BLANKLINE>
  - Cleaned up ``does_esmtp`` in faux SMTP connection classes provided by the
    tests.
  - If the ``QueueProcessorThread`` is asked to stop while sending messages, do
    so after sending the current message; previously if there were many, many
    messages to send, the thread could stick around for quite a while.
  <BLANKLINE>
  <BLANKLINE>
  3.5.0a1 (2007-10-23)
  --------------------
  <BLANKLINE>
  - ``QueueProcessorThread`` now accepts an optional parameter *interval* for
    defining how often to process the mail queue (default is 3 seconds)
  <BLANKLINE>
  - Several ``QueueProcessorThreads`` (either in the same process, or multiple
    processes) can now deliver messages from a single maildir without duplicates
    being sent.
  <BLANKLINE>
  <BLANKLINE>
  3.4.0 (2007-08-20)
  --------------------
  <BLANKLINE>
  - Bugfix: Don't keep open files around for every email message
    to be sent on transaction commit.  People who try to send many emails
    in a single transaction now will not run out of file descriptors.
  <BLANKLINE>
  <BLANKLINE>
  3.4.0a1 (2007-04-22)
  --------------------
  <BLANKLINE>
  Initial release as a separate project, corresponds to ``zope.sendmail``
  from Zope 3.4.0a1.


Content length in HTTP_CONTENT_LENGTH
-------------------------------------

The parseFormData method uses the parseData method for 'POST' requests. Let's
use a different file and try to parse the new input stream

  >>> multiPartFilePath = os.path.join(data, 'multipart.txt')
  >>> multiPartFile = open(multiPartFilePath, 'rb')

Setup some enviroment variable like we would get from a valid form.

  >>> environ = {}
  >>> environ['REQUEST_METHOD'] = 'POST'
  >>> environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=---------------------------721837373350705526688164684'
  >>> environ['HTTP_CONTENT_LENGTH'] = '558'
  >>> environ['QUERY_STRING'] = ''

Try it:

  >>> fieldList = parseFormData('POST', inputStream=multiPartFile, environ=environ)
  >>> fieldList
  [<MultiPartField, ...'id'>, <MultiPartField, ...'title'>, <MultiPartField, ...'file': ...'test.txt'>, <MultiPartField, ...'submit'>]

Invalid content length
----------------------

The parser should not bother if the content length is something non-numeric.

  >>> multiPartFilePath = os.path.join(data, 'multipart.txt')
  >>> multiPartFile = open(multiPartFilePath, 'rb')

Setup some enviroment variable like we would get from a valid form.

  >>> environ = {}
  >>> environ['REQUEST_METHOD'] = 'POST'
  >>> environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=---------------------------721837373350705526688164684'
  >>> environ['HTTP_CONTENT_LENGTH'] = '5x58'
  >>> environ['QUERY_STRING'] = ''

Try it:

  >>> fieldList = parseFormData('POST', inputStream=multiPartFile, environ=environ)
  >>> fieldList
  [<MultiPartField, ...'id'>, <MultiPartField, ...'title'>, <MultiPartField, ...'file': ...'test.txt'>, <MultiPartField, ...'submit'>]

application/x-www-form-urlencoded content length in HTTP_CONTENT_LENGTH
-----------------------------------------------------------------------

  >>> urlencodedPartFilePath = os.path.join(data, 'urlencoded.txt')
  >>> urlencodedPartFile = open(urlencodedPartFilePath, 'rb')

Now we can use the file pointer:

  >>> parseFormData('POST', inputStream=urlencodedPartFile) is None
  True

As you can see the parseFormData method does not work without a content type
and content lenght. Setup some enviroment variable like we would get from a
valid form. But first don't forget to seek:

  >>> environ = {}
  >>> environ['REQUEST_METHOD'] = 'POST'
  >>> environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded; charset=iso-8859-1'
  >>> environ['HTTP_CONTENT_LENGTH'] = '51'
  >>> environ['QUERY_STRING'] = ''

Now try again:

  >>> urlencodedPartFile.seek(0)
  >>> fieldList = parseFormData('POST', inputStream=urlencodedPartFile, environ=environ)
  >>> fieldList
  [<SimpleField, ...'version' = ...'1.1'>, <SimpleField, ...'operation' = ...'searchRetrieve'>, <SimpleField, ...'query' = ...'dinosaur'>]

application/x-www-form-urlencoded invalid content lenght
--------------------------------------------------------

The parser should not bother if the content length is something non-numeric.

  >>> urlencodedPartFilePath = os.path.join(data, 'urlencoded.txt')
  >>> urlencodedPartFile = open(urlencodedPartFilePath, 'rb')

Now we can use the file pointer:

  >>> parseFormData('POST', inputStream=urlencodedPartFile) is None
  True

As you can see the parseFormData method does not work without a content type
and content lenght. Setup some enviroment variable like we would get from a
valid form. But first don't forget to seek:

  >>> environ = {}
  >>> environ['REQUEST_METHOD'] = 'POST'
  >>> environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded; charset=iso-8859-1'
  >>> environ['CONTENT_LENGTH'] = '5x1'
  >>> environ['QUERY_STRING'] = ''

Now try again:

  >>> urlencodedPartFile.seek(0)
  >>> fieldList = parseFormData('POST', inputStream=urlencodedPartFile, environ=environ)
  >>> fieldList
  [<SimpleField, ...'version' = ...'1.1'>, <SimpleField, ...'operation' = ...'searchRetrieve'>, <SimpleField, ...'query' = ...'dinosaur'>]


Invalid method
--------------

  >>> parseFormData('XXX') is None
  True


tempfile
--------

Let's test the temporary file factory arguments:

  >>> largeFilePath = os.path.join(data, 'large_file.txt')
  >>> largeFile = open(largeFilePath, 'rb')

  >>> environ = {}
  >>> environ['REQUEST_METHOD'] = 'POST'
  >>> environ['CONTENT_TYPE'] = 'multipart/form-data; boundary=---------------------------721837373350705526688164684'
  >>> environ['HTTP_CONTENT_LENGTH'] = '25206'
  >>> environ['QUERY_STRING'] = ''

Setup a tempfile and arguments

  >>> import tempfile
  >>> tmpFileFactory = tempfile.NamedTemporaryFile
  >>> tmpFileFactoryArguments = {'mode': 'w+b'}
  >>> fieldList = parseFormData('POST', inputStream=multiPartFile,
  ...     environ=environ, tmpFileFactory=tmpFileFactory,
  ...     tmpFileFactoryArguments=tmpFileFactoryArguments)
  >>> fieldList = parseFormData('POST', inputStream=largeFile, environ=environ)
  >>> pprint(fieldList)
  [<MultiPartField, ...'id'>,
   <MultiPartField, ...'upload': ...'large.txt'>,
   <MultiPartField, ...'add'>]

Get the MultiPartField wiht the upload data:

  >>> mpf = fieldList[1]
  >>> mpf
  <MultiPartField, ...'upload': ...'large.txt'>

As you can see we will get our tempfile instance with our 'w+b' mode given from
the tmpFileFactoryArguments:

  >>> str(mpf.file).find('file') > -1
  True