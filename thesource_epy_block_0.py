import numpy as np
from gnuradio import gr
import pmt
class blk(gr.sync_block):
    def __init__(self, Num_Samples_To_Count =128):
        gr.sync_block.__init__(
            self,
            name='Selector Control',
            in_sig=[np.complex64],
            out_sig=[np.complex64]
        )
        self.Num_Samples_To_Count = Num_Samples_To_Count
        self.portName='messageOutput'
        self.message_port_register_out(pmt.intern(self.portName))
        self.state=True
        self.counter = 0

    def work(self, input_items, output_items):
        self.counter = self.counter + len(output_items[0])
        if(self.counter > self.Num_Samples_To_Count):
            PMT_msg = pmt.from_bool(self.state)
            self.message_port_pub(pmt.intern(self.portName), PMT_msg)
            self.state = not(self.state)
            self.counter = 0
        output_items[0][:] = input_items[0]
        return len(output_items[0])
