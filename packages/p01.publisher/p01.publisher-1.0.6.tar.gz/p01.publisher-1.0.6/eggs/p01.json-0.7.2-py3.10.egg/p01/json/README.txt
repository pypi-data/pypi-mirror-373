======
README
======

Let's test the json reader and writer methods.


jsonWriter
----------

The json writer method is by default a pointer to the json.dumps method:

  >>> from p01.json.api import jsonWriter
  >>> jsonWriter
  <function jsonWriter at ...>

Read some data:

  >>> input = {u'a': ['fred', 7],
  ...          u'b': ['mary', 1.234]}
  >>> jsonStr = jsonWriter(input)
  >>> jsonStr
  '{"a":["fred",7],"b":["mary",1.234]}'


jsonReader
----------

The json reader method is by default a pointer to the json.loads method:

  >>> from p01.json.api import jsonReader
  >>> jsonReader
  <function jsonReader at ...>

Convert the data back to python:

  >>> output = jsonReader(jsonStr)
  >>> output
  {...'a': [...'fred', 7], ...'b': [...'mary', 1.234]}

  >>> input == output
  True