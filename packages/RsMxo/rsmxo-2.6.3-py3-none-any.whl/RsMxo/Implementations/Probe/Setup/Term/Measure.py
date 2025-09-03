from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MeasureCls:
	"""Measure commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("measure", core, parent)

	def get(self, probe=repcap.Probe.Default) -> float:
		"""PROBe<*>:SETup:TERM:MEASure \n
		Snippet: value: float = driver.probe.setup.term.measure.get(probe = repcap.Probe.Default) \n
		Returns the measured common mode voltage. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: voltage_meas: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:TERM:MEASure?')
		return Conversions.str_to_float(response)
