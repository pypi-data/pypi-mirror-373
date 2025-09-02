=======
JSONRPC
=======

JSON is javascript object notation. JSON-RPC performs the same service
as XML-RPC, except the transport is JSON instead of XML.

Many thanks to Jim Washington for the work on zif.jsonserver. This project uses
many code writen by Jim. I implemented an additional python JSONRPC proxy which
can communicate with the server. This means we can use this library to call
JSON from python to python. The JSON-RPC proxy uses similar patterns like the
XML-RPC implementation.

There is also an additional xmlhttp and json javascript implementation which
offers a JSON-RPC proxy implementation for JavaScript.

This project provides the proposed request type "application/json". The request
type "application/json-rpc" is supported as long it is not officialy deprecated.

The goal of this project is to provide a JSON-RPC implementation. Simple
Browser views which handle JSON calls with a BrowserRequest are not supported
by this package. I'm still not sure if this is good or bad and in which
direction I will go with this package.

Some of my goals are right now, but can change in the future if I'll understand
all the concepts around JSON, e.g. JSPON, JSONP, CrossSite etc:

- provide a secure way to handle JSON calls from client to server.
  I hope we can implement JSONRequest some days. CrossSite seems to use a
  intereting concept

- Simple pythonic implementation

- Use together with JQuery (see http://www.jquery.org).

- No other dependency then JQuery and basic zope packages.

- well tested (this is not the case for JavaScript right now)


About JSON
----------

See www.json.org for more information about JSON.

See http://json-rpc.org/wd/JSON-RPC-1-1-WD-20060807.html for more information
about the JSON 1.1 specification.


What this package can't do
--------------------------

JSON and this package have different limitations. This package can right now
not handle the following tasks:

- Handle fileupload

- Handle GET request

Note that the JSONRPCRequest implementation is based on the IHTTPRequest, this
means that there is no other browser page available if you call them in
python, e.g. getMultiAdapter((context, request), name='myViewName'). This is
explicitly done this way. If you'd like to use content form such browser pages
in a JSON request/call, you can inherit your skin form IJSONRPCLayer and
IBrowserRequest and register your JSON-RPC views for this custom layer.


Setup
-----

  >>> import json
  >>> import p01.publisher.testing
  >>> import p01.jsonrpc.testing
  >>> from p01.jsonrpc.testing import getJSONRPCTestProxy


JSON-RPC server
---------------

The JSON server looks for content-type "application/json", and handles those
requests as JSON-RPC. The official mime-type for JSON is "application/json"
The old content type ``application/json-rpc`` is supported too.

Let's define a content object:

  >>> import zope.interface
  >>> class IDemoContent(zope.interface.Interface):
  ...     """Demo content interface."""

  >>> import persistent
  >>> class DemoContent(persistent.Persistent):
  ...     """Demo content."""
  ...     zope.interface.implements(IDemoContent)

And define a JSONRPC method view:

  >>> from p01.jsonrpc import publisher
  >>> class DemoView(publisher.MethodPublisher):
  ...     """Sample JSON view."""
  ...
  ...     def hello(self):
  ...         return u"Hello World"
  ...
  ...     def greeting(self, name):
  ...         return u"Hello %s" % name
  ...
  ...     def mixedparams(self, prefix, bar=None, foo=None):
  ...         # Note; keyword arguments can be found in request.form
  ...         return u"%s %s %s" % (prefix, bar, foo)
  ...
  ...     def kws(self, adam=None, foo=None, bar=None):
  ...         # Note; keyword arguments can be found in request.form
  ...         a = self.request.get('adam')
  ...         b = self.request.form.get('foo')
  ...         c = self.request.form.get('bar')
  ...         return u"%s %s %s" % (a, b, c)
  ...
  ...     def showId(self):
  ...         return u"The json id is: %s" % self.request.jsonId
  ...
  ...     def forceValueError(self):
  ...         raise ValueError('Something was wrong in server method.')

Let's define a content object that is a container:

  >>> import zope.interface
  >>> class IDemoContainer(zope.container.interfaces.IReadContainer):
  ...     """Demo container interface."""

  >>> import persistent
  >>> from zope.container import btree

  >>> class DemoContainer(btree.BTreeContainer):
  ...     """Demo container."""
  ...     zope.interface.implements(IDemoContainer)

And define a JSONRPC method view:

  >>> from p01.jsonrpc import publisher
  >>> class DemoContainerView(publisher.MethodPublisher):
  ...     """Sample JSON view."""
  ...
  ...     def available(self):
  ...         return u"Hello World"
  ...
  ...     def greeting(self, name):
  ...         return u"Hello %s" % name
  ...
  ...     def mixedparams(self, prefix, foo=None, bar=None):
  ...         # Note; keyword arguments can be found in request.form
  ...         return u"%s %s %s" % (prefix, foo, bar)
  ...
  ...     def kws(self, adam=None, foo=None, bar=None):
  ...         # Note; keyword arguments can be found in request.form
  ...         a = self.request.get('adam')
  ...         b = self.request.form.get('foo')
  ...         c = self.request.form.get('bar')
  ...         return u"%s %s %s" % (a, b, c)
  ...
  ...     def showId(self):
  ...         return u"The json id is: %s" % self.request.jsonId
  ...
  ...     def forceValueError(self):
  ...         raise ValueError('Something was wrong in server method.')


Make them available under the fake package ``jsonsamples``:

  >>> import sys
  >>> sys.modules['custom'] = type('Module', (), {})()
  >>> sys.modules['custom'].IDemoContent = IDemoContent
  >>> sys.modules['custom'].DemoContent = DemoContent
  >>> sys.modules['custom'].DemoView = DemoView
  >>> sys.modules['custom'].IDemoContainer = IDemoContainer
  >>> sys.modules['custom'].DemoContainer = DemoContainer
  >>> sys.modules['custom'].DemoContainerView = DemoContainerView

Let's show how we can register a jsonrpc view:

  >>> from zope.configuration import xmlconfig
  >>> import p01.jsonrpc
  >>> context = xmlconfig.file('meta.zcml', p01.jsonrpc)
  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:p01="http://namespaces.zope.org/p01">
  ...   <p01:jsonrpc
  ...       for="custom.IDemoContent"
  ...       class="custom.DemoView"
  ...       permission="zope.Public"
  ...       methods="hello greeting mixedparams kws showId forceValueError"
  ...       layer="p01.jsonrpc.testing.IJSONRPCTestSkin"
  ...       />
  ... </configure>
  ... """, context)

Let's show how we can register a jsonrpc view for the container:
(The container class needs permission configuration too)

  >>> context = xmlconfig.file('meta.zcml', p01.jsonrpc)
  >>> context = xmlconfig.file('meta.zcml', zope.security, context)
  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:p01="http://namespaces.zope.org/p01"
  ...     xmlns="http://namespaces.zope.org/zope">
  ...     <class class="custom.DemoContainer">
  ...       <allow
  ...           interface="custom.IDemoContainer"
  ...           />
  ...     </class>
  ...   <p01:jsonrpc
  ...       for="custom.IDemoContainer"
  ...       class="custom.DemoContainerView"
  ...       permission="zope.Public"
  ...       methods="available greeting mixedparams kws showId forceValueError"
  ...       layer="p01.jsonrpc.testing.IJSONRPCTestSkin"
  ...       />
  ... </configure>
  ... """, context)


