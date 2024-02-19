
This tool is a tool to help convert German text to the de-e system proposed by the VfGD (https://geschlechtsneutral.net/gesamtsystem/).
To parse the input text, we use the ParZu dependency parser for German, which can be found here:  http://github.com/rsennrich/parzu

Requirements:
-------------
Flask package for python.

Clevertagger: https://github.com/rsennrich/clevertagger

Zmorge: https://pub.cl.uzh.ch/users/sennrich/zmorge/ (The tool was programmed with zmorge-20150315-smor_newlemma.ca, so I recommend using that instance).

The software was developed using the following:

    Linux (32 and 64 bit)
    SWI-Prolog 9.04 
    Python 3.8
    Perl 5

Local installation:
-------------------

1. Install all required software

2. Git clone this directory to your own directory.

3. In the config.ini file, change the following filepaths:
    - taggercmd to you clevertagger installation
    - smor_model to your zmorge model

Usage:
------

You can run the program locally by running __init__.py. You should then find the program running on localhost:4000.

Docker:
------

You can build the docker image by calling:
```console
~$: sudo docker build -t docker_image .
```

To then run the image in a container, you can call:
```console
~$: sudo docker run -p 80:80 -v /path/to/file/reports:/app/reports docker_image
```
You will then find the app running on http://localhost:80.

In order to run transfer the docker image to a server, you need to pack it into a tar file and then copy to the server using scp:
```console
~$: sudo docker save -o docker_image.tar docker_image
~$: sudo scp -i ~/.ssh/id_rsa docker_image.tar root@<server-ip>:/root/ 
```
On the server, you need to unpack the docker image and then run it:
```console
~$: docker load -i docker_image.tar
~$: docker run -d -p 8080:80 -v /var/app/reports:/app/reports docker_image
```


Possible Errors:
---------------
Small errors can occur in the software due to errors in the parsing from ParZu.


