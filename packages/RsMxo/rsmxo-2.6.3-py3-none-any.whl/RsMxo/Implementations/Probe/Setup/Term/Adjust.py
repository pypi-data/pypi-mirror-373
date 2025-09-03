from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AdjustCls:
	"""Adjust commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("adjust", core, parent)

	def set(self, voltage_adj: float, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:TERM:ADJust \n
		Snippet: driver.probe.setup.term.adjust.set(voltage_adj = 1.0, probe = repcap.Probe.Default) \n
		Activates control of the termination voltage. \n
			:param voltage_adj: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.decimal_value_to_str(voltage_adj)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:TERM:ADJust {param}')

	def get(self, probe=repcap.Probe.Default) -> float:
		"""PROBe<*>:SETup:TERM:ADJust \n
		Snippet: value: float = driver.probe.setup.term.adjust.get(probe = repcap.Probe.Default) \n
		Activates control of the termination voltage. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: voltage_adj: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:TERM:ADJust?')
		return Conversions.str_to_float(response)
