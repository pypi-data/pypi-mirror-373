from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.Utilities import trim_str_response
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TypePyCls:
	"""TypePy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("typePy", core, parent)

	def get(self, probe=repcap.Probe.Default) -> str:
		"""PROBe<*>:SETup:TYPE \n
		Snippet: value: str = driver.probe.setup.typePy.get(probe = repcap.Probe.Default) \n
		Queries the class of the probe. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: type_py: String containing the probe class, e.g. None (no probe detected) , passive, current, active diff., active single-ended."""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:TYPE?')
		return trim_str_response(response)
