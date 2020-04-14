#  ECE562 Semester Project
#  Direct-Mapped Cache Simulator
#  Brent Rubell and Christian Ellis

# imports
import math
from binascii import hexlify
from os import urandom


"""
# Notes!
# CACHE VARIABLES
# read counter, read hits counter, read miss counter
# write counter, write hits counter, write miss counter
# writeback counter

# STATE Matricies 
# LRU counters
# LFU counters
# Validity flags
# Dirty flags

# FUNCTIONS
# Read(index, tag) -> 0 miss / 1 hit, increment read counter

# create, read, write
"""

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

    self.tag_width = self.size - self.offset_width - self.index_width

    # Build physical memory, randomly generate values in physical memory
    self.memory = bytearray(urandom(self.addr_width ** 2))

    # Build cache
    self.cache = [0] * self.sets
    self.valid_bits = [0] * self.sets

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
      print("---Data---")
      print("Cache: ", self.cache)
      print("Valid Bits: ", self.valid_bits)
      print("Memory: ", self.memory)


  def read(self, address):
    self.counter_reads += 1
    # convert to binary string
    addr = "{0:b}".format(address)
    print("Address: ", addr)
    # calculate offset
    offset = addr[self.offset_width:0]
    print("Offset: ", offset)
    # calculate index
    idx = addr[self.index_width:self.offset_width]
    print("Index: ", idx)


### SIMULATOR ###
def main():
  # fixed parameters
  # TODO: take in from sys.argv
  print("\t * Creating Cache")
  addr_width = 4
  cache_size = 32
  block_size = 2
  print("Address Width: ", addr_width)
  print("Cache Size: ", cache_size)
  print("Block Size: ", block_size)

  myCache = CACHE(addr_width, cache_size, block_size, 1)

  print("Reading cache at 0x01")
  myCache.read(0x01)

if __name__ == '__main__':
    main()