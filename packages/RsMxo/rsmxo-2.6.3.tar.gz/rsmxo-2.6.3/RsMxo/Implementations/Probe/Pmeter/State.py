from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def set(self, state: bool, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:PMETer:STATe \n
		Snippet: driver.probe.pmeter.state.set(state = False, probe = repcap.Probe.Default) \n
		Activates the integrated R&S ProbeMeter on probes with Rohde & Schwarz probe interface. \n
			:param state: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.bool_to_str(state)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:PMETer:STATe {param}')

	def get(self, probe=repcap.Probe.Default) -> bool:
		"""PROBe<*>:PMETer:STATe \n
		Snippet: value: bool = driver.probe.pmeter.state.get(probe = repcap.Probe.Default) \n
		Activates the integrated R&S ProbeMeter on probes with Rohde & Schwarz probe interface. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: state: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:PMETer:STATe?')
		return Conversions.str_to_bool(response)
