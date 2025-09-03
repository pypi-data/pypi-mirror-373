from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ZadjustCls:
	"""Zadjust commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("zadjust", core, parent)

	def set(self, zero_adj_val: float, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:OFFSet:ZADJust \n
		Snippet: driver.probe.setup.offset.zadjust.set(zero_adj_val = 1.0, probe = repcap.Probe.Default) \n
		Set the waveform to zero position. It corrects the effect of a voltage offset or temperature drift. To set the value by
		the instrument, use method RsMxo.Probe.Setup.Offset.Azero.set. \n
			:param zero_adj_val: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.decimal_value_to_str(zero_adj_val)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:OFFSet:ZADJust {param}')

	def get(self, probe=repcap.Probe.Default) -> float:
		"""PROBe<*>:SETup:OFFSet:ZADJust \n
		Snippet: value: float = driver.probe.setup.offset.zadjust.get(probe = repcap.Probe.Default) \n
		Set the waveform to zero position. It corrects the effect of a voltage offset or temperature drift. To set the value by
		the instrument, use method RsMxo.Probe.Setup.Offset.Azero.set. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: zero_adj_val: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:OFFSet:ZADJust?')
		return Conversions.str_to_float(response)
