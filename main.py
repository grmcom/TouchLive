'''
TouchLive !
===============

<Put the description here ^^>

'''

import kivy
kivy.require('1.0.7')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty
from simpleOSC import initOSCClient, initOSCServer, closeOSC, \
        setOSCHandler, sendOSCMsg
import pygame.midi


class TouchLiveSlider(Slider):
    '''Custom slider class for having his index and custom graphics defined in
    the .kv
    '''
    index = NumericProperty(0)


class TouchLiveButton(Button):
    '''Custom button class for having his index and custom graphics defined in
    the .kv + highligh state that draw an hover when activated.
    '''
    highlight = BooleanProperty(False)
    index = NumericProperty(0)


class TouchLiveMain(FloatLayout):
    '''Main panel containing all the buttons and sliders.
    The layout is done in the .kv, and assign each part of the UI to grid,
    grid_right, grid_bottom, grid_xy.
    '''

    app = ObjectProperty(None)
    grid = ObjectProperty(None)
    grid_right = ObjectProperty(None)
    grid_bottom = ObjectProperty(None)
    grid_xy = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(TouchLiveMain, self).__init__(**kwargs)

        # create and bind every slider and buttons
        for x in xrange(64):
            btn = TouchLiveButton(index=x)
            btn.bind(state=self.on_button_state)
            self.grid.add_widget(btn)

        for x in xrange(16):
            slider = TouchLiveSlider(index=x, min=0, max=127)
            slider.bind(value=self.on_right_slider_value)
            self.grid_right.add_widget(slider)

        for x in xrange(8):
            slider = TouchLiveSlider(index=x, min=0, max=127,
                                        orientation='vertical')
            slider.bind(value=self.on_bottom_slider_value)
            self.grid_bottom.add_widget(slider)

        # led handler for monome
        prefix = self.app.config.get('monome', 'prefix')
        setOSCHandler('/%s/led' % prefix, self.on_led)
        setOSCHandler('/%s/led_col' % prefix, self.on_led_col)
        setOSCHandler('/%s/led_row' % prefix, self.on_led_row)
        setOSCHandler('/%s/led_frame' % prefix, self.on_led_frame)
        setOSCHandler('/%s/led_clear' % prefix, self.on_led_clear)

        # empty handlers
        setOSCHandler('/sys/prefix', self.empty_handler)
        setOSCHandler('/sys/cable', self.empty_handler)
        setOSCHandler('/sys/offset', self.empty_handler)
        setOSCHandler('/sys/intensity', self.empty_handler)
        setOSCHandler('/sys/test', self.empty_handler)
        setOSCHandler('/sys/report', self.empty_handler)

    def on_button_state(self, instance, value):
        prefix = self.app.config.get('monome', 'prefix')
        index = instance.index
        value = 1 if value == 'down' else 0
        sendOSCMsg('/%s/press' % prefix, [index % 8, index / 8, value])

    def on_bottom_slider_value(self, instance, value):
        midi_out = self.app.midi_out
        midi_out.write_short(0xb0, instance.index, int(value))

    def on_right_slider_value(self, instance, value):
        midi_out = self.app.midi_out
        midi_out.write_short(0xba, instance.index, int(value))

    def on_led(self, addr, tags, data, source):
        x, y, s =data[0:3]
        index = 63-int((x + y) + (y * 7))
        print index
        self.grid.children[index].highlight = bool(s)

    def on_led_col(self, addr, tags, data, source):
        col, cv = data[0:2]
        colvals = map(int, (list(''.join([str((cv>> y) & 1) for y in xrange(7, -1, -1)]))))
        colvals.reverse()
        for i in xrange(8):
            index = int(col + (8 * i))
            self.grid.children[index].highlight = (colvals[i] > 0)

    def on_led_row(self, addr, tags, data, source):
        row, rv = data[0:2]
        rowvals = map(int, (list(''.join([str((rv>> y) & 1) for y in xrange(7, -1, -1)]))))
        rowvals.reverse()
        for i in xrange(8):
            index = int(row) * 8 + i
            self.grid.children[index].highlight = (rowvals[i] > 0)

    def on_led_frame(self, addr, tags, data, source):
        for i in xrange(8):
            rv = data[i]
            rowvals = (map(int, (list("".join([str((rv>> y) & 1) for y in range(7, -1, -1)])))))
            rowvals.reverse()
            for n in xrange(8):
                index = i * 8 + n
                self.grid.children[index].highlight = rowvals[n] > 0

    def on_led_clear(self, addr, tags, data, source):
        x = data[0]
        for i in xrange(64):
            self.grid.children[i] = (x == 1)

    def empty_handler(self, *largs):
        pass


class TouchLiveConnect(FloatLayout):
    '''Tiny startup panel to connect or configure the app
    '''
    app = ObjectProperty(None)


class TouchLiveApp(App):
    '''Our application !
    '''

    def build(self):
        return TouchLiveConnect(app=self)

    def build_config(self, config):
        config.add_section('midi')
        config.set('midi', 'device', '0')
        config.add_section('monome')
        config.set('monome', 'prefix', '')
        config.set('monome', 'receive_port', '9001')
        config.set('monome', 'send_port', '9000')
        config.add_section('network')
        config.set('network', 'host', '127.0.0.1')

    def build_settings(self, settings):
        data = '''[
            { "type": "title", "title": "Midi configuration" },
            { "type": "numeric", "title": "Device",
              "desc": "Midi device number",
              "section": "midi", "key": "device" },

            { "type": "title", "title": "Monome configuration" },
            { "type": "string", "title": "Prefix",
              "desc": "Monome prefix to use",
              "section": "monome", "key": "prefix" },
            { "type": "numeric", "title": "Send port",
              "desc": "Monome send port to use, from 1024 to 65535",
              "section": "monome", "key": "send_port" },
            { "type": "numeric", "title": "Receive port",
              "desc": "Monome receive port to use, from 1024 to 65535",
              "section": "monome", "key": "receive_port" },

            { "type": "title", "title": "Network configuration" },
            { "type": "string", "title": "Host",
              "desc": "Host or ip address to use",
              "section": "network", "key": "host" }
        ]'''
        settings.add_json_panel('Touch Live', self.config, data=data)

    def on_stop(self):
        closeOSC()

    def do_connect(self):
        config = self.config
        host = config.get('network', 'host')
        sport = config.getint('monome', 'send_port')
        rport = config.getint('monome', 'receive_port')
        mdevice = config.getint('midi', 'device')
        # osc
        initOSCClient(host, sport)
        initOSCServer(host, rport)
        # midi
        pygame.midi.init()
        pygame.midi.get_count()
        self.midi_out = pygame.midi.Output(device_id=mdevice)
        self.device_name = pygame.midi.get_device_info(mdevice)

        # switch to main screen
        parent = self.root.parent
        parent.remove_widget(self.root)
        self.root = TouchLiveMain(app=self)
        parent.add_widget(self.root)


if __name__ in ('__main__', '__android__'):
    try:
        TouchLiveApp().run()
    finally:
        closeOSC()
