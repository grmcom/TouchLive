import os; os.environ['PYMT_SHADOW_WINDOW'] = '0'
import sys
from pymt import *
from simpleOSC import *
import pygame
import pygame.midi
from pygame.locals import *




# User input for monome prefix etc.
mdevice=raw_input("Enter Midi Device Number: ")
prefix=raw_input("Enter Monome Prefix: ")
ip=raw_input("Enter ip: ")
sport=raw_input("Enter Monome send port: ")
rport=raw_input("Enter Monome recieve port: ")


# osc
initOSCClient('%s'%ip, int(sport))
initOSCServer('%s'%ip, int(rport))


# midi
pygame.midi.init()
pygame.midi.get_count()
midi_out = pygame.midi.Output(device_id=int(mdevice))
device_name = pygame.midi.get_device_info(int(mdevice))
print device_name



w = MTWindow(fullscreen=False, width=1024, height=768)



# The lights on Monome buttons act independently from the button press. Here we add labels that act as the monome lights
lbl=[]
lblayout= MTGridLayout(cols=8, rows=8, pos= (10, w.height/5*2-10), spacing=10)
w.add_widget(lblayout)

for i in range(64):
    lbl.append(MTLabel(style={"draw-background": True, 'bg-color':(0, 0, 0, 1)}, label=' ',  size=(w.width/24, w.width/24)))
    lblayout.add_widget(lbl[i])
    

# Here we add transparent MTButtons that sit over the labels(lights)
tbtn=[]
tblayout= MTGridLayout(cols=8, rows=8, pos= (10, w.height/5*2-10), spacing=10)
w.add_widget(tblayout)
for i in range(64):
    tbtn.append(MTButton(style={'draw-border': True, 'border-width': .5, 'border-color':(1,1,1,1), 'border-color-down':(1,1,1,1), 'bg-color':(0, 0, 0, .1), 'color':(1, 1, 1, .1), 'bg-color-down':(1, 1, 1, .1)}, size=(w.width/24, w.width/24)))
    tblayout.add_widget(tbtn[i])



def on_spress_callback(btn, *largs):
    sendOSCMsg( ('/%s/press'%prefix), [btn%8, btn/8, 1] ) #send button press to prefix/press. (btn%8, btn/8) is used to calculate the grid position from the button number
   

def on_srelease_callback(btn, *largs):
    sendOSCMsg( ('/%s/press'%prefix), [btn%8, btn/8, 0] )      
    


for i in range(64):
	tbtn[i].push_handlers(on_press = curry(on_spress_callback, i))
	tbtn[i].push_handlers(on_release = curry(on_srelease_callback, i))


# here we add the vertical midi sliders
vslider=[]
slayout= MTBoxLayout(spacing=10, pos=(20, 15))
w.add_widget(slayout)
for i in range(8):
    vslider.append(MTSlider(style={'slider-color':(1, 1, 1, 1), 'border-width': .5, 'slider-color-down':(1, 1, 1, 1),  'bg-color':(0, 0, 0, 1), 'draw-border': True, 'border-color':(1,1,1,1)}, min=0, max=127, orientation='vertical', size=(w.width/24, (w.height/3+15))))
    slayout.add_widget(vslider[i]) 


# here we add the horizontal midi sliders
hslider=[]
hlayout= MTGridLayout(spacing=10, pos=(w.width/3+100, w.height/5*2-10), cols=2, rows=8)
w.add_widget(hlayout)
for i in range(16):
    hslider.append(MTSlider(style={'slider-color':(1, 1, 1, 1), 'border-width': .5, 'slider-color-down':(1, 1, 1, 1),  'bg-color':(0, 0, 0, 1), 'draw-border': True, 'border-color':(1,1,1,1)},  min=0, max=127, orientation='horizontal', size=((w.height/3+15), w.width/24)))
    hlayout.add_widget(hslider[i])


# here we add the midi x y pads
xypad=[]
xlayout= MTBoxLayout(spacing=10, pos=(w.width/3+110, 15))
w.add_widget(xlayout)
for i in range(2):
    xypad.append(MTXYSlider(style={'slider-color':(1, 1, 1, 1), 'border-width': .5, 'slider-color-down':(1, 1, 1, 1),  'bg-color':(0, 0, 0, 1), 'draw-border': True, 'border-color':(1,1,1,1)}, size=((w.height/3+15), (w.height/3+15))))
    xlayout.add_widget(xypad[i])





