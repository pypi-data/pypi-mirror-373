##############################################################################
#
# Copyright (c) 2013 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Request implementations

$Id: request.py 5657 2025-09-01 13:33:32Z roger.ineichen $
"""
import base64
import logging
import re
import tempfile
from builtins import object
from builtins import str

import p01.cgi.interfaces
import p01.cgi.parser
import p01.json.api
import p01.jsonrpc.exception
import six
import zope.interface
import zope.publisher.browser
import zope.publisher.interfaces
from zope.i18n.interfaces import IUserPreferredCharsets
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.locales import LoadLocaleError
from zope.i18n.locales import locales
from zope.interface import implementer
from zope.publisher.base import DebugFlags
from zope.publisher.base import RequestDataProperty
from zope.publisher.base import RequestEnvironment
from zope.publisher.browser import CONVERTED
from zope.publisher.browser import DEFAULT
from zope.publisher.browser import REC
from zope.publisher.browser import RECORD
from zope.publisher.browser import RECORDS
from zope.publisher.browser import Record
from zope.publisher.browser import SEQUENCE
from zope.publisher.browser import get_converter
from zope.publisher.http import CookieMapper
from zope.publisher.http import DEFAULT_PORTS
from zope.publisher.http import ENCODING
from zope.publisher.http import HTTPVirtualHostChangedEvent
from zope.publisher.http import HeaderGetter
from zope.publisher.http import URLGetter
from zope.publisher.http import sane_environment
from zope.publisher.interfaces.browser import IBrowserApplicationRequest
from zope.publisher.interfaces.http import IHTTPApplicationRequest
from zope.publisher.interfaces.http import IHTTPCredentials
from zope.publisher.interfaces.http import IHTTPRequest
from zope.security.proxy import removeSecurityProxy

import p01.publisher.publication
import p01.publisher.response
from p01.publisher import interfaces
from p01.publisher._compat import PYTHON2
from p01.publisher._compat import _u

if PYTHON2:
    import Cookie as cookies
    from urllib import quote
else:
    import http.cookies as cookies
    from urllib.parse import quote
    unicode = str


JSON_RPC_VERSION = '2.0'

STREAM_SPOOLED_MAX_SIZE = 65536 # zope default
UPLOAD_SPOOLED_MAX_SIZE = 512*1024 # 0.5 MB
DEFAULTABLE_METHODS = ['GET', 'POST', 'HEAD', 'OPTIONS']

_marker = object()

eventlog = logging.getLogger('eventlog')

host_port_re = re.compile(
    r"^(.*):([0-9]*)$", re.DOTALL)


def splitport(host):
    """Split port number off the hostname.

        >>> splitport('example.com:80')
        ('example.com', '80')

        >>> splitport('localhost')
        ('localhost', None)

        >>> splitport('[::1]')
        ('[::1]', None)

        >>> splitport('[::1]:443')
        ('[::1]', '443')

        >>> splitport('localhost:')
        ('localhost', None)

    """
    match = host_port_re.match(host)
    if match:
        host, port = match.groups()
    else:
        port = None
    return host, port or None



def ensure_str(s, encoding='utf-8'):
    if isinstance(s, six.binary_type):
        try:
            return s.decode(encoding)
        except UnicodeDecodeError:
            # fallback to latin1 if utf-8 decoding fails
            return s.decode('latin-1')
    return s

###############################################################################
#
# request helper

class HTTPInputStream(object):
    """Special stream that supports caching the read data.

    This implementation also support the new SpooledTemporaryFile
    """
    def __init__(self, stream, environment):
        self.stream = stream
        self.cacheStream = tempfile.SpooledTemporaryFile(
            max_size=STREAM_SPOOLED_MAX_SIZE, mode='w+b')
        size = environment.get('CONTENT_LENGTH')
        # There can be no size in the environment (None) or the size
        # can be an empty string IE < 10, in which case we treat it as absent.
        if not size:
            size = environment.get('HTTP_CONTENT_LENGTH')
        self.size = size and int(size) or -1

    def getCacheStream(self):
        self.read(self.size)
        self.cacheStream.seek(0)
        return self.cacheStream

    def read(self, size=-1):
        data = self.stream.read(size)
        self.cacheStream.write(data)
        return data

    def readline(self, size=None):
        if size is not None:
            data = self.stream.readline(size)
        else:
            data = self.stream.readline()
        self.cacheStream.write(data)
        return data

    def readlines(self, hint=0):
        data = self.stream.readlines(hint)
        self.cacheStream.write(b''.join(data))
        return data


###############################################################################
#
# browser request

@zope.interface.implementer(zope.publisher.interfaces.IRequest)
class BaseRequest(object):
    """Represents a publishing request.

    This object provides access to request data. Request data may
    vary depending on the protocol used.

    Request objects are created by the object publisher and will be
    passed to published objects through the argument name, REQUEST.

    The request object is a mapping object that represents a
    collection of variable to value mappings.
    """

    __slots__ = (
        '__provides__',      # Allow request to directly provide interfaces
        '_held',             # Objects held until the request is closed
        '_traversed_names',  # The names that have been traversed
        '_last_obj_traversed', # Object that was traversed last
        '_traversal_stack',  # Names to be traversed, in reverse order
        '_environ',          # The request environment variables
        '_response',         # The response
        '_args',             # positional arguments
        '_body_instream',    # input stream
        '_body',             # The request body as a string
        '_publication',      # publication object
        '_principal',        # request principal, set by publication
        'interaction',       # interaction, set by interaction
        'debug',             # debug flags
        'annotations',       # per-package annotations
        # 'app',               # wsgi application for non ZODB publication
        # 'appURL',            # application url
        )

    environment = RequestDataProperty(RequestEnvironment)

    def __init__(self, body_instream, environ, response=None, positional=None):
        self._traversal_stack = []
        self._last_obj_traversed = None
        self._traversed_names = []
        self._environ = environ

        self._args = positional or ()

        if response is None:
            self._response = self._createResponse()
        else:
            self._response = response

        self._response._request = self

        self._body_instream = body_instream
        self._held = ()
        self._publication = None
        self._principal = None
        self.interaction = None
        self.debug = DebugFlags()
        self.annotations = {}

    appURL = property(lambda self: self.getApplicationURL())

    def setPrincipal(self, principal):
        self._principal = principal

    principal = property(lambda self: self._principal)

    def _getPublication(self):
        """See IPublisherRequest"""
        return self._publication

    publication = property(_getPublication)

    def setPublication(self, pub):
        self._publication = pub

    @property
    def app(self):
        """WSGI application (only available for non ZODB publication)"""
        return getattr(self._publication, 'app', None)

    def processInputs(self):
        """See IPublisherRequest"""
        # Nothing to do here

    def traverse(self, obj):
        """See IPublisherRequest"""

        publication = self.publication

        traversal_stack = self._traversal_stack
        traversed_names = self._traversed_names

        prev_object = None
        while True:

            self._last_obj_traversed = obj

            if removeSecurityProxy(obj) is not removeSecurityProxy(prev_object):
                # Invoke hooks (but not more than once).
                publication.callTraversalHooks(self, obj)

            if not traversal_stack:
                # Finished traversal.
                break

            prev_object = obj

            # Traverse to the next step.
            entry_name = traversal_stack.pop()
            traversed_names.append(entry_name)
            obj = publication.traverseName(self, obj, entry_name)

        return obj

    def close(self):
        """See IPublicationRequest"""
        for held in self._held:
            if zope.publisher.interfaces.IHeld.providedBy(held):
                held.release()

        self._held = None
        self._body_instream = None
        self._publication = None

    def getPositionalArguments(self):
        """See IPublicationRequest"""
        return self._args

    def _getResponse(self):
        return self._response

    response = property(_getResponse)

    def getTraversalStack(self):
        """See IPublicationRequest"""
        return list(self._traversal_stack) # Return a copy

    def hold(self, object):
        """See IPublicationRequest"""
        self._held = self._held + (object,)

    def setTraversalStack(self, stack):
        """See IPublicationRequest"""
        self._traversal_stack[:] = list(stack)

    def _getBodyStream(self):
        """See zope.publisher.interfaces.IApplicationRequest"""
        return self._body_instream

    bodyStream = property(_getBodyStream)

    def __len__(self):
        """See Interface.Common.Mapping.IEnumerableMapping"""
        return len(list(self.keys()))

    def items(self):
        """See Interface.Common.Mapping.IEnumerableMapping"""
        result = []
        get = self.get
        for k in list(self.keys()):
            result.append((k, get(k)))
        return result

    def keys(self):
        """See Interface.Common.Mapping.IEnumerableMapping"""
        return list(self._environ.keys())

    def __iter__(self):
        return iter(list(self.keys()))

    def values(self):
        """See Interface.Common.Mapping.IEnumerableMapping"""
        result = []
        get = self.get
        for k in list(self.keys()):
            result.append(get(k))
        return result

    def __getitem__(self, key):
        """See Interface.Common.Mapping.IReadMapping"""
        result = self.get(key, _marker)
        if result is _marker:
            raise KeyError(key)
        else:
            return result

    def get(self, key, default=None):
        """See Interface.Common.Mapping.IReadMapping"""
        result = self._environ.get(key, _marker)
        if result is not _marker:
            return result

        return default

    def __contains__(self, key):
        """See Interface.Common.Mapping.IReadMapping"""
        lookup = self.get(key, self)
        return lookup is not self

    has_key = __contains__

    def _createResponse(self):
        # Should be overridden by subclasses
        return p01.publisher.response.BaseResponse()

    def __bool__(self):
        # This is here to avoid calling __len__ for boolean tests
        return 1

    __nonzero__ = __bool__

    def __str__(self):
        L1 = list(self.items())
        L1.sort()
        return "\n".join(["%s:\t%s" % item for item in L1])

    def _setupPath_helper(self, attr):
        path = self.get(attr, "/")
        if path.endswith('/'):
            # Remove trailing backslash, so that we will not get an empty
            # last entry when splitting the path.
            path = path[:-1]
            self._endswithslash = True
        else:
            self._endswithslash = False

        clean = []
        for item in path.split('/'):
            if not item or item == '.':
                continue
            elif item == '..':
                # try to remove the last name
                try:
                    del clean[-1]
                except IndexError:
                    # the list of names was empty, so do nothing and let the
                    # string '..' be placed on the list
                    pass
            clean.append(item)

        clean.reverse()
        self.setTraversalStack(clean)

        self._path_suffix = None

    # not supported
    def retry(self):
        """See IPublisherRequest"""
        raise NotImplementedError("p01.publisher does not support retry")

    def supportsRetry(self):
        """See IPublisherRequest"""
        raise NotImplementedError("p01.publisher does not support retry")


###############################################################################
#
# http request

@zope.interface.implementer(IHTTPCredentials, IHTTPRequest,
    IHTTPApplicationRequest)
class HTTPRequest(BaseRequest):
    """Model HTTP request data.

    This object provides access to request data.  This includes, the
    input headers, form data, server data, and cookies.

    Request objects are created by the object publisher and will be
    passed to published objects through the argument name, REQUEST.

    The request object is a mapping object that represents a
    collection of variable to value mappings.  In addition, variables
    are divided into four categories:

      - Environment variables

        These variables include input headers, server data, and other
        request-related data.  The variable names are as <a
        href="http://hoohoo.ncsa.uiuc.edu/cgi/env.html">specified</a>
        in the <a
        href="http://hoohoo.ncsa.uiuc.edu/cgi/interface.html">CGI
        specification</a>

      - Form data

        These are data extracted from either a URL-encoded query
        string or body, if present.

      - Cookies

        These are the cookie data, if present.

      - Other

        Data that may be set by an application object.

    The form attribute of a request is actually a Field Storage
    object.  When file uploads are used, this provides a richer and
    more complex interface than is provided by accessing form data as
    items of the request.  See the FieldStorage class documentation
    for more details.

    The request object may be used as a mapping object, in which case
    values will be looked up in the order: environment variables,
    other variables, form data, and then cookies.
    """

    __slots__ = (
        '__provides__',   # Allow request to directly provide interfaces
        '_auth',          # The value of the HTTP_AUTHORIZATION header.
        '_cookies',       # The request cookies
        '_path_suffix',   # Extra traversal steps after normal traversal
        '_app_names',     # The application path as a sequence
        '_app_server',    # The server path of the application url
        '_orig_env',      # The original environment
        '_endswithslash', # Does the given path end with /
        'method',         # The upper-cased request method (REQUEST_METHOD)
        '_locale',        # The locale for the request
        '_vh_root',       # Object at the root of the virtual host
        )

    def __init__(self, body_instream, environ, response=None):
        super(HTTPRequest, self).__init__(
            HTTPInputStream(body_instream, environ), environ, response)

        self._orig_env = environ
        environ = sane_environment(environ)

        if 'HTTP_AUTHORIZATION' in environ:
            self._auth = environ['HTTP_AUTHORIZATION']
            del environ['HTTP_AUTHORIZATION']
        else:
            self._auth = None

        self.method = environ.get("REQUEST_METHOD", 'GET').upper()

        self._environ = environ

        self.__setupCookies()
        self.__setupPath()
        self.__setupURLBase()
        self._vh_root = None

        self.setupLocale()

    def setupLocale(self):
        """Setup locale

        NOTE: I recommend to implement a better concept in your own project
        This is a very generic pattern and should be improved depending on your
        project usecases.

        In our projects, we apply the locale together with localizaion data e.g.
        geo location, timezone etc. in the setPrincipal method and we use this
        method only for setup caching variable and the default language.
        The setPrincipal method is also the right place for setup principal
        or session related language or timezone data.
        """
        envadapter = IUserPreferredLanguages(self, None)
        if envadapter is None:
            self._locale = None
            return

        langs = envadapter.getPreferredLanguages()
        for httplang in langs:
            parts = (httplang.split('-') + [None, None])[:3]
            try:
                self._locale = locales.getLocale(*parts)
                return
            except LoadLocaleError:
                # Just try the next combination
                pass
        else:
            # No combination gave us an existing locale, so use the default,
            # which is guaranteed to exist
            self._locale = locales.getLocale(None, None, None)

    def _getLocale(self):
        return self._locale
    locale = property(_getLocale)

    def __setupURLBase(self):
        get_env = self._environ.get
        # Get base info first. This isn't likely to cause
        # errors and might be useful to error handlers.
        script = get_env('SCRIPT_NAME', '').strip()

        # _script and the other _names are meant for URL construction
        self._app_names = [f for f in script.split('/') if f]

        # get server URL and store it too, since we are already looking it up
        server_url = get_env('SERVER_URL', None)
        if server_url is not None:
            self._app_server = server_url = server_url.strip()
        else:
            server_url = self.__deduceServerURL()

        if server_url.endswith('/'):
            server_url = server_url[:-1]

        # strip off leading /'s of script
        while script.startswith('/'):
            script = script[1:]

        self._app_server = server_url

    def __deduceServerURL(self):
        environ = self._environ

        if (environ.get('HTTPS', '').lower() == "on" or
            environ.get('SERVER_PORT_SECURE') == "1"):
            protocol = 'https'
        else:
            protocol = 'http'

        if 'HTTP_HOST' in environ:
            host = environ['HTTP_HOST'].strip()
            hostname, port = splitport(host)
        else:
            hostname = environ.get('SERVER_NAME', '').strip()
            port = environ.get('SERVER_PORT', '')

        if port and port != DEFAULT_PORTS.get(protocol):
            host = hostname + ':' + port
        else:
            host = hostname

        return '%s://%s' % (protocol, host)

    def _parseCookies(self, text, result=None):
        """Parse 'text' and return found cookies as 'result' dictionary."""

        if result is None:
            result = {}

        # ignore cookies on a CookieError
        try:
            c = cookies.SimpleCookie(text)
        except cookies.CookieError as e:
            eventlog.warning(e)
            return result

        for k,v in list(c.items()):
            # recode cookie value to ENCODING (UTF-8)
            rk = _u(k if type(k) == bytes
                    else k.encode('latin1'), ENCODING)
            rv = _u(v.value if type(v.value) == bytes
                    else v.value.encode('latin1'), ENCODING)
            result[rk] = rv

        return result

    def __setupCookies(self):
        # Cookie values should *not* be appended to existing form
        # vars with the same name - they are more like default values
        # for names not otherwise specified in the form.
        self._cookies = {}
        cookie_header = self._environ.get('HTTP_COOKIE', None)
        if cookie_header is not None:
            self._parseCookies(cookie_header, self._cookies)

    def __setupPath(self):
        # PATH_INFO is unicode here, so setupPath_helper sets up the
        # traversal stack correctly.
        self._setupPath_helper("PATH_INFO")

    def supportsRetry(self):
        """See IPublisherRequest"""
        raise NotImplementedError("p01.publisher does not support retry")

    def retry(self):
        """See IPublisherRequest"""
        raise NotImplementedError("p01.publisher does not support retry")

    def traverse(self, obj):
        """See IPublisherRequest"""

        ob = super(HTTPRequest, self).traverse(obj)
        if self._path_suffix:
            self._traversal_stack = self._path_suffix
            ob = super(HTTPRequest, self).traverse(ob)

        return ob

    def getHeader(self, name, default=None, literal=False):
        """See IHTTPRequest"""
        environ = self._environ
        if not literal:
            name = name.replace('-', '_').upper()
        val = environ.get(name, None)
        if val is not None:
            return val
        if not name.startswith('HTTP_'):
            name='HTTP_%s' % name
        return environ.get(name, default)

    headers = RequestDataProperty(HeaderGetter)

    def getCookies(self):
        """See IHTTPApplicationRequest"""
        return self._cookies

    cookies = RequestDataProperty(CookieMapper)

    def setPathSuffix(self, steps):
        """See IHTTPRequest"""
        steps = list(steps)
        steps.reverse()
        self._path_suffix = steps

    def _authUserPW(self):
        """See IHTTPCredentials"""
        if self._auth and self._auth.lower().startswith('basic '):
            encoded = self._auth.split(None, 1)[-1]
            decoded = base64.b64decode(encoded.encode('iso-8859-1'))
            name, password = bytes.split(decoded, b':', 1)
            return name, password

    def unauthorized(self, challenge):
        """See IHTTPCredentials"""
        self._response.setHeader("WWW-Authenticate", challenge, True)
        self._response.setStatus(401)

    def _createResponse(self):
        # Should be overridden by subclasses
        return p01.publisher.response.HTTPResponse()

    def getURL(self, level=0, path_only=False):
        names = self._app_names + self._traversed_names
        if level:
            if level > len(names):
                raise IndexError(level)
            names = names[:-level]
        # See: http://www.ietf.org/rfc/rfc2718.txt, Section 2.2.5
        names = [quote(name.encode("utf-8"), safe='/+@') for name in names]

        if path_only:
            if not names:
                return '/'
            return '/' + '/'.join(names)
        else:
            if not names:
                return self._app_server
            return "%s/%s" % (self._app_server, '/'.join(names))

    def getApplicationURL(self, depth=0, path_only=False):
        """See IHTTPApplicationRequest"""
        if depth:
            names = self._traversed_names
            if depth > len(names):
                raise IndexError(depth)
            names = self._app_names + names[:depth]
        else:
            names = self._app_names

        # See: http://www.ietf.org/rfc/rfc2718.txt, Section 2.2.5
        names = [quote(name.encode("utf-8"), safe='/+@') for name in names]

        if path_only:
            return names and ('/' + '/'.join(names)) or '/'
        else:
            return (names and ("%s/%s" % (self._app_server, '/'.join(names)))
                    or self._app_server)

    def setApplicationServer(self, host, proto='http', port=None):
        if port and str(port) != DEFAULT_PORTS.get(proto):
            host = '%s:%s' % (host, port)
        self._app_server = '%s://%s' % (proto, host)
        zope.event.notify(HTTPVirtualHostChangedEvent(self))

    def shiftNameToApplication(self):
        """Add the name being traversed to the application name

        This is only allowed in the case where the name is the first name.

        A Value error is raise if the shift cannot beperformed.
        """
        if len(self._traversed_names) == 1:
            self._app_names.append(self._traversed_names.pop())
            zope.event.notify(HTTPVirtualHostChangedEvent(self))
            return

        raise ValueError("Can only shift leading traversal "
                         "names to application names")

    def setVirtualHostRoot(self, names=()):
        del self._traversed_names[:]
        self._vh_root = self._last_obj_traversed
        self._app_names = list(names)
        zope.event.notify(HTTPVirtualHostChangedEvent(self))

    def getVirtualHostRoot(self):
        return self._vh_root

    URL = RequestDataProperty(URLGetter)

    def get(self, key, default=None):
        """See Interface.Common.Mapping.IReadMapping"""
        result = self._cookies.get(key, _marker)
        if result is not _marker:
            return result

        return super(HTTPRequest, self).get(key, default)

    def keys(self):
        """See Interface.Common.Mapping.IEnumerableMapping"""
        d = {}
        d.update(self._environ)
        d.update(self._cookies)
        return list(d.keys())

    # def getJSONData(self, raw):
    #     """Load string as json data

    #     This hook can get used for enhanced json data convertion using custom
    #     json encoder, decoder pattern
    #     """
    #     return p01.json.api.jsonReader(raw)
    def getJSONData(self, raw):
        """Load string as json data

        This hook can get used for enhanced json data convertion using custom
        json encoder, decoder pattern
        """
        # bytes to UTF-8-SIG (remove BOM); str unchanged
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode('utf-8-sig', 'strict')

        # empty or whitespace raise ParseError
        if not raw or not raw.strip():
            raise p01.jsonrpc.exception.ParseError

        # optional: leading BOM if str is Unicode (very rare)
        if raw and raw[0] == u'\ufeff':
            raw = raw.lstrip(u'\ufeff')
        return p01.json.api.jsonReader(raw)

    def __repr__(self):
        # Returns a *short* string.
        try:
            url = self.URL
        except AttributeError:
            # missing _app_names in URL call
            url = ''
        return '<%s.%s instance URL=%s>' % (
            self.__class__.__module__, self.__class__.__name__, str(url))


