""" Readers for processes outputs.

They employ asyncio to makes possible read stdio and stderr concurently.
"""

import asyncio
import functools
import subprocess
import os
import numpy as np
from .decorators import maybeclassmethod


class ProcessOutputReader:
  """
  Class, that run a process, optionally saves all the output of the process to a file,
  and pass the stdout and stderr of the process to its two async routines, read_error
  and read_output.

  The descendant can redefine the routines to parse the output (or its parts).
  """
  async def run_subprocess(self, read_args=[]):

      if self.directory:
         dr = os.getcwd()
         os.chdir(self.directory)
      else:
         dr = None
      proc = await asyncio.create_subprocess_exec(*self.cmd,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        **self.kwargs)
      if dr:
         os.chdir(dr)

      exception = None

      def replace_feed_data(stream_reader):
          nonlocal exception
          if stream_reader._buffer:
             if self.print_output is True:
                print(stream_reader._buffer.decode('utf8'))
             self.outfile.write(stream_reader._buffer)

          def feed_data(data):
              nonlocal exception
              try:
                if self.print_output is True:
                  print(data.decode('utf8'), end='')
                self.outfile.write(data)
              except Exception as e:
                if not exception:
                    exception = e
                raise
              fd(data)
          fd = stream_reader.feed_data
          stream_reader.feed_data = feed_data

      if self.outfile:
        replace_feed_data(proc.stdout)
        replace_feed_data(proc.stderr)

      out = await asyncio.gather(
          self.read_output(proc.stdout, *read_args),
          self.read_error(proc.stderr, *read_args),
          proc.wait(),
        )

      if exception:
         raise exception

      return self.result(*out)

  def result(self, output, error, wait):
      """ This function is for postprocessing the results.

      It is intended to be predefined in the descendants

      Parameters
      ----------

      output: mixed
        Result of the self.read_output

      error: mixed
        Result of the self.read_error

      wait: int
        The process return value

      Return
      ------

      out: mixed
        Currently, the tuple (output, error, return_code) is returned, however,
        subclasses can return anything they want.
      """

      if wait != 0:
         e = ValueError(f"The process ended with return value {wait}")
         e.output = output
         e.error = error
         raise e
      return output, error, wait

  def run(self, cmd, outfile, read_args=[], print_output=False, directory=None, **kwargs):
      self.cmd = cmd
      self.kwargs = kwargs
      try:
        self.outfile = outfile
        self.print_output = print_output
        self.directory = directory

        import logging
        logging.getLogger("asyncio").setLevel(logging.WARNING)
        out = asyncio.run( self.run_subprocess(read_args) )
      finally:
        if self.outfile:
           self.outfile.close()
      return out

  async def read_error(self, stderr, *args):
      while True:
          line=await stderr.readline()
          if not line:
             return
          print(line.decode('utf8'))

  async def read_output(self, stdout, *args):
      raise NotImplementedError('Please, redefine BaseProcess.read_output coroutine')

  @maybeclassmethod
  def result_from_file(self, cls, output, error=None, read_args=[], return_code=0, print_output=False):
      if not self:
          self = cls()
      return self.read_from_file(output, error, read_args, return_code, print_output)

  @maybeclassmethod
  def read_from_file(self, cls, output, error=None, read_args=[], return_code=0, print_output=False):
      """ Read the data from file."""
      if not self:
          self = cls()
      loop = asyncio.new_event_loop()
      self.print_output = print_output

      def out():
          with AsyncioFileReader(output) as air:
              task = loop.create_task(self.read_output(air, *read_args))
              return loop.run_until_complete(task)

      def err():
          if not error:
              return None
          with AsyncioFileReader(error) as air:
              task = loop.create_task(self.read_error(air, *read_args))
              return loop.run_until_complete(task)

      try:
          return self.result(out(), err(), return_code)
      finally:
          loop.close()


class AsyncioFileReader:
  """ File reader that mimics asyncio StreamReader.
      In fact, it is synchronous, but it offers the
      same interface as the asyncio StreamReader.
  """

  def __init__(self, filename, buffersize=8192):
      self.file = None   # just to set it in case the open fail
      self.file = open(filename, 'rb') if isinstance(filename, str) else filename
      self.buffersize = buffersize

  def close(self):
      if self.file:
          self.file.close()
          self.file=None

  def __del__(self):
      self.close()

  def __enter__(self):
      return self

  def __exit__(self, type, value, traceback):
      self.close()

  async def readline(self):
      return self.file.readline()

  @staticmethod
  @functools.lru_cache(maxsize=128)
  def separator_shifts(sep):
      shifts = np.ones(len(sep) + 1, dtype=int)
      shift = 1
      for pos in range(len(sep)):
        while shift <= pos and sep[pos] != sep[pos - shift]:
            shift += shifts[pos - shift]
        shifts[pos + 1] = shift
      return shifts

  async def readuntil(self, sep=b'\n'):
      lsep = len(sep)
      if lsep == 0:
          return b''

      # https://stackoverflow.com/questions/14128763/how-to-find-the-overlap-between-2-sequences-and-return-it
      shifts = self.separator_shifts(sep)

      # do the actual search
      # read the bytes into the array to avoid incrementing the array one by one
      out = b''
      buffer = bytearray(self.buffersize + lsep)
      bufEnd = 0
      bufPos = 0

      def result():
          if not out:
             return bytes(buffer[:bufPos])
          return out + bytes(buffer[:bufPos])

      startPos = 0
      matchLen = 0
      while True:
        if bufPos == bufEnd:
           if bufEnd >= self.buffersize:
              out += buffer[:bufEnd]
              bufEnd = bufPos = 0
           n = lsep - matchLen
           data = self.file.read(n)
           ldata = len(data)
           buffer[bufPos:bufPos + ldata] = data
           bufEnd += ldata
           if len(data) < n:
              raise asyncio.IncompleteReadError(result(), sep)
        c = buffer[bufPos]
        bufPos += 1
        while matchLen >= 0 and sep[matchLen] != c:
          startPos += shifts[matchLen]
          matchLen -= shifts[matchLen]
        matchLen += 1
        if matchLen == lsep:
           return result()


async def readline(stdout):
    line = await stdout.readline()
    if not line:
        raise EOFError()
    return line.decode('utf8')


async def readline_until(stdout, cond, can_end=True):
    while True:
        line = await stdout.readline()
        if not line:
            if can_end:
                return ''
            raise EOFError()
        if cond(line):
            return line.decode('utf8')
