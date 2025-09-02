This package provides a WSGI publisher concept using zope components including
transactions, application error handling, traverser, pages views and offers
jsonrpc without a ZODB. The package offers a wsgi application which kicks in
the known zope publication concept. The publication concept can get used with
gevent or similar async frameworks. It's up to you how you store persistent
items. Probably the container, item and traversal pattern in m01.mongo is a
good choice for this.
