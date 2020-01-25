from keplermatik_transmitters import Transmitter, Transmitters
from skyfield.api import load


class Satellites(dict):

    @property
    def selected_satellite(self):
        if ([a_satellite for norad_cat_id, a_satellite in self.items() if a_satellite.selected]):
            return [a_satellite for norad_cat_id, a_satellite in self.items() if a_satellite.selected][0]

    def cleanup_untrackable_satellites(self):
        satellites_to_delete = []
        # todo: search TLEs directly
        skyfield_sats = load.tle('tle.txt')

        for id, satellite in self.items():
            if not id in skyfield_sats:
                satellites_to_delete.append(id)

        for satellite_to_delete in satellites_to_delete:
            for satellite in [satellite for satellite in self if satellite == satellite_to_delete]: del \
                self[int(satellite_to_delete)]

        print("CLEANED UP SATELLITES | " + str(len(self)) + " SATELLITES TRACKABLE")

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
    # hardcode properties so you can instantiate a radio without a dict
    """Comment removed"""

    def __init__(self, data):

        self.transmitters = Transmitters()

        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return Satellite(value) if isinstance(value, dict) else value

    def predict(self):

        sat = sf[self.norad_cat_id]

        ts = load.timescale()
        time = ts.now()
        # print(sat.epoch.tt)
        # hours = np.arange(0, 3, 0.01)

        # time = ts.utc(2018, 2, 7, hours)

        geocentric = sat.at(time)
        subpoint = geocentric.subpoint()

        self.latitude = subpoint.latitude
        self.longitude = subpoint.longitude
        self.altitude = int(subpoint.elevation.m)

        here = Topos('38.95171 N', '92.33407 W')
        difference = sat - here

        topocentric = difference.at(time)
        self.position = topocentric.position.km
        self.elevation, self.azimuth, self.range = topocentric.altaz()
        self.speed = topocentric.speed().km_per_s
        self.velocity = topocentric.velocity.km_per_s
        self.range_rate = (self.velocity[0] * self.position[0] + satellite.velocity[1] * satellite.position[1] +
                           satellite.velocity[2] * satellite.position[2]) / ((satellite.position[0] ** 2 +
                                                                              satellite.position[1] ** 2 +
                                                                              satellite.position[2] ** 2) ** .5)
        c = 299792458
        for uuid, transmitter in satellite.transmitters.items():
            if (transmitter.downlink_low):
                print("Downlink: " + str(transmitter.downlink_low))
                doppler_shift = transmitter.downlink_low * (satellite.range_rate * 1000 / c)
                print("Doppler Shift: " + str(doppler_shift))
                print("Shifted Frequency: " + str(transmitter.downlink_low - doppler_shift))
        if satellite.elevation.degrees > 0:
            # print('The satellite is above the horizon')
            pass

        print("Azimuth: " + str(satellites[num].azimuth.degrees))
        print("Elevation: " + str(satellites[num].elevation.degrees))
        print("Altitude " + str(satellites[num].altitude / 1000))
        print("Range " + str(satellites[num].range.km))
        print("Range Rate: " + str(satellites[num].range_rate) + "\n")

    def __repr__(self):
        return str(self.__dict__)
# for norad_cat_id, satellite in self.satellites.items():
#    print(satellite.name + " (" + str(satellite.norad_cat_id) + ")")
#    for uuid, transmitter in satellite.transmitters.items():
#        print("     " + transmitter.description)
#        if (transmitter.uplink_low):
#            print("          Uplink Low: " + str(int(transmitter.uplink_low) / 1000000) + " MHz")
#        if (transmitter.uplink_high):
#            print("          Uplink High: " + str(int(transmitter.uplink_high) / 1000000) + " MHz")
#        if(transmitter.downlink_low):
#            print("          Downlink Low: " + str(int(transmitter.downlink_low)/1000000) + " MHz")
#        if (transmitter.downlink_high):
#            print("          Downlink High: " + str(int(transmitter.downlink_high) / 1000000) + " MHz")
#    print("-")