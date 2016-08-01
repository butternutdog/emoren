Script based on [emokit](https://github.com/openyou/emokit). It uses python3 instead of python2, replaces Crypto with [cryptography](https://cryptography.io/en/latest/), and do not use gevents. Instead of rendering with pygame a simple plot with matplotlib is available.
Requires [pyhidapi](https://github.com/NF6X/pyhidapi).
which in turn requires [hidapi](https://github.com/signal11/hidapi)

Scripts below are tested on a mac with python3 and pip3 and brew installed.
Install prerequisites:

    brew install hidapi
    git clone https://github.com/NF6X/pyhidapi.git
    cd pyhidapi
    python setup.py install
    cd ..

    pip install cryptography

Now if you run `python emoren.py` you should see that packets are received.

For plotting and saving binary dumps:

    pip install numpy
    pip install matplotlib
    
    # Capture data and visualize by running
    python plot.py
