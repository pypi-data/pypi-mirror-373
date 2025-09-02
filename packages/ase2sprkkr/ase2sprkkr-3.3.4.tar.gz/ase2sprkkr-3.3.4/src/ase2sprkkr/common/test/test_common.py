import inspect
import tempfile
import asyncio

if __package__:
   from .init_tests import TestCase, patch_package
else:
   from init_tests import TestCase, patch_package
__package__, __name__ = patch_package(__package__, __name__)

from ..decorators import add_to_signature   # NOQA: E402
from ..process_output_reader import AsyncioFileReader  # NOQA: E402


class TestCommon(TestCase):

  def test_common(self):

    def f(a, b=2, **kwargs):
        return a,b,kwargs

    @add_to_signature(f)
    def ff(c=2, *args, **kwargs):
        return c,f(*args,**kwargs)

    self.assertEqual( ('c',('a',2, {'d':'d', 'e':'e'})),
                       ff('a',c='c', d='d', e='e'))
    self.assertEqual( ('c',('a','b', {'d':'d', 'e':'e'})),
                       ff('a','b','c', d='d', e='e'))
    self.assertTrue('a' in inspect.signature(ff).parameters)
    self.assertEqual('a', list(inspect.signature(ff).parameters.values())[0].name)

    @add_to_signature(f, prepend=True)
    def ff(c, *args, **kwargs):
        return c,f(*args,**kwargs)

    self.assertEqual( ('c',('a',2, {'d':'d', 'e':'e'})),
                       ff('c', 'a', d='d', e='e'))

    def f(c=1, d=5):
        return c,d

    @add_to_signature(f, prepend=True)
    def ff(a=2, d='d', *args, **kwargs):
        return a, f(d=d, *args, **kwargs)

    self.assertEqual( ('a', (1, 'c')),
                      ff('a', 'c')
                    )

    @add_to_signature(f, prepend=True)
    def ff(a=2, *args, d='d', **kwargs):
        return a, f(d=d, *args, **kwargs)

    self.assertEqual( ('a', ('c', 'd')),
                      ff('a', 'c')
                    )

    def f(*args):
       return args

    @add_to_signature(f)
    def ff(a,*args):
       return a, f(*args)

    self.assertEqual( ('a', ('c', 'd')),
                      ff('a', 'c', 'd')
                    )

    @add_to_signature(lambda:None)
    def ff(*args, c, **kwargs):
        return c
    self.assertEqual( 1, ff(c=1) )

    @add_to_signature(lambda x: x)
    def ff(*args, c, **kwargs):
        return c, args
    self.assertEqual((1,(2,)), ff(2,c=1) )

    @add_to_signature(lambda x: x)
    def ff(*args, c, **kwargs):
        return c, kwargs
    self.assertEqual((1,{'x':2}), ff(x=2,c=1) )

    @add_to_signature(lambda:None)
    def ff(a, *args, c, **kwargs):
        return a,c
    self.assertEqual((2,1), ff(2,c=1) )

    def f(a=1, b=2):
        return a,b

    @add_to_signature(f, excluding='b')
    def ff(c=1, *args, **kwargs):
        return c,f(b=5, *args, **kwargs)
    self.assertEqual((7,(3,5)), ff(3,7))
    self.assertEqual((7,(3,5)), ff(3,c=7))
    self.assertEqual((7,(3,5)), ff(a=3,c=7))

  def test_asyncio_file_reader(self):
    with tempfile.TemporaryFile(mode='w+b') as tfile:
      tfile.write(b"""First line\nSecond line\nHi, this is a very long file!! really!!! 12345123456789""")
      tfile.seek(0)
      ar = AsyncioFileReader(tfile, buffersize=5)
      self.assertAsyncEqual(b"First line\n", ar.readline())
      self.assertAsyncEqual(b"Second line\n", ar.readline())
      self.assertAsyncEqual(b"Hi, this", ar.readuntil(b'is'))
      self.assertAsyncEqual(b" is", ar.readuntil(b'is'))
      self.assertAsyncEqual(b" a very long file!! really!!!", ar.readuntil(b'!!!'))
      self.assertAsyncEqual(b" 12345123456", ar.readuntil(b'123456'))
      with self.assertRaises(asyncio.IncompleteReadError):
        self.runAsync(ar.readuntil(b'123456'))

  def test_cached_property(self):
      from ..decorators import cached_property

      class A():
        u = 1

        @cached_property
        def a(self):
            self.__class__.u+=1
            return self.__class__.u
      a=A()
      self.assertEqual(2, a.a)
      self.assertEqual(2, a.a)
      a.a=5
      self.assertEqual(5, a.a)
      self.assertEqual(5, a.a)
      del a.a
      self.assertEqual(3, a.a)
      self.assertEqual(3, a.a)
      a=A()
      self.assertEqual(4, a.a)
      self.assertEqual(4, a.a)

      class A():
        u = 1

        @cached_property
        def a(self):
            self.__class__.u+=1
            return self.__class__.u

        @a.setter
        def a(self, value):
            self.__dict__['a'] = value + 10

        @a.deleter
        def a(self):
            self.__dict__['a'] = 25

      a=A()
      self.assertEqual(2, a.a)
      self.assertEqual(2, a.a)
      a.a=5
      self.assertEqual(15, a.a)
      self.assertEqual(15, a.a)
      del a.a
      self.assertEqual(25, a.a)
      self.assertEqual(25, a.a)
      a=A()
      self.assertEqual(3, a.a)
      self.assertEqual(3, a.a)

      # test, that indirect decorator works
      def modifier(fce):
          def wrap(self):
              return fce(self)
          return cached_property(wrap)

      class A():
        u = 1

        @modifier
        def a(self):
            self.__class__.u+=1
            return self.__class__.u

        @modifier
        def b(self):
            self.__class__.u+=1
            return self.__class__.u

      a=A()
      self.assertEqual(2, a.a)
      self.assertEqual(2, a.a)
      self.assertEqual(3, a.b)
      self.assertEqual(3, a.b)
      self.assertEqual(2, a.a)
