import requests, re, os, pickle
from requests_toolbelt.threaded import pool
from skyfield.api import load
import keplermatik_satellites
import keplermatik_transmitters

class SatnogsClient:

    def __init__(self, satellites):
        self.satellites = satellites
        self.transmitters = keplermatik_transmitters.Transmitters()

    def get_satellites(self):
        satellites_url = 'https://db.satnogs.org/api/satellites/'
        print("GETTING SATELLITES | " + satellites_url)
        payload = {'status': 'alive'}
        try:
            r = requests.get(satellites_url, params=payload)
            outfile = open('satnogs_satellites', 'wb')
            pickle.dump(r, outfile)
            outfile.close()
        except:
            print("NETWORK ERROR | USING CACHED SATNOGS SATELLITES")
            infile = open('satnogs_satellites', 'rb')
            r = pickle.load(infile)
            infile.close()


        for satellite in r.json():

            #todo: if this key isn't in the dict it won't wind up in the object, move to init
            satellite['selected'] = False
            if(satellite['norad_cat_id'] != 99999):
                self.satellites.update({satellite['norad_cat_id']:keplermatik_satellites.Satellite(satellite)})

#todo: handle network errors

        transmitters_url = 'https://db.satnogs.org/api/transmitters/'
        print("GETTING TRANSMITTERS | " + transmitters_url)

        payload = {'status': 'active'}

        try:
            t = requests.get('https://db.satnogs.org/api/transmitters/', params=payload)
            outfile = open('satnogs_transmitters', 'wb')
            pickle.dump(t, outfile)
            outfile.close()
        except:
            print("NETWORK ERROR | USING CACHED SATNOGS TRANSMITTERS")
            infile = open('satnogs_transmitters', 'rb')
            t = pickle.load(infile)
            infile.close()

        for transmitter in t.json():
            self.transmitters.update({transmitter['uuid']:keplermatik_transmitters.Transmitter(transmitter)})

        for uuid, transmitter in self.transmitters.items():
            if transmitter.norad_cat_id in self.satellites:
                satellite = self.satellites[transmitter.norad_cat_id]
                satellite.transmitters.update({uuid:transmitter})

        del self.transmitters

        #todo: select first satellite

        self.update_tles()

        #self.satellites.cleanup_untrackable_satellites()


    def update_tles(self):
    #todo: so much to organize, maybe create different functions
        tle_text = ""
        tle_not_found_count = 0
        manual_tle_count = 0
        celestrack_urls = []
        manual_tle_urls = []

        #if os.path.exists("tle.txt"):
        #    os.remove("tle.txt")

        print("UPDATING TLEs | " + str(len(self.satellites)) + " SATELLITES IN SATNOGS")

        celestrack_files = ['satnogs.txt', 'active.txt', 'tle-new.txt']

        print("DOWNLOADING CELESTRAK TLEs | " + ', '.join(celestrack_files).upper())

        for filename in celestrack_files:
            celestrack_urls.append('https://celestrak.com/NORAD/elements/' + filename)

        p = pool.Pool.from_urls(celestrack_urls)
        p.join_all()

        for response in p.responses():
            tle_text += response.text


        if(len(tle_text) != 0):

            with open('celestrack_tle.txt', 'wb') as file:
                file.write(bytes(tle_text, "UTF-8"))

            print("CELESTRACK TLEs LOADED")

        else:
            print("NETWORK ERROR | USING CACHED CELESTRACK TLES")
            with open('celestrack_tle.txt', 'r') as file:
                tle_text = file.read()

        #print("TLES: " + tle_text)
        del (p)

        for id, satellite in self.satellites.items():

            if not satellite.tle_exists("celestrack_tle.txt"):
                tle_not_found_count += 1
                manual_tle_urls.append('https://db.satnogs.org/satellite/' + str(satellite.norad_cat_id) + "/")

        print("FOUND MISSING TLEs | " + str(tle_not_found_count) + " TLEs NOT FOUND")

        p = pool.Pool.from_urls(manual_tle_urls)
        p.join_all()
        manual_tles = ""
        for response in p.responses():
            norad_cat_id = int(re.findall("https://db.satnogs.org/satellite/(.*)/", response.url)[0])

            tle_name = re.findall("data-name=\"(.*)\"", response.text)[0]
            tle_line1 = re.findall("data-tle1=\"(.*)\"", response.text)[0]
            tle_line2 = re.findall("data-tle2=\"(.*)\"", response.text)[0]

            if (tle_line1[2:7] == str(norad_cat_id).zfill(5)):
                manual_tle_count += 1
                manual_tles += tle_name + "\r\n" + tle_line1 + "\r\n" + tle_line2 + "\r\n"

        for exc in p.exceptions():
            pass
            #print('GET {}. Raised {}.'.format(exc.request_kwargs['url'],
            #                                 exc.message))

        if (len(manual_tles) != 0):
            with open('satnogs_tle.txt', 'wb') as file:
                file.write(bytes("\n", "UTF-8"))
                file.write(bytes(manual_tles, "UTF-8"))
                print('DOWNLOADED SATNOG TLEs | ' + str(manual_tle_count) + " MANUAL TLEs ADDED")

        else:
            #todo: look for them in the celestrak TLEs just in case
            manual_tle_count = 0
            for id, satellite in self.satellites.items():
                if satellite.tle_exists("satnogs_tle.txt"):
                    manual_tle_count += 1

            print('NETWORK ERROR | ' + str(manual_tle_count) + " MANUAL TLEs ADDED FROM SATNOGS TLE CACHE")

        with open('tle.txt', 'wb') as file:
            file.write(bytes(tle_text, "UTF-8"))
            #todo fix \n between the files
            with open('satnogs_tle.txt', 'r') as file2:
                manual_tles = file2.read()
                file.write(bytes(manual_tles, "UTF-8"))

        print('REMOVING UNTRACKABLE SATELLITES | ' + str(tle_not_found_count - manual_tle_count) + " SATELLITES NOT TRACKABLE")

        self.satellites.cleanup_untrackable_satellites()