# Vertical Sliders Midi Output
def on_vslider_value_change_callback(vslider, value):   
    midi_out.write_short(0xB0, int(vslider), int(value))
    
for i in range(8):
	vslider[i].push_handlers(on_value_change = curry(on_vslider_value_change_callback, i))


# Horizontal Sliders Midi Output
def on_hslider_value_change_callback(hslider, value):   
    midi_out.write_short(0xBA, int(hslider), int(value))
    
for i in range(16):
	hslider[i].push_handlers(on_value_change = curry(on_hslider_value_change_callback, i))


	



# led-handler: led on/off information from the monome
def led_handler(addr, tags, data, source):
    x=data[0]
    y=data[1]
    s=data[2]


    if s==1:
        lbl[int((x+y)+(y*7))].style['bg-color'] = (1, 1, 1, 1) 
    else:
        lbl[int((x+y)+(y*7))].style['bg-color'] = (0, 0, 0, 1)


setOSCHandler(('/%s/led'%prefix), led_handler) # adding our function





# define led column on/off handler
def led_col_handler(addr, tags, data, source):
    col=data[0]
    cv=data[1]
    colvals=(map(int, (list("".join([str((rv>> y) & 1) for y in range(7, -1, -1)])))))
    colvals.reverse()
    
    for i in range(8):
        if rowvals[i]>0:
            lbl[int(col+(8*i))].style['bg-color'] = (1, 1, 1, 1)
        else:
            lbl[int(col+(8*i))].style['bg-color'] = (0, 0, 0, 1)

    



setOSCHandler(('/%s/led_col'%prefix), led_col_handler) # adding our function



# define led row on/off handler
def led_row_handler(addr, tags, data, source):
    row=data[0]
    rv=data[1]
    rowvals=(map(int, (list("".join([str((rv>> y) & 1) for y in range(7, -1, -1)])))))
    rowvals.reverse()
    print rowvals

    for i in range(8):
        if rowvals[i]>0:
            lbl[int(row*8)+i].style['bg-color'] = (1, 1, 1, 1)
        else:
            lbl[int(row*8)+i].style['bg-color'] = (0, 0, 0, 1)

setOSCHandler(('/%s/led_row'%prefix), led_row_handler) # adding our function



# frame handler
def led_frame_handler(addr, tags, data, source):
    for i in range(8):
        rv=data[i]
        rowvals=(map(int, (list("".join([str((rv>> y) & 1) for y in range(7, -1, -1)])))))
        rowvals.reverse()
        print rowvals

        for n in range(8):
            if rowvals[n]>0:
                lbl[int(i*8)+n].style['bg-color'] = (1, 1, 1, 1)
            else:
                lbl[int(i*8)+n].style['bg-color'] = (0, 0, 0, 1)
        
setOSCHandler(('/%s/led_frame'%prefix), led_frame_handler) # adding our function



# clear handler
def led_clear_handler(addr, tags, data, source):
    x=data[0]

    if x==1:
        for i in range(64):
            lbl[i].style['bg-color'] = (1, 1, 1, 1) 
    else:
        for i in range(64):
            lbl[i].style['bg-color'] = (0, 0, 0, 1)

setOSCHandler(('/%s/clear'%prefix), led_clear_handler) # adding our function






#                                                                         -----Not Yet Implemented------
# prefix handler
def prefix_handler(addr, tags, data, source):
    pass
setOSCHandler(('/sys/prefix'), prefix_handler) # adding our function

# cable handler
def cable_handler(addr, tags, data, source):
    pass
setOSCHandler(('/sys/cable'), cable_handler) # adding our function

# offset handler
def offset_handler(addr, tags, data, source):
    pass
setOSCHandler(('/sys/offset'), offset_handler) # adding our function

# intensity handler
def intensity_handler(addr, tags, data, source):
    pass
setOSCHandler(('/sys/intensity'), intensity_handler) # adding our function

# test handler
def test_handler(addr, tags, data, source):
    pass
setOSCHandler(('/sys/test'), test_handler) # adding our function

# report handler
def report_handler(addr, tags, data, source):
    pass
setOSCHandler(('/sys/report'), report_handler) # adding our function

#                                                                         -----Not Yet Implemented------









runTouchApp()

print "Closing OSCClient"
closeOSC()
print "Done"
