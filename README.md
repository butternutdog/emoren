
Overview
--------

Emoren reads EEG data from the EPOC+ headset. It is based on [emokit](https://github.com/openyou/emokit).
It differs from emokit by using python3 instead of python2, replaces Crypto with [cryptography](https://cryptography.io/en/latest/), and do not use gevents. 
To visualize the EEG data, numpy and matplotlib is required.

The script requires [pyhidapi](https://github.com/NF6X/pyhidapi),
which in turn requires [hidapi](https://github.com/signal11/hidapi).

Install prerequisites
---------------------

Scripts below are tested on a mac with python3 and pip3 and brew installed.
Run: 

    brew install hidapi
    git clone https://github.com/NF6X/pyhidapi.git
    cd pyhidapi
    python setup.py install
    cd ..
    
    pip install cryptography

Usage
-----

Now if you run `python emoren.py` you should see that packets are received.

For plotting and saving binary dumps:

    pip install numpy
    pip install matplotlib
    
    # Capture data and visualize by running
    python plot.py
