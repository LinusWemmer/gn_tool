
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

You can run the program locally by running getParse.py. You should then find the program running on localhost:5000.

Possible Errors:
---------------
Small errors can occur in the software due to errors in the parsing from ParZu, these issues cannot be fixed.