###############################################################################
#
# browser request

class TMPFileUpload(object):
    """File upload objects

    File upload objects are used to represent file-uploaded data.

    File upload objects can be used just like files.

    In addition, they have a 'headers' attribute that is a dictionary
    containing the file-upload headers, and a 'filename' attribute
    containing the name of the uploaded file.

    This implementation is using a persistent tmp file reference which only
    get removed on transaction doom.

    Use the TMPFileUploadMixin in your request class for using the tmp file
    based upload concept
    """

    def __init__(self, aFieldStorage):

        file = aFieldStorage.file
        # first close the file for all future processing
        file .close()
        self.tmpFile = file

        if hasattr(file, '__methods__'):
            methods = file.__methods__
        else:
            methods = ['close', 'fileno', 'flush', 'isatty',
                'read', 'readline', 'readlines', 'seek',
                'tell', 'truncate', 'write', 'writelines',
                'name']

        for m in methods:
            if hasattr(file, m):
                self.__dict__[m] = getattr(file, m)

        self.headers = aFieldStorage.headers
        self.filename = str(aFieldStorage.filename, 'UTF-8')


class TMPUploadMixin(object):
    """TMP file uplaod mixin class

    NOTE: this mixin class requires a tmp file upload storage like defined
    in p01.tmp and p01.fsfile.
    """

    fileUploadFactory = TMPFileUpload

    @property
    def tmpFileFactoryArguments(self):
        """Returns tmp file factory arguments"""
        return None

    def tmpFileFactory(self):
        return p01.tmp.interfaces.ITMPFile(self)


