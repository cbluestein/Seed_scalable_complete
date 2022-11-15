from scapy.all import *
load_contrib('bgp') #scapy does not automatically load items from Contrib. Must call function and module name to load.


class MutablePacket():
    def __init__(self, pkt):
        self.pkt = pkt
        self.been_modified = False
        self.bgp_updates = []

    def is_bgp(self):
        if (str(self.summary()).find('BGPHeader') > 0):
            return True
        return False
    
    def is_bgp_update(self):
        if (self.is_bgp() and self.pkt[BGPHeader].type == 2):
            return True
        return False

    def bytes(self):
        return bytes(self.pkt)

    def remove_nlri(self, nlri, update):
        print("removing invalid nlri...")
        bgp_update = self.pkt.getlayer(scapy.contrib.bgp.BGPUpdate, update.get_layer_index())

        nlri_bytes = bytes(nlri)
        print("len of nlri: " + str(len(nlri_bytes)))
        # pkt_byte_array = bytearray(bytes(self.pkt))
        update_byte_array = bytearray(bytes(bgp_update))
        
        try: 
            # get index of nlri in the update
            index = update_byte_array.index(nlri_bytes)
            print("start index of nlri to remove: " + str(index))

            # delete the nlri from the update
            del update_byte_array[index:index+len(nlri_bytes)]

            # convert self.pkt to bytearray
            pkt_bytes = bytearray(bytes(self.pkt))
        
            # get index of update in the packet
            pkt_index = pkt_bytes.index(bytes(bgp_update))
            
            # delete the entire update from the packet
            del pkt_bytes[pkt_index:pkt_index+len(bytes(bgp_update))]

            # replace add in the modified update where the old update was
            pkt_bytes[pkt_index:pkt_index] = update_byte_array
            
            # convert the modified bytearray back to a packet
            self.pkt = IP(bytes(pkt_bytes))
            
            # update the bgp header length
            bgp_header = self.pkt.getlayer(scapy.contrib.bgp.BGPHeader, update.get_layer_index())
            bgp_header.len = bgp_header.len - len(nlri_bytes)

            # update pkt checksums, and lengths, set modified flag
            del self.pkt[IP].chksum
            del self.pkt[TCP].chksum
            self.pkt[IP].len = self.pkt[IP].len - len(nlri_bytes)
            print("modified packet: ") 
            self.pkt.show2()
            self.set_modified()
        except ValueError as v:
            print("Error. nlri not found in packet. this is weird: " + repr(v))
            print("nlri not found:")
            nlri.show()

    def is_modified(self):
        return self.been_modified

    def set_modified(self):
        self.been_modified = True

    def packet(self):
        return self.pkt

    def summary(self):
        return self.pkt.summary()

    def show(self):
        return self.pkt.show()

    def iterpayloads(self):
        return self.pkt.iterpayloads()