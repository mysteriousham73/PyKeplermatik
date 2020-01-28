from keplermatik_transmitters import Transmitters
from keplermatik_predictor import Predictor
import satnogs_network
from skyfield.api import Topos, EarthSatellite, load
from time import time
import re, numpy as np


class Satellites(dict):

    def __init__(self):
        super(Satellites, self).__init__()
        self.predictor = Predictor(self)

        satnogs = satnogs_network.SatnogsClient(self)
        satnogs.get_satellites()
        print("LOADING TLEs | " + str(len(self)) + " SATELLITES")
        for norad_cat_id, satellite in self.items():
            # print("LOADING TLE | " + satellite.name)
            satellite.load_tle()
        print("TLES LOADED")

    def predict_all(self):
        start_time = time()

        timing = self.predictor.predict()

        print("PREDICTIONS COMPLETE | " + str(len(self)) + " SATELLITES IN " + str(round(time() - start_time, 3)) + " SECONDS")
        print("PREDICTION RUN | QUEUE LOAD " + str(timing['queue_load']) + " PREDICT " + str(timing['prediction']) + " (" + str(round(timing['prediction'] / len(self), 3)) + "/SAT) " + "QUEUE UNLOAD " + str(timing['queue_unload']))

    @property
    def selected_satellite(self):
        if([a_satellite for norad_cat_id, a_satellite in self.items() if a_satellite.selected]):
            return [a_satellite for norad_cat_id, a_satellite in self.items() if a_satellite.selected][0]

    def cleanup_untrackable_satellites(self):
        satellites_to_delete = []

        for id, satellite in self.items():
            satellite.load_tle()
            if not satellite.tle.exists:
                satellites_to_delete.append(id)

        for satellite_to_delete in satellites_to_delete:
            for satellite in [satellite for satellite in self if satellite == satellite_to_delete]: del(self[int(satellite_to_delete)])

        print("CLEANED UP " + str(len(satellites_to_delete)) + " SATELLITES | " + str(len(self)) + " SATELLITES TRACKABLE")

    def select_satellite_by_norad_cat_id(self, id):
        for norad_cat_id, allsatellites in self.items():
            allsatellites.selected = False

        satellite_to_select = self[id]
        satellite_to_select.selected = True
        selected_satellite_text = satellite_to_select.name + " (" + str(satellite_to_select.norad_cat_id) + ")"

        print("SATELLITE SELECTED | " + selected_satellite_text)

    def select_satellite(self, satellite):
        for norad_cat_id, allsatellites in self.items():
            allsatellites.selected = False

        satellite_to_select = self[satellite.norad_cat_id]
        satellite_to_select.selected = True
        selected_satellite_text = satellite_to_select.name + " (" + str(satellite_to_select.norad_cat_id) + ")"

        print("SATELLITE SELECTED | " + selected_satellite_text)


class Satellite(object):

    def __init__(self, data):
        self.range_rate = 0
        self.transmitters = Transmitters()
        self.norad_cat_id = 0
        self.current_time_resolution = 1
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

        self.tle = TLE(self.norad_cat_id)

    def load_tle(self):
        self.tle.load_tle("tle.txt")

    def tle_exists(self, filename):
        self.tle.load_tle(filename)
        return self.tle.exists


    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return Satellite(value) if isinstance(value, dict) else value

    @property
    def doppler_per_hz(self):
        c = 299792.458
        return -(self.range_rate / c)

    def predict_now(self):
        ts = load.timescale()
        timescale = ts.now()
        # print(sat.epoch.tt)
        self.predict(timescale)

    def predict_gmtime(self, this_gmtime):
        ts = load.timescale()
        #utc(self, year, month=1, day=1, hour=0, minute=0, second=0.0):
        hours = np.arange(0, 23, 1/60)
        #minutes = np.arange(0, 2, (1))
        #tscale = ts.utc(this_gmtime[0], this_gmtime[1], this_gmtime[2], this_gmtime[3], this_gmtime[4], this_gmtime[5])
        tscale = ts.utc(2019, 1, 27, hours)
        return self.predict(tscale)

    def predict_range(self, start_time, finish_time, step):
        pass

    def predict(self, tscale):
        sat = EarthSatellite(self.tle.tle_lines[1], self.tle.tle_lines[2], self.name)

        geocentric = sat.at(tscale)
        subpoint = geocentric.subpoint()

        self.latitude = subpoint.latitude
        self.longitude = subpoint.longitude
        self.altitude = subpoint.elevation.m

        here = Topos('38.95171 N', '92.33407 W')
        difference = sat - here

        topocentric = difference.at(tscale)
        self.position = topocentric.position.km
        self.elevation, self.azimuth, self.range = topocentric.altaz()
        self.speed = topocentric.speed().km_per_s
        self.velocity = topocentric.velocity.km_per_s
        self.range_rate = (self.velocity[0] * self.position[0] + self.velocity[1] * self.position[1] + self.velocity[2] * self.position[2])/((self.position[0] ** 2 + self.position[1] ** 2 + self.position[2] ** 2) ** .5)

        for uuid, transmitter in self.transmitters.items():
            transmitter.range_rate = self.range_rate

        #if self.elevation.degrees > 0:
        #   # print('The satellite is above the horizon')
        #    pass

    def __repr__(self):
        return str(self.__dict__)


class TLE:

    def __init__(self, norad_cat_id):
        self.exists = False
        self.tle_text = ""
        self.tle_lines = []
        self.norad_cat_id = norad_cat_id
        self.filename = ""


    def load_tle(self, filename):
        with open(filename, 'r') as file:
            tle_file_contents = file.read()
            re_string = "\n(.*\n1.*" + str(self.norad_cat_id) + "[UCS].*\n.*)"
            self.tle_text = re.findall(re_string, tle_file_contents)

            if(self.tle_text):
                self.tle_lines = self.tle_text[0].split("\n")
                self.exists = True
            else:
                #print("TLE NOT FOUND | NORAD CAT ID " + str(norad_cat_id))
                self.exists = False