class ZopeUploadMixin(object):
    """Default file input stream upload mixin class"""

    fileUploadFactory = zope.publisher.browser.FileUpload

    @property
    def tmpFileFactoryArguments(self):
        """Returns tmp file factory arguments"""
        return {'max_size': UPLOAD_SPOOLED_MAX_SIZE, 'mode': 'w+b'}

    @property
    def tmpFileFactory(self):
        return tempfile.SpooledTemporaryFile


@zope.interface.implementer(interfaces.IBrowserRequest,
    IBrowserApplicationRequest)
class BrowserRequest(ZopeUploadMixin, HTTPRequest):

    __slots__ = (
        '__provides__', # Allow request to directly provide interfaces
        'form',         # Form data
        'raw',          # raw body data
        # 'json',         # decoded json data
        'charsets',     # helper attribute
        '__meth',
        '__tuple_items',
        '__defaults',
        '__annotations__',
        )

    # Set this to True in a subclass to redirect GET requests when the
    # effective and actual URLs differ.
    use_redirect = False

    def __init__(self, body_instream, environ, response=None):
        self.form = {}
        self.raw = None
        self.charsets = None
        super(BrowserRequest, self).__init__(body_instream, environ, response)

    def _createResponse(self):
        return p01.publisher.response.BrowserResponse()

    def _decode(self, text):
        """Try to decode the text using one of the available charsets."""
        # According to PEP-3333, in python-3, QUERY_STRING is a string,
        # representing 'latin-1' encoded byte array. So, if we are in python-3
        # context, encode text as 'latin-1' first, to try to decode
        # resulting byte array using user-supplied charset.
        if not isinstance(text, bytes):
            text = text.encode('latin-1')
        if self.charsets is None:
            envadapter = IUserPreferredCharsets(self)
            self.charsets = envadapter.getPreferredCharsets() or ['utf-8']

            self.charsets = [c for c in self.charsets if c != '*']
        for charset in self.charsets:
            try:
                text = _u(text, charset)
                break
            except UnicodeError:
                pass
        # Ensure the text is decoded (avoid mix bin and str)
        return ensure_str(text)

    def json(self, **kwargs):
        """Convert to json data"""
        if self.raw is not None:
            # ensure unicode
            if not isinstance(self.raw, str):
                raw = self._decode(self.raw)
            else:
                raw = self.raw
            return self.getJSONData(raw, **kwargs)

    def processInputs(self):
        """See IPublisherRequest"""
        fp = None
        if self.method not in ['GET', 'HEAD']:
            # Process self.form if not a GET request.
            fp = self._body_instream
            if self.method == 'POST':
                ct = self._environ.get('CONTENT_TYPE')
                if ct and ct.startswith((
                    'application/json',
                    'application/x-json',
                    )):
                    # process given body stream
                    buf = []
                    chunk = fp.read(1024)
                    while chunk:
                        buf.append(chunk)
                        chunk = fp.read(1024)
                    # bytes, decode later
                    self.raw = b"".join(buf)
                    # return here, we do not support additional query string
                    # params
                    return
                if ct and not ct.startswith(
                    ('multipart/', 'application/x-www-form-urlencoded')):
                    # for non-multi and non-form content types, cgi parser
                    # consumes the body and we have no good place to put it.
                    return

        fslist = p01.cgi.parser.parseFormData(self.method, inputStream=fp,
            environ=self._environ, tmpFileFactory=self.tmpFileFactory,
            tmpFileFactoryArguments=self.tmpFileFactoryArguments)

        if fslist is not None:
            self.__meth = None
            self.__tuple_items = {}
            self.__defaults = {}

            # process all entries in the field storage (form)
            for item in fslist:
                self.__processItem(item)

            if self.__defaults:
                self.__insertDefaults()

            if self.__tuple_items:
                self.__convertToTuples()

            if self.__meth:
                self.setPathSuffix((self.__meth,))

    _typeFormat = re.compile('([a-zA-Z][a-zA-Z0-9_]+|\\.[xy])$')

    def __processItem(self, item):
        """Process item in the field storage and use FileUpload."""

        # Note: A field exists for files, even if no filename was
        # passed in and no data was uploaded. Therefore we can only
        # tell by the empty filename that no upload was made.
        key = item.name
        if p01.cgi.interfaces.IMultiPartField.providedBy(item) \
            and item.file is not None and \
            (item.filename is not None and item.filename != ''):
            item = self.fileUploadFactory(item)
        else:
            item = item.value

        flags = 0
        converter = None

        # Loop through the different types and set
        # the appropriate flags
        # Syntax: var_name:type_name

        # We'll search from the back to the front.
        # We'll do the search in two steps.  First, we'll
        # do a string search, and then we'll check it with
        # a re search.
        while key:
            pos = key.rfind(":")
            if pos < 0:
                break
            match = self._typeFormat.match(key, pos + 1)
            if match is None:
                break

            key, type_name = key[:pos], key[pos + 1:]

            # find the right type converter
            c = get_converter(type_name, None)

            if c is not None:
                converter = c
                flags |= CONVERTED
            elif type_name == 'list':
                flags |= SEQUENCE
            elif type_name == 'tuple':
                self.__tuple_items[key] = 1
                flags |= SEQUENCE
            elif (type_name == 'method' or type_name == 'action'):
                if key:
                    self.__meth = key
                else:
                    self.__meth = item
            elif (type_name == 'default_method'
                    or type_name == 'default_action') and not self.__meth:
                if key:
                    self.__meth = key
                else:
                    self.__meth = item
            elif type_name == 'default':
                flags |= DEFAULT
            elif type_name == 'record':
                flags |= RECORD
            elif type_name == 'records':
                flags |= RECORDS
            elif type_name == 'ignore_empty' and not item:
                # skip over empty fields
                return

        if key is not None:
            key = self._decode(key)

        if isinstance(item, (str, bytes)):
            item = self._decode(item)

        if flags:
            self.__setItemWithType(key, item, flags, converter)
        else:
            self.__setItemWithoutType(key, item)

    def __setItemWithoutType(self, key, item):
        """Set item value without explicit type."""
        form = self.form
        if key not in form:
            form[key] = item
        else:
            found = form[key]
            if isinstance(found, list):
                found.append(item)
            else:
                form[key] = [found, item]

    def __setItemWithType(self, key, item, flags, converter):
        """Set item value with explicit type."""
        #Split the key and its attribute
        if flags & REC:
            key, attr = self.__splitKey(key)

        # defer conversion
        if flags & CONVERTED:
            try:
                item = converter(item)
            except:
                if item or flags & DEFAULT or key not in self.__defaults:
                    raise
                item = self.__defaults[key]
                if flags & RECORD:
                    item = getattr(item, attr)
                elif flags & RECORDS:
                    item = getattr(item[-1], attr)

        # Determine which dictionary to use
        if flags & DEFAULT:
            form = self.__defaults
        else:
            form = self.form

        # Insert in dictionary
        if key not in form:
            if flags & SEQUENCE:
                item = [item]
            if flags & RECORD:
                r = form[key] = Record()
                setattr(r, attr, item)
            elif flags & RECORDS:
                r = Record()
                setattr(r, attr, item)
                form[key] = [r]
            else:
                form[key] = item
        else:
            r = form[key]
            if flags & RECORD:
                if not flags & SEQUENCE:
                    setattr(r, attr, item)
                else:
                    if not hasattr(r, attr):
                        setattr(r, attr, [item])
                    else:
                        getattr(r, attr).append(item)
            elif flags & RECORDS:
                last = r[-1]
                if not hasattr(last, attr):
                    if flags & SEQUENCE:
                        item = [item]
                    setattr(last, attr, item)
                else:
                    if flags & SEQUENCE:
                        getattr(last, attr).append(item)
                    else:
                        new = Record()
                        setattr(new, attr, item)
                        r.append(new)
            else:
                if isinstance(r, list):
                    r.append(item)
                else:
                    form[key] = [r, item]

    def __splitKey(self, key):
        """Split the key and its attribute."""
        i = key.rfind(".")
        if i >= 0:
            return key[:i], key[i + 1:]
        return key, ""

    def __convertToTuples(self):
        """Convert form values to tuples."""
        form = self.form

        for key in self.__tuple_items:
            if key in form:
                form[key] = tuple(form[key])
            else:
                k, attr = self.__splitKey(key)

                # remove any type_names in the attr
                i = attr.find(":")
                if i >= 0:
                    attr = attr[:i]

                if k in form:
                    item = form[k]
                    if isinstance(item, Record):
                        if hasattr(item, attr):
                            setattr(item, attr, tuple(getattr(item, attr)))
                    else:
                        for v in item:
                            if hasattr(v, attr):
                                setattr(v, attr, tuple(getattr(v, attr)))

    def __insertDefaults(self):
        """Insert defaults into form dictionary."""
        form = self.form

        for keys, values in list(self.__defaults.items()):
            if not keys in form:
                form[keys] = values
            else:
                item = form[keys]
                if isinstance(values, Record):
                    for k, v in list(values.items()):
                        if not hasattr(item, k):
                            setattr(item, k, v)
                elif isinstance(values, list):
                    for val in values:
                        if isinstance(val, Record):
                            for k, v in list(val.items()):
                                for r in item:
                                    if not hasattr(r, k):
                                        setattr(r, k, v)
                        elif not val in item:
                            item.append(val)

    def traverse(self, obj):
        """See IPublisherRequest"""
        ob = super(BrowserRequest, self).traverse(obj)
        method = self.method

        base_needed = 0
        if self._path_suffix:
            # We had a :method variable, so we need to set the base,
            # but we don't look for default documents any more.
            base_needed = 1
            redirect = 0
        elif method in DEFAULTABLE_METHODS:
            # We need to check for default documents
            publication = self.publication

            nsteps = 0
            ob, add_steps = publication.getDefaultTraversal(self, ob)
            while add_steps:
                nsteps += len(add_steps)
                add_steps = list(add_steps)
                add_steps.reverse()
                self.setTraversalStack(add_steps)
                ob = super(BrowserRequest, self).traverse(ob)
                ob, add_steps = publication.getDefaultTraversal(self, ob)

            if nsteps != self._endswithslash:
                base_needed = 1
                redirect = self.use_redirect and method == 'GET'


        if base_needed:
            url = self.getURL()
            response = self.response
            if redirect:
                response.redirect(url)
                return ''
            elif not response.getBase():
                response.setBase(url)

        return ob

    def keys(self):
        """See Interface.Common.Mapping.IEnumerableMapping"""
        d = {}
        d.update(self._environ)
        d.update(self._cookies)
        d.update(self.form)
        return list(d.keys())

    def get(self, key, default=None):
        """See Interface.Common.Mapping.IReadMapping"""
        result = self.form.get(key, _marker)
        if result is not _marker:
            return result

        return super(BrowserRequest, self).get(key, default)


