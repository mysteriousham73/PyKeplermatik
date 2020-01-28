from twisted.internet.protocol import DatagramProtocol
import re
from time import time
from keplermatik_radios import Radio
from twisted.internet import protocol

class RadioDiscovery(DatagramProtocol):

    def __init__(self, radios):
        self.radios = radios

    def datagramReceived(self, datagram, address):
        if (str(datagram).find("discovery_protocol_version") != -1):
            self.process_message(str(datagram))

    def process_message(self, message):

        radio_config_list = re.findall(r'(\S*)=(\S*)', str(message))
        radio_config_list.pop(0)
        radio_config = dict(radio_config_list)
        radio_config['selected'] = False
        radio_config['last_seen'] = time()

        #todo:  this is part of conversion to radio object from dict
        new_radio = Radio(radio_config)

        seen_radio = [element for element in self.radios if element['serial'] == radio_config['serial']]

        if not (seen_radio):
            self.radios.append(radio_config)

            found_radio = radio_config['model'] + " (" + radio_config['serial'] + ") at " + radio_config['ip'] + ":" + \
                          radio_config['port']
            print("FOUND RADIO | " + found_radio)
            # wx.adv.NotificationMessage("Found Radio", found_radio).Show()

        else:
            if seen_radio[0]['ip'] != radio_config['ip']:
                print("CHANGED IP | " + radio_config['model'] + " (" + radio_config['serial'] + ") changed IP to " +
                      radio_config['ip'])
                seen_radio[0]['ip'] = radio_config['ip']

            if seen_radio[0]['port'] != radio_config['port']:
                print("CHANGED PORT | " + radio_config['model'] + " (" + radio_config['serial'] + ") changed port to " +
                      radio_config['port'])
                seen_radio[0]['port'] = radio_config['port']

            seen_radio[0]['last_seen'] = radio_config['last_seen']


class FlexClient(protocol.Protocol):

    def connectionMade(self):
        self.transport.write(self.factory.message)

    def dataReceived(self, data):
        print("Server said:", data)
        self.transport.loseConnection()

    def connectionLost(self, reason):
        print("connection lost")


class FlexClientFactory(protocol.ClientFactory):
    protocol = FlexClient

    def __init__(self, message):
        self.message = message

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
        #reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!")
        #reactor.stop()





