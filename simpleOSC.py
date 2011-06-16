
""" Basic module to ease the use of pyOSC module https://trac.v2.nl/wiki/pyOSC

you must have pyOSC installed for this to run.

This is meant to be used by students or newies that are starting to experiment with OSC. If you are an advanced user
you probably want to bypass this module and use directly pyOSC, we have some examples of very simple use in our website.
Check the pyOSC website for more documentation.

License : LGPL

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
    
"""

try :
    from OSC import *
except :
    print "Warning!!! you must have pyOSC installed -> https://trac.v2.nl/wiki/pyOSC"
    
import threading


basic_client = 0
basic_server = 0
st = 0


def printing_handler(addr, tags, data, source):
    print "---"
    print "received new osc msg from %s" % getUrlStr(source)
    print "with addr : %s" % addr
    print "typetags :%s" % tags
    print "the actual data is : %s" % data
    print "---"



def initOSCClient(ip='127.0.0.1', port=9000) :
    global basic_client
    basic_client = OSCClient()
    basic_client.connect( (ip,port) )
    
def initOSCServer(ip='127.0.0.1', port=9001, mode=0) :
    """ mode 0 for basic server, 1 for threading server, 2 for forking server
    """
    global basic_server, st

    if mode == 0 :
        basic_server = OSCServer( (ip ,port) ) # basic
    elif mode == 1 : 
        basic_server = ThreadingOSCServer( (ip ,port) ) # threading
    elif mode == 2 :
        basic_server = ForkingOSCServer( (ip ,port) ) # forking

    basic_server.addDefaultHandlers()
    st = threading.Thread( target = basic_server.serve_forever )
    st.start()

def setOSCHandler(address="/print", hd=printing_handler) :
    basic_server.addMsgHandler(address, hd) # adding our function

def closeOSC() :
    if basic_client is not 0 : basic_client.close()
    if basic_server is not 0: basic_server.close() 
    if st is not 0: st.join()

def reportOSCHandlers() :
    print "Registered Callback-functions are :"
    for addr in basic_server.getOSCAddressSpace():
        print addr
    
def sendOSCMsg( address='/print', data=[] ) :
    m = OSCMessage()
    m.setAddress(address)
    for d in data :
        m.append(d)
    basic_client.send(m)

def createOSCBundle() : # just for api consistency
    return OSCBundle()

def sendOSCBundle(b):
    basic_client.send(b)

def createOSCMsg(address='/print', data=[]) :
    m = OSCMessage()
    m.setAddress(address)
    for d in data :
        m.append(d)
    return m
