
from time import time


class Radios(list):
    radios = []

    @property
    def selected_radio(self):
        if([a_radio for a_radio in self if a_radio['selected']]):
            return [a_radio for a_radio in self if a_radio['selected']][0]

    def timeout_radios(self, age):
            radios_to_timeout = [a_radio for a_radio in self if (time() - a_radio['last_seen']) > age]

            for radio in radios_to_timeout:
                timeout_radio = radio['model'] + " (" + radio['serial'] + ") at " + radio['ip'] + ":" + radio['port']
                print("RADIO TIMEOUT | " + timeout_radio)

            for radio in radios_to_timeout:
                #todo:  instead of removing, mark inactive in case they come back?
                self.remove(radio)

    def select_radio(self, radio):
        for allradios in self:
            allradios['selected'] = False

        radio_to_select = [a_radio for a_radio in self if a_radio['serial'] == radio['serial']][0]
        radio_to_select['selected'] = True
        selected_radio = radio_to_select['model'] + " (" + radio_to_select['serial'] + ") at " + radio_to_select['ip'] + ":" + radio_to_select['port']

        print("RADIO SELECTED | " + selected_radio)



class Radio(object):

    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return Radio(value) if isinstance(value, dict) else value