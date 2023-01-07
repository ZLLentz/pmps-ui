import json

from pydm import Display
from pydm.widgets import PyDMEmbeddedDisplay
from pydm.widgets.channel import PyDMChannel

from beamclass_table import install_bc_setText
from tooltips import get_tooltip_for_bc


class ArbiterOutputs(Display):

    def __init__(self, parent=None, args=None, macros=None):
        super().__init__(parent=parent, args=args, macros=macros)
        self.config = macros
        self._channels = []
        self.setup_ui()

    def setup_ui(self):
        self.setup_outputs()
        self.setup_bitmask_summaries()

    def setup_bitmask_summaries(self):
        install_bc_setText(self.ui.bc_summary_label)
        bc_channel = PyDMChannel(
            self.ui.bc_bytes.channel,
            value_slot=self.update_bc_summary,
        )
        bc_channel.connect()
        self._channels.append(bc_channel)
        rate_channel = PyDMChannel(
            self.ui.rate_bytes.channel,
            value_slot=self.update_rate_summary,
        )
        rate_channel.connect()
        self._channels.append(rate_channel)

    def update_bc_summary(self, value):
        self.ui.bc_summary_label.setText(value)
        self.ui.bc_summary_label.setToolTip(get_tooltip_for_bc(value))

    def update_rate_summary(self, value):
        if value >> 2 & 1:
            rate = 120
        elif value >> 1 & 1:
            rate = 10
        elif value & 1:
            rate = 1
        else:
            rate = 0
        self.ui.rate_summary_label.setText(f'{rate} Hz')

    def setup_outputs(self):
        ffs = self.config.get('fastfaults')
        if not ffs:
            return
        outs_container = self.ui.arbiter_outputs_content
        if outs_container is None:
            return
        count = 0
        for ff in ffs:
            prefix = ff.get('prefix')
            ffo_start = ff.get('ffo_start')
            ffo_end = ff.get('ffo_end')

            ffos_zfill = len(str(ffo_end)) + 1

            entries = range(ffo_start, ffo_end+1)

            template = 'templates/arbiter_outputs_entry.ui'
            for _ffo in entries:
                s_ffo = str(_ffo).zfill(ffos_zfill)
                macros = dict(index=count, P=prefix, FFO=s_ffo)
                widget = PyDMEmbeddedDisplay(parent=outs_container)
                widget.macros = json.dumps(macros)
                widget.filename = template
                widget.disconnectWhenHidden = False
                widget.setMinimumHeight(40)
                outs_container.layout().addWidget(widget)
                count += 1
        print(f'Added {count} arbiter outputs')

    def channels(self):
        return self._channels

    def ui_filename(self):
        return 'arbiter_outputs.ui'
