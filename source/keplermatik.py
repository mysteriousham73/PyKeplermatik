import sys
import multiprocessing as mp
import keplermatik_radios, flexradio_network, keplermatik_satellites, satnogs_network, pickle
from time import gmtime, time, sleep
import os
import pickle
#import timeit
#os.environ["KIVY_NO_CONSOLELOG"] = "1"



# fix for pyinstaller packages app to avoid ReactorAlreadyInstalledError
if 'twisted.internet.reactor' in sys.modules:
    del sys.modules['twisted.internet.reactor']

#from kivy.support import install_twisted_reactor
#install_twisted_reactor()

from twisted.internet import reactor

def init():

    print("Keplermatik!")
    print("")

    radios = keplermatik_radios.Radios()
    #satellites = keplermatik_satellites.Satellites()
    #satnogs = satnogs_network.SatnogsClient(satellites)
    #satnogs.get_satellites()
    #satellites.cleanup_untrackable_satellites()
    #filename = 'satellite_data'
    #outfile = open(filename, 'wb')
    #pickle.dump(satellites, outfile)
    #outfile.close()
    infile = open('satellite_data', 'rb')
    satellites = pickle.load(infile)
    infile.close()
    print("LOADING TLEs | " + str(len(satellites)) + " SATELLITES")
    infile = open('satellites_with_tles', 'rb')
    satellites = pickle.load(infile)
    infile.close()

#    for norad_cat_id, satellite in satellites.items():
    #    print("LOADING TLE | " + satellite.name)
#        satellite.load_tle()
    print("TLES LOADED")
    #outfile = open('satellites_with_tles', 'wb')
    #pickle.dump(satellites, outfile)
    #outfile.close()
    infile = open('satellites_with_tles', 'rb')
    satellites = pickle.load(infile)
    infile.close()


    print("PREDICTING SATELLITES | " + str(len(satellites)) + " SATELLITES")
    start_time = time()
    timing = predict_satellites_mp(satellites)
    print("PREDICTIONS COMPLETE | " + str(len(satellites)) + " SATELLITES IN " + str(round(time() - start_time, 3)) + " SECONDS")
    print("PREDICTION RUN | QUEUE LOAD " + str(timing['queue_load']) + " PREDICT " + str(timing['prediction']) + " (" + str(round(timing['prediction'] / len(satellites), 3)) + "/SAT) " + "QUEUE UNLOAD " + str(timing['queue_unload']))
    print(satellites[7530])

class Predictor(mp.Process):

    def __init__(self, name, in_queue, out_queue):
        super(Predictor, self).__init__()
        self.name = name
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            satellite = self.in_queue.get()

            try:
                satellite.predict_gmtime(gmtime())
                self.out_queue.put(satellite)
            finally:
                self.in_queue.task_done()

def main():
    pass


def predict_satellites_mp(satellites):
    in_queue = mp.JoinableQueue()
    out_queue = mp.Queue()

    workers = [Predictor(str(worker_name), in_queue, out_queue) for worker_name in range(4)]
    timing = {}

    for worker in workers:
        worker.daemon = True
        worker.start()

    work_len = 0

    start_time = time()
    for norad_cat_id, satellite in satellites.items():
        in_queue.put((satellite))
        work_len += 1

    timing['queue_load'] = round(time() - start_time, 3)
    start_time = time()
    in_queue.join()
    timing['prediction'] = round(time() - start_time, 3)
   # while out_queue.qsize() != work_len:
   #     # waiting for workers to finish
   #     print("Waiting for workers. Out queue size {}".format(out_queue.qsize()))
   #     sleep(0.1)

    start_time = time()
    while not out_queue.empty():
        satellite = out_queue.get()
        satellites[satellite.norad_cat_id] = satellite

    timing['queue_unload'] = round(time() - start_time, 3)

    return timing

#    print("Azimuth: " + str(s.azimuth.degrees))
#    print("Elevation: " + str(s.elevation.degrees))
#    print("Altitude " + str(s.altitude / 1000))
#    print("Range " + str(s.range.km))
#    print("Range Rate: " + str(s.range_rate) + "\n")

#    print("Uplink: " + str(t.uplink_frequency))
#    print("Downlink: " + str(t.downlink_frequency))
#    print("Uplink Shifted: " + str(t.uplink_frequency.shifted))
#    print("Downlink Shifted: " + str(t.downlink_frequency.shifted))
#    print("Uplink Shifted: " + str(t.uplink_frequency.shifted))
#    print("Downlink Shifted: " + str(t.downlink_frequency.shifted))
#    print("Doppler / Hz: " + str(s.doppler_per_hz))



    #todo: threadify

    #while(True):
    #    pass

 #   from kivy.app import App
 #   from kivy.uix.button import Button

  #  class TestApp(App):
  #      def build(self):
  #          return Button(text='Hello World')

    #TestApp().run()
    #app = wx.App(False)
    #todo:  implement config, maybe a more generic lib than wx
    #todo:  sub xvtr all, pan all, slice all

    #config = wx.Config("flexdoppler")
#    selected_radio_serial = config.Read("selected_radio_serial")
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
    #freeze_support()
    init()