###############################################################################
#
# json-rpc request

@implementer(interfaces.IJSONRPCRequest)
class JSONRPCRequest(HTTPRequest):
    """JSON-RPC request implementation based on IHTTPRequest.

    This implementation supports the following JSON-RPC Specification versions:

    - 1.0
    - 1.1
    - 2.0

    Version 1.0 and 1.1 offers params as a list. This params get converted to
    positional arguments if calling the JSON-RPC function.

    The version 2.0 offers support for named key/value params. The important
    thing to know is that this implementation will convert named params kwargs
    to form paramters. This means the method doesn't get any key word argument.

    The z3c.jsonrpc client JavaScript method JSONRPCProxy converts a
    typeof object as arguments[0] to named key/value pair arguments.

    """


    __slots__ = (
        '__provides__',
        '_root',
        '_args',
        '_cookies',
        '_jsonId',
        '_app',
        'app',
        # 'appURL',
        'charsets',
        'form',
        'jsonId',
        'jsonVersion',
        )

    appURL = property(lambda self: self.getApplicationURL())

    def __init__(self, body_instream, environ, response=None):
        self.form = {}
        self._root = None
        self._args = ()
        self._cookies = None
        self._jsonId = 'jsonrpc'
        self.charsets = None
        self.jsonId = None
        self.jsonVersion = JSON_RPC_VERSION
        super(JSONRPCRequest, self).__init__(body_instream, environ, response)

    def _createResponse(self):
        """return a response"""
        return p01.publisher.response.JSONRPCResponse()

    def _decode(self, text):
        """Try to decode the text using one of the available charsets."""
        # According to PEP-3333, in python-3, QUERY_STRING is a string,
        # representing 'latin-1' encoded byte array. So, if we are in python-3
        # context, encode text as 'latin-1' first, to try to decode
        # resulting byte array using user-supplied charset.
        if not isinstance(text, bytes):
            text = text.encode('latin-1')
        if self.charsets is None:
            envadapter = IUserPreferredCharsets(self)
            self.charsets = envadapter.getPreferredCharsets() or ['utf-8']
            self.charsets = [c for c in self.charsets if c != '*']
        for charset in self.charsets:
            try:
                text = _u(text, charset)
                break
            except UnicodeError:
                pass
        return text

    _typeFormat = re.compile('([a-zA-Z][a-zA-Z0-9_]+|\\.[xy])$')

    def processInputs(self):
        """take the converted request and make useful args of it."""
        stream = self._body_instream
        chunks = []
        chunk = stream.read(1024)
        while chunk:
            chunks.append(chunk)
            chunk = stream.read(1024)

        # input = ''.join(chunk)
        # # ensure unicode
        # if not isinstance(input, str):
        #     input = self._decode(input)
        # try:
        #     data = self.getJSONData(input)
        # except:
        #     # catch any error since we don't know which library is used as
        #     # parser
        #     raise p01.jsonrpc.exception.ParseError
        # bytes
        raw = b"".join(chunks)
        text = self._decode(raw)
        try:
            data = self.getJSONData(text)
        except Exception:
            # catch any error since we don't know which library is used as
            # parser
            raise p01.jsonrpc.exception.ParseError

        # get the params
        params = data.get('params', [])
        if self.jsonId is None:
            self.jsonId = data.get('id', self._jsonId)

        # get the json version. The version 1.0 offers no version argument.
        # The version 1.1 offers a version key and since version 2.0 the
        # version is given with the ``jsonrpc`` key. Let's try to find the
        # version for our request.
        self.jsonVersion = data.get('version', self.jsonVersion)
        self.jsonVersion = data.get('jsonrpc', self.jsonVersion)
        if self.jsonVersion in ['1.0', '1.1', '2.0']:
            # json-rpc 1.0 and 1.1
            if isinstance(params, list):
                args = params
                # version 1.0 and 1.1 uses a list of arguments
                for arg in args:
                    if isinstance(arg, dict):
                        # set every dict key value as form items and support at
                        # least ``:list`` and ``:tuple`` input field name postifx
                        # conversion.
                        for key, d in list(arg.items()):
                            key = str(key)
                            pos = key.rfind(":")
                            if pos > 0:
                                match = self._typeFormat.match(key, pos + 1)
                                if match is not None:
                                    key, type_name = key[:pos], key[pos + 1:]
                                    if type_name == 'list' and not isinstance(d, list):
                                        d = [d]
                                    if type_name == 'tuple' and not isinstance(d, tuple):
                                        d = tuple(d)
                            self.form[key] = d
            elif isinstance(params, dict):
                # process the key/value pair params. This arguments get stored
                # in the request.form argument and we skip it from method calls.
                # This means this library will not support key word arguments
                # for method calls. It will instead store them in the form.
                # This has two reasons.
                # 1. Zope doesn't support kwargs in the publication
                #    implementation. It only supports positional arguments
                # 2. The JSON-RPC specification doesn't allow to use positional
                #     and keyword arguments on one method call
                # 3. Python doesn't allow to convert kwargs to positional
                #    arguments because a dict doesn't provide an order
                # This means you should avoid to call a method with kwargs.
                # just use positional arguments if possible. Or get them from
                # directly from the request or request.form argument in your
                # code. Let me know if this is a real problem for you and you
                # like to implement a different kwarg handling. We have some
                # ideas for add support for this.
                args = params
                # set every dict key value as form items and support at
                # least ``:list`` and ``:tuple`` input field name postifx
                # conversion.
                for key, d in list(args.items()):
                    key = str(key)
                    pos = key.rfind(":")
                    if pos > 0:
                        match = self._typeFormat.match(key, pos + 1)
                        if match is not None:
                            key, type_name = key[:pos], key[pos + 1:]
                            if type_name == 'list' and not isinstance(d, list):
                                d = [d]
                            if type_name == 'tuple' and not isinstance(d, tuple):
                                d = tuple(d)
                    self.form[key] = d
                args = []
            elif params is None:
                args = []
        else:
            raise TypeError(
                'Unsupported JSON-RPC version (%s)' % self.jsonVersion)
        self._args = tuple(args)
        # make environment, cookies, etc., available to request.get()
        super(JSONRPCRequest, self).processInputs()
        self._environ['JSONRPC_MODE'] = True

        # split here on '.' for get path suffix steps
        functionstr = data['method']
        function = functionstr.split('.')
        if function:
            # translate '.' to '/' in function to represent object traversal.
            self.setPathSuffix(function)

    def traverse(self, object):
        return super(JSONRPCRequest, self).traverse(object)

    def keys(self):
        """See Interface.Common.Mapping.IEnumerableMapping."""
        d = {}
        d.update(self._environ)
        d.update(self._cookies)
        d.update(self.form)
        return list(d.keys())

    def get(self, key, default=None):
        """See Interface.Common.Mapping.IReadMapping."""
        result = self.form.get(key, _marker)
        if result is not _marker:
            return result
        return super(JSONRPCRequest, self).get(key, default)

    def __getitem__(self, key):
        return self.get(key)
