
#Overview

Emoren reads EEG data from the EPOC+ headset. It is based on [emokit](https://github.com/openyou/emokit).
It differs from emokit by using python3 instead of python2, replaces Crypto with [cryptography](https://cryptography.io/en/latest/), and do not use gevents. 
To visualize the EEG data, numpy and matplotlib is required.

The script requires [pyhidapi](https://github.com/NF6X/pyhidapi),
which in turn requires [hidapi](https://github.com/signal11/hidapi).

#Install prerequisites

The scripts have been tested on MacOS X and with Ubuntu, with both python2 and python3.

###Mac hidapi installation

    brew install hidapi
    
###Linux hidapi installation:

    sudo apt-get install libudev-dev libusb-1.0-0-dev autotools-dev autoconf automake libtool
    git clone https://github.com/signal11/hidapi
    cd hidapi
    ./bootstrap
    ./configure
    make
    sudo make install
    cd ..
    
To make sure that the hidraw devices are readable, follow [these](http://askubuntu.com/questions/15570/configure-udev-to-change-permissions-on-usb-hid-device) instructions, a working config line might look like

    SUBSYSTEM=="hidraw", ATTRS{idVendor}=="1234", ATTRS{idProduct}=="ed02", MODE="0666"

Make sure the `idVendor` and `idProduct` matches your device, you can list usb devices with `lsusb`.

##All:

    pip install cryptography    <--- make sure you have libssl-dev and libffi-dev on linux
 
    git clone https://github.com/NF6X/pyhidapi.git
    cd pyhidapi
    # Under linux, to make sure you use the hidraw devices first, you might have to swap line 157 and 158 in hidapi/hidapi.py before installing
    python setup.py install
    cd ..

#Usage

Now if you run `python emoren.py` you should see that packets are received.

For plotting and saving binary dumps:

    pip install numpy
    pip install matplotlib
    
    # Capture data and visualize by running
    python plot.py
