## ePaper + Grafana Dashboard

#### Installation

Enable SPI on your raspberry pi (Interface Options > SPI)

```bash
$ sudo raspi-config
$ sudo reboot
```

Install software dependencies

```bash
$ sudo apt-get update
$ sudo apt-get install -y chromium-browser wiringpi python3-pip libopenjp2-7 python3-pip
```

Install hardware dependencies

```bash
$ wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz && \
    tar zxvf bcm2835-1.60.tar.gz && \
    cd bcm2835-1.60/ && \
    sudo ./configure && \
    sudo make && \
    sudo make check && \
    sudo make install
```

Install latest wiringPi

```bash
sudo apt-get -y install wiringpi && \
    cd /tmp && \
    wget https://project-downloads.drogon.net/wiringpi-latest.deb && \
    sudo dpkg -i wiringpi-latest.deb && \
    gpio -v
```

