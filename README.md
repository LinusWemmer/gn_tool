
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

Deploying to the server
-----------------------

Pack the image into a tar file and copy it over with scp:
```console
~$: docker build -t docker_image .
~$: docker save -o docker_image.tar docker_image
~$: scp -i ~/.ssh/id_rsa docker_image.tar root@<server-ip>:/root/
```

### First deployment

On the server, load the image and start it. Give the container a **name** — every later update
needs it to address the running container:
```console
~#: docker load -i docker_image.tar
~#: docker run --restart always -d --name inklusivomat \
      -p 8080:80 -v /var/app/reports:/app/reports docker_image
~#: curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8080/
```

### Updating a running server

`docker load` only replaces the *image*. The running container keeps its own copy of the old one and
serves the old code, and it still holds port 8080 — so starting the new one before removing the old
one fails with `Bind for 0.0.0.0:8080 failed: port is already allocated`. Run these five steps in
order:
```console
~#: docker load -i docker_image.tar                     # 1. bring in the new image
~#: docker stop inklusivomat                            # 2. stop the old container
~#: docker rm inklusivomat                              # 3. remove it -- "stop" alone is not
                                                        #    enough: --restart always brings a
                                                        #    stopped container back on reboot
~#: docker run --restart always -d --name inklusivomat \
      -p 8080:80 -v /var/app/reports:/app/reports docker_image     # 4. start the new one
~#: docker ps                                           # 5. check: "Up", 0.0.0.0:8080->80/tcp
~#: curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8080/   #    and answers with 200
```

Only once the new container is up and answering, clean up. `docker load` leaves the previous image
behind without a tag (it says `renaming the old one with ID sha256:… to empty string`), and each one
costs about 1.4 GB:
```console
~#: docker image prune                                  # 6. removes untagged images
```
Do not prune earlier — until the new container runs, the untagged image is what you fall back to
(`docker run … <image-id>`).

If a container from an older deployment has no name, `docker ps -a` shows which one publishes
`0.0.0.0:8080->80/tcp`; use its ID in steps 2 and 3, and remove any leftover container in state
`Created` from a failed `docker run` the same way. If `docker ps -a` lists nothing on that port,
something outside docker holds it — `ss -ltnp | grep 8080` names the process.


Possible Errors:
---------------
Small errors can occur in the software due to errors in the parsing from ParZu.


License
-------

gn_tool is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License (see LICENSE).

The files in postprocesser/DepSVG are from Kaarel Kaljurand's DepSVG library and are licensed under the LGPL (https://github.com/Kaljurand/DepSVG)

preprocesser/tokenizer.perl and preprocessing/nonbreaking_prefix.de are from the Moses toolkit and licensed under the LGPL (http://www.statmt.org/moses/)

preprocesser/punkt_tokenizer.py is from the NLTK and licensed under the Apache License 2.0 (https://github.com/nltk/nltk)
