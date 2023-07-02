# lilTorrent
small clone of a real life torrent network implemented in python


## File descriptions
- STUN.py
    a stun server that keeps the info about peers in itself; Redis is used to implement this
- peer.py:
    the main file, containing initilizing of a peer, and being able to connect to other peers and sending or receiving data from each other
- request.py
    this file stores the different type of requests that can be made in the app as the following:
    - conncection request
    - random quote request
    - random image request
- utils.py:
    some util functions are iplemented in this file.
