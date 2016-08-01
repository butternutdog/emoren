Requires [pyhidapi](https://github.com/NF6X/pyhidapi).
which in turn requires [hidapi](https://github.com/signal11/hidapi)

On mac, this might work:

    brew install hidapi
    git clone https://github.com/NF6X/pyhidapi.git
    cd pyhidapi
    python setup.py install
    cd ..
    
Also, install the following:

    pip install cryptography
    
For plotting and saving binary dumps:

    pip install numpy
    pip install matplotlib
