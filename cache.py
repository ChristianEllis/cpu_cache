#  ECE562 Semester Project
#  Direct-Mapped Cache Simulator
#  Brent Rubell and Christian Ellis

# imports
import math
from binascii import hexlify
from os import urandom

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
    self.memory = bytearray(urandom(self.addr_width ** 2))

    # Build cache
    self.lines = int(self.size/self.block_size)
    self.cache = [0] * self.lines

    self.cache_data =  [[0 for x in range(0, 2)] for x in range(0, self.lines)]

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
    # calculate tag
    tag = address >> self.tag_shift

    # calculate index
    set_mask = self.size // self.block_size
    set_mask = (self.size // (self.block_size * 1)) - 1
    set_num = (address >> self.set_shift) & set_mask
    index = set_num * 1

    # calculate offset
    offset = address & (self.block_size - 1)
    return tag, index, offset

  def write(self, address, data):
    """Writes a byte to a cache address.

    """
    # inc. write counter
    self.counter_writes += 1

    # split addr into TIO
    tag, index, offset = self.split_tio(address)
    if self.debug:
      print("Tag: {}\nIndex: {}\nOffset: {}".format(tag, index, offset))

    if self.tag_bits[index] == 1:
      # if tag bit at set index is unused
      print("MISS!")

      # set tag bit
      self.tag_bits[index] = 0
      self.valid_bits[index] = 1

      # read block into cache from memory at address
      for i in range(0, self.block_size):
        self.cache_data[index][offset+i] = self.memory[index+offset+i]
      print('cache: ', self.cache_data)
      # set dirty bit
      self.dirty_bits[index] = 1
      # write back byte into cache
      self.cache_data[index][offset] = data
      print('cache: ', self.cache_data)
      

  def read(self, address):
    """Reads an address from the cache.
    Returns 1 if hit, 0 otherwise.
    :param int address: Cache address.

    """
    # inc. read counter
    self.counter_reads += 1

    # split addr. into TIO
    tag, index, offset = self.split_tio(address)

    if self.debug:
      print("Tag: {}\nIndex: {}\nOffset: {}".format(tag, index, offset))

    if self.valid_bits[index] == 1:
      if self.cache[index] == tag:
        print("Read: {} = Hit".format(hex(address)))
        self.counter_read_hit += 1
      else:
        print("Read: {} = Miss".format(hex(address)))
        self.valid_bits[index] = 1
        self.cache[index] = tag
        self.counter_read_miss += 1
    else:
      print("Read: {} = Miss".format(hex(address)))
      self.valid_bits[index] = 1
      self.cache[index] = tag
      self.counter_read_miss += 1

    # pull block_size blocks from physical memory into cache
    for i in range(0, self.block_size-1):
      self.cache_data[index][offset+i] = self.memory[index+offset+i]

    # increment the total counter reads
    self.counter_reads += 1

  def flush_cache(self):
    """Flushes cache data."""
    self.cache_data =  [[0 for x in range(0, 2)] for x in range(0, self.lines)]

  # graphical utils.
  def print_cache(self):
    """Displays contents of cache"""
    print("---cache dump---")
    for i in range(0, 4):
      print(self.cache_data[i])
    print("----------------")

  def cache_stats(self):
    """Display cache counter statistics."""
    print("total reads: {}\ntotal writes: {}\n".format(self.counter_reads, self.counter_writes))
    print("read hits: {}\nread misses:{}\n".format(self.counter_read_hit, self.counter_read_miss))


### SIMULATOR ###
def main():
  # -- cache parameters --- #
  addr_width = 4
  cache_size = 8
  block_size = 2
  print("Address Width: ", addr_width)
  print("Cache Size: ", cache_size)
  print("Block Size: ", block_size)

  myCache = CACHE(addr_width, cache_size, block_size, 1)


  myCache.write(0x00, 0x01)
  myCache.read(0x00)

  # print output of cache
  myCache.print_cache()
  # display cache stats
  myCache.cache_stats()

if __name__ == '__main__':
    main()