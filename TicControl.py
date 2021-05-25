# REQUIRED LIBRARIES
# smbus2, time
from smbus2 import SMBus, i2c_msg
import time

class TicI2C(object):
  def __init__(self, bus, address):
    self.bus = bus
    self.address = address

  # Sends the "de-energize" command. Will set the "position uncertain" flag after re-energizing
  def deenergize(self):
    command = [0x86]
    write = i2c_msg.write(self.address, command)
    self.bus.i2c_rdwr(write)

  # Sends the "energize" command. If manually de-energized, "position uncertain" will be high and need to be homed
  def energize(self):
    command = [0x85]
    write = i2c_msg.write(self.address, command)
    self.bus.i2c_rdwr(write)

  # Sets the target position in steps
  # Prevents movement commands from being sent again until movement completed
  def set_target_position(self, target):
    command = [0xE0,
      target >> 0 & 0xFF,
      target >> 8 & 0xFF,
      target >> 16 & 0xFF,
      target >> 24 & 0xFF]
    write = i2c_msg.write(self.address, command)
    self.bus.i2c_rdwr(write)

  # Gets one or more variables from the Tic
  def get_variables(self, offset, length):
    write = i2c_msg.write(self.address, [0xA1, offset])
    read = i2c_msg.read(self.address, length)
    self.bus.i2c_rdwr(write, read)
    return list(read)

  # Gets the "Current position" variable from the Tic
  def get_current_position(self):
    b = self.get_variables(0x22, 4)
    position = b[0] + (b[1] << 8) + (b[2] << 16) + (b[3] << 24)
    if position >= (1 << 31):
      position -= (1 << 32)
    return position

  # Homes Tic in given direction
  def home(self, direction):
    command = [0x97,
        direction]
    write = i2c_msg.write(self.address, command)
    self.bus.i2c_rdwr(write)

  # Set max speed in steps per 10k sec. Value is saved in RAM and reinitalized upon reset
  def set_max_speed(self, speed):
    command = [0xE6,
        speed >> 0 & 0xFF,
        speed >> 8 & 0xFF,
	speed >> 16 & 0xFF,
	speed >> 24 & 0xFF]
    write = i2c_msg.write(self.address, command)
    self.bus.i2c_rdwr(write)

  # Set starting speed in steps per 10k sec. Value is saved in RAM and reinitialized upon reset
  def set_starting_speed(self, speed):
    command = [0xE5,
	speed >> 0 & 0xFF,
	speed >> 8 & 0xFF,
	speed >> 16 & 0xFF,
	speed >> 24 & 0xFF]
    write = i2c_msg.write(self.address, command)
    self.bus.i2c_rdwr(write)

  # Check to ensure homing is complete
  def homing_complete(self):
    homing_complete = 1
    while homing_complete == 0x01:
         time.sleep(0.5)
         write = i2c_msg.write(self.address, [0xA1, 0x01]) # Check misc flags
         read = i2c_msg.read(self.address, 1)
         self.bus.i2c_rdwr(write, read)
         homing_complete = (int(list(read)[0]) >> 4) 
    return 1

  # Check to see if driver is moving
  def movement_complete(self):
    movement_complete = 1
    while movement_complete == 0x01 or movement_complete == 0x02:
         time.sleep(0.5)
         write = i2c_msg.write(self.address, [0xA1, 0x09]) # Check motion planning mode
         read = i2c_msg.read(self.address, 1)
         self.bus.i2c_rdwr(write, read)
         movement_complete = (int(list(read)[0]) >> 1)
    return 1
