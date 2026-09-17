
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

Before building, make sure `external/` holds the two Zmorge files, because `install.sh` can no
longer download them: the University of Zurich answers 403 for the directory and 404 for the files,
and the old host `kitt.ifi.uzh.ch` does not resolve at all. Copy them in by hand:
```console
~$: mkdir -p external
~$: cp /wherever/you/keep/zmorge-20150315-smor_newlemma.ca external/
~$: cp /wherever/you/keep/hdt_ab.zmorge-20140521-smor_newlemma.model external/
```
`install.sh` skips the download when the files are already there, and aborts with a clear message
when they are missing — do not ignore that, because an image built without them starts and then
dies on every request with `Cannot open transducer file`.

You can build the docker image by calling:
```console
~$: docker build -t docker_image .
```

To then run the image in a container, you can call:
```console
~$: docker run -p 80:80 -v /absolute/path/to/gn_tool/reports:/app/reports docker_image
```
The `-v` argument needs an **absolute path to the reports directory** (not to `reports.txt`);
a relative path is read as the name of a docker volume and rejected.
You will then find the app running on http://localhost:80.

If port 80 is already taken — a local Apache or nginx will hold it, and docker then reports
`failed to bind host port 0.0.0.0:80/tcp: address already in use` — either stop that server or map
the container to a free port instead, for example `-p 8080:80` and then http://localhost:8080.

`sudo` is only needed when your user is not in the `docker` group.

In order to transfer the docker image to a server, you need to pack it into a tar file and then copy to the server using scp:
```console
~$: sudo docker save -o docker_image.tar docker_image
~$: sudo scp -i ~/.ssh/id_rsa docker_image.tar root@<server-ip>:/root/ 
```
On the server, you need to unpack the docker image and then run it:
```console
~$: docker load -i docker_image.tar
~$: docker run --restart always -d -p 8080:80 -v /var/app/reports:/app/reports docker_image
```


Possible Errors:
---------------
Small errors can occur in the software due to errors in the parsing from ParZu.


License
-------

gn_tool is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License (see LICENSE).

The files in postprocesser/DepSVG are from Kaarel Kaljurand's DepSVG library and are licensed under the LGPL (https://github.com/Kaljurand/DepSVG)

preprocesser/tokenizer.perl and preprocessing/nonbreaking_prefix.de are from the Moses toolkit and licensed under the LGPL (http://www.statmt.org/moses/)

preprocesser/punkt_tokenizer.py is from the NLTK and licensed under the Apache License 2.0 (https://github.com/nltk/nltk)
