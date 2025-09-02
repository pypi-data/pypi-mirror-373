======
README
======

This package offers a bridge between wsgi and the zope publication stack. It
offers a wsgi application whcih is used as a replacement for the ZODB root
application and starts the zope publicaiton concept including transaction and
error handling.

In other words it's a wsgi application framework which supports the zope
component and traversal concepts and doesn't require to use routes or other
knwonn concept. So you can stay with the existing zope adapter, views, pages,
namespace traversal, file or cdn resources and all you already know from zope.


no ZODB
-------

This package is a zope.app.Publication package replacement for projects without
a ZODB database. Instead of the db (database) attribute the wsgi application is
passed to the prublisher. The concept is simple. the package offers a wsgi
application which is configred within paste deploy using a zope.conf and
paste.ini file. See p01.recipe.setup:paste for a zc.buildout recipe.


application
-----------

The wsgi application is used as a replacement for the root application normaly
located in the ZODB as the root application. This allows us to use any ORM
or similar database to object mapping concept and use gevent or similar
concepts for performance.


transaction
-----------

Of corse transactions is a part of the zope publication stack and is supported
including zope error handling.


zope component
--------------

This package depends and integrates with the normal zope component stack and
uses the zope.publisher request/response components.


improvements
------------

We also improved different concepts. One interesting part is the transaction
and request handling order. Zope by default reads the request body and later
applies the transaction. We apply the transaction first and read the request
input. This allows us to observe the incomming request input and write
incoming file uploads to a temp file and remove the file on abort. The file
upload handling is not a part of this implememntation. It's up to you to
implement a transaction observed file upload. Or you can use the 


zope.app.appsetup
-----------------

The p01.publisher doesn't depend on zope.app.appsetup and it's a zope app
specific part. We just copied the product config part from zope.app.appsetup
and support the product config based on ZConfig. Also known as zope.conf product setup.


ILoggingInfo
------------

We do not provide ILoggingInfo. This should be a part of your wsgi logging
middleware. Or even better, do if like we do, just implement an own zope.error
utility and catch errors as early as possible instead of push them trough the 
wsgi stack. Or provide an own wsgi server handler which catches what you need.
We implemented our sentry handler in such a gevent wsgi server handler.


wsgi
----

The package provides a generic wsgi application factory. Implement you own
application factory and register them as IWSGIApplication utility. Then your
done and your pages could get served with a zc.buildout paste setup using the
p01.recipe.setup:paste recipe.


server
------

The implementation doesn't depend on a specific wsgi server. Anything can get
used which is compatible with a paste deploy setup. And if thsi doesn't fit,
just define your own server_factory and define an entry point in your package
fir such a custom factory. We use circus and as you probably know, they use
sokets as request input. We just defined a similar concept like defined in 
chaussette and use them as our server factory.


jsonrpc
-------

The p01.publisher depends on the z3c.josnrpc interfaces and provides a
replacement using ujson and uses applicaiton/json as content-type. The reason
why we do this is, that we need to provide the ZODB/wsgi replacment for the
jsonrpc publisher too.

The package includes customized configure.zcml files which will replace the
z3c.jsonrpc configure.zcml.


gevent
------

This implementation doesn't depend on geven, greenlet or eventlet but can get
used with them. We run our wsgi application with gevent and circus. If you do
so, doen't forget to apply an initializsation in your buildout setup which
makes sure that the method monkey.patch_all() get called. This implemntation
does not import gevent and does not call the monkey patch_all method. 


authentication
--------------

This package doesn't lookup placefull authentication. This means we do not try
to authenticate anonymous principal on every traversal step. We just provide
authentication calls on the wsgi application level. This sould not be a problem
for most applications. But don't worry, if you need them you can implement
placefull authentication as zope components. This only means we do not support
placefull authenticate by default.


not supported
-------------

This package doesn't support soap or xmlrpc at this time. Let me know if you
need a ZODB less replacement for this services.

The retry pattern is not supported. Requests are allways raise and handle errors
and never get retried.

Side effect adapters are also not supported.


contact
-------

Ok, that's not much information. But since this is just a wsgi application
stack setup which kicks in the zope publication concept including error
handling etc., it should be easy and simple to understand whats going on.
Of course an understanding how the default zope publication stack works
including transactions helps a lot. Otherwise just let me know if you need more
information.