Now we will setup a content object in our site:

  >>> import p01.jsonrpc.testing
  >>> p01.jsonrpc.testing.setUpTestApplication()
  <JSONRPCTestApplication>

  >>> site  = getRootFolder()
  >>> site
  <JSONRPCTestApplication>

  >>> content = DemoContent()
  >>> site[u'content'] = content
  >>> container = DemoContainer()
  >>> site[u'container'] = container

Now we can call the method from our JSONRPC view:

  >>> request = p01.jsonrpc.testing.TestRequest()
  >>> demoView = DemoView(content, request)
  >>> demoView.hello()
  u'Hello World'

But this is not intuitive. Let's see how we can traverse to the method ``hello``
with the traverser:

  >>> from p01.jsonrpc.publisher import MethodTraverser
  >>> methodTraverser = MethodTraverser(demoView, request)
  >>> methodTraverser.publishTraverse(request, 'hello')()
  u'Hello World'

Now we try to access the JSON-RPC view method with a test browser. As you can
see, there is no view accessible. This is because the JSONRPC view is not a
browser view and is not traversable. The error shows that the request factory
falls back to the browser request factory:

  >>> handleErrors = False
  >>> useBasicAuth = True
  >>> browser = p01.publisher.testing.getTestBrowser(handleErrors=handleErrors,
  ...     useBasicAuth=useBasicAuth)
  >>> browser.addHeader('Accept-Language', 'en')
  >>> browser.addHeader('Content-Type', 'application/json')
  >>> siteURL = 'http://localhost/++skin++JSONRPCTestSkin'
  >>> browser.open(siteURL + '/content/hello')
  Traceback (most recent call last):
  ...
  NotFound: Object: <JSONRPCTestApplication>, name: u'++skin++JSONRPCTestSkin'

Testing
-------

If you need to test a JSONRPC view you can use the test proxy like shown
below in the ``JSON-RPC proxy`` section.


JSON-RPC proxy
--------------

The jsonrpc package provides also a JSON-RPC proxy implementation. This
implementation is similar to the one known from xmlrpclib except that it can
handle JSON instead of XML.

Let's try to call our method called ``hello`` we defined before:

  >>> proxy = getJSONRPCTestProxy(siteURL + '/content')
  >>> proxy.hello()
  u'Hello World'

  >>> proxy2 = getJSONRPCTestProxy(siteURL + '/container')
  >>> proxy2.available()
  u'Hello World'

