FROM balenalib/rpi-raspbian

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update
RUN apt-get install build-essential python3-dev wiringpi p7zip-full python3-pip python3-pil wget chromium-browser
RUN pip3 install --no-cache-dir -r requirements.txt

#RUN wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz && \
#    tar zxvf bcm2835-1.60.tar.gz && \
#    cd bcm2835-1.60/ && \
#    ./configure --disable-dependency-tracking && \
#    make && \
#    make check && \
#    make install

RUN wget http://www.waveshare.net/w/upload/9/9a/12.48inch_e-Paper_Module_Code_RPI.7z

RUN 7z x 12.48inch_e-Paper_Module_Code_RPI.7z  -r -o./12.48inch_e-Paper_Module_Code && \
    chmod 777 -R 12.48inch_e-Paper_Module_Code

WORKDIR /usr/src/app/12.48inch_e-Paper_Module_Code/python/examples

COPY main.py ./

