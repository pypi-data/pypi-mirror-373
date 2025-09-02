This is a Mathics3 Python Module showing the classic "Hello, World!"
The purpose is to demonstrate how to write a Mathics3 Python Module which extends Mathics3 by adding a function, but written in Python.

You can also use this as a template to clone if you want to create your own Mathics3 Module.

To install in development mode (run code from the source tree):

::

   $ make develop


After installing inside Mathics3, you can load this using the
``LoadModule[]`` function.

Then the function ```Hello[]`` is available::

      $ mathicsscript
      In[1]:= LoadModule["pymathics.hello"]
      Out[1]= pymathics.hello

      In[2]:= Hello[]
      Out[2]:= Hello, World!

      In[2]:= Hello["everyone"]
      Out[2]:= Hello, everyone!

You can test with ``pytest``::

     $ pytest test

or simply::

     $ make check
