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

	def get(self, probe=repcap.Probe.Default) -> int:
		"""PROBe<*>:SETup:LASer:STATe \n
		Snippet: value: int = driver.probe.setup.laser.state.get(probe = repcap.Probe.Default) \n
		Returns the current status of the laser. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: laser_state:
				- 1: The laser is working.
				- 2: The laser needs service, but is still working.
				- 3: Defective laser, send to your Rohde & Schwarz service center."""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:LASer:STATe?')
		return Conversions.str_to_int(response)
