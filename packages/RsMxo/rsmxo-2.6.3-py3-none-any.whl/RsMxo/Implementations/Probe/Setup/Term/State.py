from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, voltage_state: bool, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:TERM:STATe \n
		Snippet: driver.probe.setup.term.state.set(voltage_state = False, probe = repcap.Probe.Default) \n
		Activates control of the termination voltage. \n
			:param voltage_state: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.bool_to_str(voltage_state)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:TERM:STATe {param}')

	def get(self, probe=repcap.Probe.Default) -> bool:
		"""PROBe<*>:SETup:TERM:STATe \n
		Snippet: value: bool = driver.probe.setup.term.state.get(probe = repcap.Probe.Default) \n
		Activates control of the termination voltage. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: voltage_state: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:TERM:STATe?')
		return Conversions.str_to_bool(response)
