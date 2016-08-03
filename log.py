"""
# Logger for emoren

Usage:

```
$> python log.py NAME_OF_LOGFILE
```

If no name is given for the logfile, it defaults to `emoren-`.

The logfile name will get a timestamp appended to it.
"""

import emoren as em
import sys
import time
import random
import numpy as np

buffer_rows = 128 * 60 * 60 # An hours worth?

def build_row(packet, sensors):
    timestamp = [int(time.time() * 1000)]
    values = [packet.sensors[s]['value'] for s in sensors]
    quality = [packet.sensors[s]['quality'] for s in sensors]
    return timestamp + values + quality

def flush_buffer(data_buffer, filename, rowcount):  
    np.save(filename, data_buffer[0:rowcount])

def main(savefile):
    sensors = list(em.sensor_bits.keys()) # TODO: gyros, battery
    width = len(sensors) * 2 + 1 # sensor data + sensor quality + timestamp
    print("Data will be saved in the format: ")
    print((str(["timestamp"] + sensors + [sensor + " quality" for sensor in sensors])))
    counter = 0
    counter_modulo = 0
    nodata = 0
    nodata_sleep = .1
    data_buffer = np.zeros([buffer_rows, width])
    
    try:
        for packet in em.get_packets():
            counter_modulo = counter % buffer_rows
            data_buffer[counter_modulo] = build_row(packet, sensors)
            if counter_modulo == buffer_rows - 1:
                flush_buffer(data_buffer, savefile + str(time.time()), buffer_rows)
            counter += 1

    except KeyboardInterrupt:
        print("Keyboard interrupt, exiting")
        exit()
    except:
        raise
    finally:
        if(counter_modulo > 0):
            print(("Writing final " + str(counter_modulo+1) + " rows"))
            flush_buffer(data_buffer, savefile + str(time.time()), counter_modulo+1)

if __name__ == "__main__":
    savefile = 'emotiv-' if len(sys.argv) == 1 else sys.argv[1]
    main(savefile)