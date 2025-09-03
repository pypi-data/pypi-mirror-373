from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.Utilities import trim_str_response
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PrDateCls:
	"""PrDate commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("prDate", core, parent)

	def get(self, probe=repcap.Probe.Default) -> str:
		"""PROBe<*>:ID:PRDate \n
		Snippet: value: str = driver.probe.id.prDate.get(probe = repcap.Probe.Default) \n
		Queries the production date of the probe. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: production_date: Date in a string."""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:ID:PRDate?')
		return trim_str_response(response)
