import emoren as em
import sys
import time
import random
import numpy as np
import matplotlib.pyplot as plt 
from matplotlib.collections import LineCollection

savefile = 'emotiv-'
buffer_rows = 128 * 60 * 60 # An hours worth?

def plot(data):
    #data = data[::8,:] # Downsample a bit, not really meaningful to look at otherwise
    plt.clf()
    eeg_data = data[:,:14]
    quality_data = data[:,14:]
    samples, channels = eeg_data.shape
    seconds = samples / 128
    t = seconds * np.arange(samples, dtype=float)/samples
    ticklocs = []
    ax = plt.axes()
    plt.xlim(0, seconds)
    plt.xticks(np.arange(seconds))

    eeg_dmin = eeg_data.min()
    eeg_dmax = eeg_data.max()
    dr = (eeg_dmax - eeg_dmin)
    y0 = eeg_dmin
    y1 = (channels - 1) * dr + eeg_dmax
    
    quality_dmin = quality_data.min()
    quality_dmax = quality_data.max()

    quality_normalized = ((quality_data - quality_dmin) / (quality_dmax - quality_dmin + 1e-20)) * dr

    plt.ylim(y0, y1)
    segs, quality_segs = [], []

    for i in range(channels):
        segs.append(np.hstack((t[:, np.newaxis], eeg_data[:, i, np.newaxis])))
        quality_segs.append(np.hstack((t[:, np.newaxis], quality_normalized[:, i, np.newaxis])))
        ticklocs.append(i*dr)

    offsets = np.zeros((channels, 2), dtype=float)
    offsets[:, 1] = ticklocs

    lines = LineCollection(segs, offsets=offsets,
                           transOffset=None,
                           )

    lines2 = LineCollection(quality_segs, offsets=offsets,
                           transOffset=None,colors=['red']
                           )

    ax.add_collection(lines)
    ax.add_collection(lines2)
    # set the yticks to use axes coords on the y axis
    ax.set_yticks(ticklocs)
    ax.set_yticklabels([ 'O2', 'O1', 'F7', 'T8', 'F4', 'P7', 'AF3', 'T7', 'F8', 'P8', 'F3', 'FC5', 'AF4', 'FC6'])
    plt.xlabel('time (s)')
    plt.show(block=False)
    plt.pause(.000001)


def flush_buffer(data_buffer, filename, rowcount):  
    np.save(filename, data_buffer[0:rowcount])

if __name__ == "__main__":
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
       
        #while True:
        #    time.sleep(1/128)
        for packet in em.get_packets():
            counter_modulo = counter % buffer_rows
            timestamp = [int(time.time() * 1000)]
            #packet = [random.randint(-1000, 1000)] * (len(sensors) * 2 + 1)            
            #row = packet
            values = [packet.sensors[s]['value'] for s in sensors]
            quality = [packet.sensors[s]['quality'] for s in sensors]
            row = timestamp + values + quality
            data_buffer[counter_modulo] = row
            if counter_modulo == buffer_rows - 1:
                flush_buffer(data_buffer, savefile + str(time.time()), buffer_rows)
            
            if (counter % 128) == 0: # Each second
                start, stop = 0, 0
                window = 128 * 30 # Last minute
                if counter_modulo < window:
                    stop = window
                else:
                    stop = counter_modulo
                start = stop - window
                if start < 0:
                    start = 0

                plot(data_buffer[start:stop, 1:]) # Skip timestamp

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
        