Now let's make a remote procedure call with a argument:

  >>> proxy.greeting(u'Jessy')
  u'Hello Jessy'

Let's call named arguments:

  >>> proxy.kws(bar=u'BAR', foo=u'FOO')
  u'None FOO BAR'

There is also an ``id`` in the json response. Let's use such a json request id
in our JSONRPCProxy:

  >>> proxy = getJSONRPCTestProxy(siteURL + '/content', jsonId = u'my id')
  >>> proxy.showId()
  u'The json id is: my id'

The proxy also knows this id as jsonId:

  >>> proxy.jsonId
  u'my id'


JSON-RPC Versions
-----------------

Let's test the different JSON-RPC versions starting with version 1.0:

  >>> v1 = getJSONRPCTestProxy(siteURL + '/container', jsonVersion='1.0')
  >>> v1.available()
  u'Hello World'

  >>> v1.greeting(u'Jessy')
  u'Hello Jessy'

  >>> v1.kws(bar=u'BAR', foo=u'FOO')
  u'None FOO BAR'

  >>> v1 = getJSONRPCTestProxy(siteURL + '/content', jsonId = u'my id',
  ...     jsonVersion='1.0')
  >>> v1.showId()
  u'The json id is: my id'

  >>> v1.jsonId
  u'my id'

Now test with JSON-RPC version 1.1:

  >>> v11 = getJSONRPCTestProxy(siteURL + '/container', jsonVersion='1.1')
  >>> v11.available()
  u'Hello World'

  >>> v11.greeting(u'Jessy')
  u'Hello Jessy'

  >>> v11.kws(bar=u'BAR', foo=u'FOO')
  u'None FOO BAR'

  >>> v11 = getJSONRPCTestProxy(siteURL + '/content', jsonId = u'my id',
  ...     jsonVersion='1.1')
  >>> v11.showId()
  u'The json id is: my id'

  >>> v11.jsonId
  u'my id'

Now test with JSON-RPC version 2.0:

  >>> v2 = getJSONRPCTestProxy(siteURL + '/container', jsonVersion='2.0')
  >>> v2.available()
  u'Hello World'

  >>> v2.greeting(u'Jessy')
  u'Hello Jessy'

  >>> v2.kws(bar=u'BAR', foo=u'FOO')
  u'None FOO BAR'

  >>> v2 = getJSONRPCTestProxy(siteURL + '/content', jsonId = u'my id',
  ...     jsonVersion='2.0')
  >>> v2.showId()
  u'The json id is: my id'

  >>> v2.jsonId
  u'my id'


Mixed parameters
----------------

Note the keyword arguments will get stored in the request.form. Important
to know is that JSON-RPC does not support positional and named arguments in
one method call.

  >>> v1.mixedparams('Hello', foo=u'FOO', bar=u'BAR')
  Traceback (most recent call last):
  ...
  ValueError: Mixing positional and named parameters in one call is not possible

  >>> v11.mixedparams('Hello', foo=u'FOO', bar=u'BAR')
  Traceback (most recent call last):
  ...
  ValueError: Mixing positional and named parameters in one call is not possible

  >>> v2.mixedparams('Hello', foo=u'FOO', bar=u'BAR')
  Traceback (most recent call last):
  ...
  ValueError: Mixing positional and named parameters in one call is not possible


Error handling
--------------

See what happens if the server raises an Exception. We will get a response
error with additional error content:

  >>> proxy.forceValueError()
  Traceback (most recent call last):
  ...
  ResponseError: Received error from server: ...

and the error content looks like:

  >>> proxy.error
  {u'message': u'Internal error', u'code': -32603, u'data': {u'i18nMessage': u'Internal error'}}

The error property gets reset on the next successfull call:

  >>> x = proxy.showId()
  >>> proxy.error is None
  True

And now we force a ResponseError with a fake json reader. This will now raise a
ResponseError:

  >>> def forceResponseErrorJSONReader(data, *args, **kwargs):
  ...     aBadString = u'{"id":"jsonrpc", "method":"hello", "no-params"}'
  ...     return json.loads(aBadString, *args, **kwargs)

  >>> proxy = getJSONRPCTestProxy(siteURL + '/content',
  ...     jsonReader=forceResponseErrorJSONReader)
  >>> proxy.hello()
  Traceback (most recent call last):
  ...
  ResponseError: Expecting ':' delimiter: line 1 column 47 (char 46)

the error message is stored in the proxy too:

  >>> proxy.error
  u"Expecting ':' delimiter: line 1 column 47 (char 46)"


Transport
~~~~~~~~~

We used the JSONRPCTestProxy here for testing. This JSON-RPC proxy is a wrapper
for the original JSONRPCProxy and adds handleErrors support and a special
Transport layer which uses a testing caller. You can use one of the different
Transport layers defined in the z3c.json.transport module in real usecases
together with the default JSONRPCProxy implementation.


cleanup
-------

Now we need to clean up the custom module.

  >>> del sys.modules['custom']
