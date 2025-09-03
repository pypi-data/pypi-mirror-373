from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	# noinspection PyTypeChecker
	def get(self, probe=repcap.Probe.Default) -> enums.Detection:
		"""PROBe<*>:SETup:STATe \n
		Snippet: value: enums.Detection = driver.probe.setup.state.get(probe = repcap.Probe.Default) \n
		Queries if the probe at the specified input channel is active (detected) or not active (not detected) . To switch the
		probe on, use method RsMxo.Channel.State.set. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: state: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:STATe?')
		return Conversions.str_to_scalar_enum(response, enums.Detection)
