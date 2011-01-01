import os
import logging

def FileIterator(base, separator=os.path.sep):
  """Walks a directory tree, returning all the files. Follows symlinks.
  
  Args:
    base: The base path to search for files under.
    separator: Path separator used by the running system's platform.
  
  Yields:
    Paths of files found, relative to base.
  
  """
  dirs = ['']
  while dirs:
    current_dir = dirs.pop()
    for entry in os.listdir(os.path.join(base, current_dir)):
      name = os.path.join(current_dir, entry)
      fullname = os.path.join(base, name)
      if separator == '\\':
        name = name.replace('\\', '/')
      if os.path.isfile(fullname):
          yield name
      elif os.path.isdir(fullname):
          dirs.append(name)
