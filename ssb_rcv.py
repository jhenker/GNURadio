#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: SSB receiver
# Author: jackh
# GNU Radio version: 3.10.9.2

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq



class ssb_rcv(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "SSB receiver", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("SSB receiver")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "ssb_rcv")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.volume = volume = 0.5
        self.tuning = tuning = 17.5e3
        self.samp_rate = samp_rate = 192000
        self.reverse = reverse = (-1)
        self.decim = decim = 4
        self.carrier_freq = carrier_freq = 16000
        self.bfo = bfo = 1.5e3
        self.audio_rate = audio_rate = 48000

        ##################################################
        # Blocks
        ##################################################

        self._volume_range = qtgui.Range(0, 1, 0.05, 0.5, 200)
        self._volume_win = qtgui.RangeWidget(self._volume_range, self.set_volume, "'volume'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._volume_win)
        self._tuning_range = qtgui.Range(11e3, 21e3, 100, 17.5e3, 200)
        self._tuning_win = qtgui.RangeWidget(self._tuning_range, self.set_tuning, "Tuning", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._tuning_win)
        # Create the options list
        self._reverse_options = [-1, 1]
        # Create the labels list
        self._reverse_labels = ['Upper', 'Lower']
        # Create the combo box
        # Create the radio buttons
        self._reverse_group_box = Qt.QGroupBox("Sideband" + ": ")
        self._reverse_box = Qt.QHBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._reverse_button_group = variable_chooser_button_group()
        self._reverse_group_box.setLayout(self._reverse_box)
        for i, _label in enumerate(self._reverse_labels):
            radio_button = Qt.QRadioButton(_label)
            self._reverse_box.addWidget(radio_button)
            self._reverse_button_group.addButton(radio_button, i)
        self._reverse_callback = lambda i: Qt.QMetaObject.invokeMethod(self._reverse_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._reverse_options.index(i)))
        self._reverse_callback(self.reverse)
        self._reverse_button_group.buttonClicked[int].connect(
            lambda i: self.set_reverse(self._reverse_options[i]))
        self.top_layout.addWidget(self._reverse_group_box)
        self._bfo_range = qtgui.Range(0, 3e3, 1, 1.5e3, 200)
        self._bfo_win = qtgui.RangeWidget(self._bfo_range, self.set_bfo, "'bfo'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._bfo_win)
        self.zeromq_pull_source_0 = zeromq.pull_source(gr.sizeof_gr_complex, 1, 'tcp://192.168.2.21:10234', 100, False, (-1), False)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(decim, firdes.low_pass(1.0,samp_rate,3000,100), tuning, samp_rate)
        self.blocks_multiply_xx_1 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vff(1)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_ff(volume)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(reverse)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.audio_sink_0 = audio.sink(audio_rate, '', True)
        self.analog_sig_source_x_1 = analog.sig_source_f(audio_rate, analog.GR_COS_WAVE, bfo, 1, 0, 0)
        self.analog_sig_source_x_0 = analog.sig_source_f(audio_rate, analog.GR_SIN_WAVE, bfo, 1, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_multiply_xx_1, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.blocks_complex_to_float_0, 1), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_complex_to_float_0, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_xx_1, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.blocks_complex_to_float_0, 0))
        self.connect((self.zeromq_pull_source_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "ssb_rcv")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.blocks_multiply_const_vxx_1.set_k(self.volume)

    def get_tuning(self):
        return self.tuning

    def set_tuning(self, tuning):
        self.tuning = tuning
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(self.tuning)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.freq_xlating_fir_filter_xxx_0.set_taps(firdes.low_pass(1.0,self.samp_rate,3000,100))

    def get_reverse(self):
        return self.reverse

    def set_reverse(self, reverse):
        self.reverse = reverse
        self._reverse_callback(self.reverse)
        self.blocks_multiply_const_vxx_0.set_k(self.reverse)

    def get_decim(self):
        return self.decim

    def set_decim(self, decim):
        self.decim = decim

    def get_carrier_freq(self):
        return self.carrier_freq

    def set_carrier_freq(self, carrier_freq):
        self.carrier_freq = carrier_freq

    def get_bfo(self):
        return self.bfo

    def set_bfo(self, bfo):
        self.bfo = bfo
        self.analog_sig_source_x_0.set_frequency(self.bfo)
        self.analog_sig_source_x_1.set_frequency(self.bfo)

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.audio_rate)
        self.analog_sig_source_x_1.set_sampling_freq(self.audio_rate)




def main(top_block_cls=ssb_rcv, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
