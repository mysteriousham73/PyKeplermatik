import sys
import keplermatik_radios, flexradio_network, keplermatik_satellites, satnogs_network, pickle
from time import gmtime
import os
os.environ["KIVY_NO_CONSOLELOG"] = "1"



# fix for pyinstaller packages app to avoid ReactorAlreadyInstalledError
if 'twisted.internet.reactor' in sys.modules:
    del sys.modules['twisted.internet.reactor']

from kivy.support import install_twisted_reactor
install_twisted_reactor()

from twisted.internet import reactor

def main():

    print("Keplermatik!")
    print("")

    radios = keplermatik_radios.Radios()
    satellites = keplermatik_satellites.Satellites()
    satnogs = satnogs_network.SatnogsClient(satellites)
    satnogs.get_satellites()
    satellites.cleanup_untrackable_satellites()

    s = satellites[7530]
    s.load_tle()

    t = s.transmitters["uLfAhJaZJUWmA9Sik8yQ2m"]
    #print(satellites[7530].transmitters)

    s.predict_gmtime(gmtime())

    print("Azimuth: " + str(s.azimuth.degrees))
    print("Elevation: " + str(s.elevation.degrees))
    print("Altitude " + str(s.altitude / 1000))
    print("Range " + str(s.range.km))
    print("Range Rate: " + str(s.range_rate) + "\n")

    print("Uplink: " + str(t.uplink_frequency))
    print("Downlink: " + str(t.downlink_frequency))
    print("Uplink Shifted: " + str(t.uplink_frequency.shifted))
    print("Downlink Shifted: " + str(t.downlink_frequency.shifted))
    print("Uplink Shifted: " + str(t.uplink_frequency.shifted))
    print("Downlink Shifted: " + str(t.downlink_frequency.shifted))
    print("Doppler / Hz: " + str(s.doppler_per_hz))



    #todo: threadify

    #while(True):
    #    pass

    from kivy.app import App
    from kivy.uix.button import Button

    class TestApp(App):
        def build(self):
            return Button(text='Hello World')

    #TestApp().run()
    #app = wx.App(False)
    #todo:  implement config, maybe a more generic lib than wx
    #todo:  sub xvtr all, pan all, slice all

    #config = wx.Config("flexdoppler")
    selected_radio_serial = config.Read("selected_radio_serial")
    #app.SetAppDisplayName("FlexDoppler")
    #app.SetAppName("FlexDoppler")
    #FDTrayIcon(radios)

    #app.SetClassName("FlexDoppler")
    #app.SetVendorDisplayName("FlexDoppler")
    #app.SetVendorName("FlexDoppler")

    #listener = reactor.listenMulticast(4992, flexradio_network.RadioDiscovery(radios),
    #                                   listenMultiple=True)


    #reactor.registerWxApp(app)

    #reactor.run()



if __name__ == '__main__':
    main()
