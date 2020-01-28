import sys
import multiprocessing as mp
import keplermatik_radios, flexradio_network, keplermatik_satellites


def init():

    print("Keplermatik!")
    print("")

    radios = keplermatik_radios.Radios()
    satellites = keplermatik_satellites.Satellites()

    print("PREDICTING SATELLITES | " + str(len(satellites)) + " SATELLITES")
    satellites.predict_all()


def main():
    pass


if __name__ == '__main__':
    mp.freeze_support()
    init()
