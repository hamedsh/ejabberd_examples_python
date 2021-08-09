# ejabberd python example
some hobby codes with aioxmpp to working with ejabberd

## how to use
 - clone project
 - use poetry environment management or any other virtual environment and install requirements
 
 note: python version must be greater than 3.4
## simple_time_say.py
say time every second for subscribed accounts
 - run: `python3 simple_time_say.py -j [your local jabberd id] -p [your jabberd password]`. 
 example: `python3 simple_time_say.py -j tuser@localhost -p 111111`
 - use an ejabberd client, and login with another account. send `time` message to start time say, use `off` to turn it off
