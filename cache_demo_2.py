#  ECE562 Semester Project
#  Direct-Mapped Cache Simulator
#  Brent Rubell and Christian Ellis

import math
from binascii import hexlify
from os import urandom
import csv
import random

class CACHE:
  def __init__(self, addr_width, cache_size, block_size, assoc = 1, replacement='LRU',
               is_debug=True):
    """Creates a new cache object. 
    :param int addr_width: Address width, in bits.
    :param int cache_size: Size of cache object, in bytes.
    :param int block_size: Size of memory block in cache, in bytes.
    :param int assoc: Associativity
    :param str replacement: Cache replacement policy.
    :param bool is_debug: Debugging enabled?

    """
    self.debug = is_debug
    self.addr_width = addr_width
    self.size = cache_size
    self.block_size = block_size
    self.assoc = assoc
    # eviction method
    self.replacement = replacement
    
    # Number of sets = cache size / Associtivity * Block Size
    self.sets = int(self.size / self.assoc * self.block_size)

    # offset width
    self.offset_width = int(math.log2(block_size))

    # m=4, c=32, k =2, e=1
    self.index_width = int(math.log2(self.size/self.block_size/self.assoc))

    self.tag_width = self.addr_width - self.offset_width - self.index_width

    self.tag_shift = int(math.log(self.size // 1, 2))
    self.set_shift = int(math.log(self.block_size, 2))

    # Build physical memory, randomly generate values in physical memory
    self.memory = bytearray(urandom(self.size ** 2))

    # Build cache
    self.lines = int(self.size/self.block_size)
    self.cache = [0] * self.lines

    self.cache_data =  [[0 for x in range(0, self.block_size)] for x in range(0, self.lines)]

    self.addresses = [0] * 8

    # Management bits
    self.tag_bits = [1] * self.lines # NOTE: 1 = unused
    self.valid_bits = [0] * self.lines
    self.dirty_bits = [0] * self.lines

    # counters
    self.counter_reads = 0
    self.counter_read_hit = 0
    self.counter_read_miss = 0

    self.counter_writes = 0
    self.counter_write_hit = 0
    self.counter_write_miss = 0

    if self.debug:
      print("--- Cache Details ---")
      print("# Sets: ", self.sets)
      print("Offset Width: ", self.offset_width)
      print("Index Width: ", self.index_width)
      print("Tag Width: ", self.tag_width)
      print("----------------------")


  def split_tio(self, address):
    """Breaks down address into tag, index, offset.
    Returns: tag, index, offset
    """
    if self.debug:
      print("Splitting T.I.O...")
    # calculate tag
    tag = address >> self.tag_shift

    # calculate index
    set_mask = self.size // self.block_size
    set_mask = (self.size // (self.block_size * 1)) - 1
    set_num = (address >> self.set_shift) & set_mask
    index = set_num * 1

    # calculate offset
    offset = address & (self.block_size - 1)
    
    if self.debug:
      print("Tag: {}\nIndex: {}\nOffset: {}".format(tag, index, offset))

    return tag, index, offset

  def write(self, address, data):
    """Writes a byte to a cache address.

    """
    # inc. write counter
    self.counter_writes += 1

    # split addr into TIO
    tag, index, offset = self.split_tio(address)
    if self.debug:
      print("Looking for Tag #", tag)

    if self.tag_bits[index] == 1:
      # if tag bit at set index is unused
      if self.debug:
        print("Write: {} = Miss".format(hex(address)))

      # set tag bit
      self.tag_bits[index] = 0
      self.valid_bits[index] = 1
      self.counter_write_miss += 1
    else:
        if self.debug:
          print("Write: {} = Hit".format(hex(address)))
        self.counter_write_hit += 1

    # read block into cache from memory at address
    for i in range(0, self.block_size-offset):
      self.cache_data[index][offset+i] = self.memory[index+offset+i]

    # set dirty bit
    self.dirty_bits[index] = 1
    # write back byte into cache
    self.cache_data[index][offset] = data

    # return data at address
    return self.cache_data[index][offset]

  def read(self, address):
    """Reads an address from the cache.
    Returns data from address.
    :param int address: Cache address.

    """
    # inc. read counter
    self.counter_reads += 1

    # split addr. into TIO
    tag, index, offset = self.split_tio(address)

    if self.valid_bits[index] == 1:
      if self.cache[index] == tag:
        if self.debug:
          print("Read: {} = Hit".format(hex(address)))
        self.counter_read_hit += 1
      else:
        if self.debug:
          print("Read: {} = Miss".format(hex(address)))
        self.valid_bits[index] = 1
        self.cache[index] = tag
        self.counter_read_miss += 1
    else:
      if self.debug:
        print("Read: {} = Miss".format(hex(address)))
      self.valid_bits[index] = 1
      self.cache[index] = tag
      self.counter_read_miss += 1

    # pull block_size blocks from physical memory into cache
    for i in range(0, self.block_size - offset):
      try:
        self.cache_data[index][offset+i] = self.memory[index+offset+i]
      except:
        print("Buffer Overflow - Not enough memory, more cache memory than main memory?")
        pass
    # increment the total counter reads
    self.counter_reads += 1

    # return data at address
    return self.cache_data[index][offset]

  def flush_cache(self):
    """Flushes cache data."""
    self.cache_data =  [[0 for x in range(0, 2)] for x in range(0, self.lines)]

  # graphical utils.
  def print_cache(self):
    """Displays contents of cache"""
    print("------CACHE-----")
    print("[add]+off.| data")
    print("----------------")
    for i in range(0, self.lines):
      for j in range(0, self.block_size):
        print("[{}]+{}: ".format(hex(i), hex(j)), end="")
        print(hex(self.cache_data[i][j]))
    print("----------------")
  
  def print_physical_memory(self):
    """Displays contents of phy. memory"""
    for i in range(0, 4):
      print(hex(self.memory[i]))

  def cache_stats(self):
    """Display cache counter statistics."""
    # print("total reads: {}\ntotal writes: {}\n".format(self.counter_reads, self.counter_writes))
    # print("read hits: {}\nread misses:{}\n".format(self.counter_read_hit, self.counter_read_miss))
    return ([
      self.size, self.block_size,
      self.counter_reads, self.counter_writes,
      self.counter_read_hit, self.counter_read_miss,
      self.counter_write_hit, self.counter_write_miss
    ])


### "Simulator" ###
def main():
  # -- cache parameters --- #
  addr_width = 4
  cache_size = 8
  block_size = 2

  print("-- Cache Details --")
  print("Address Width: ", addr_width)
  print("Cache Size: ", cache_size)
  print("Block Size: ", block_size)
  print("-------------------")

  # init. cache object without verbose output
  myCache = CACHE(addr_width, cache_size, block_size, 1, is_debug=True)

  # Read from memory location 0x00
  data = myCache.read(0x00)

  # dump data from cache
  myCache.print_cache()

	# Write byte 0x01 to memory location 0x03
  myCache.write(0x03, 0x01)

	# Read from memory location 0x03
  data = myCache.read(0x03)

  # dump data from cache
  myCache.print_cache()
  # display cache stats
  myCache.cache_stats()

if __name__ == '__main__':
    main()