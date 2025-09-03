from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StateCls:
	"""State commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("state", core, parent)

	def get(self, timingReference=repcap.TimingReference.Default) -> bool:
		"""TREFerence<*>:STATe \n
		Snippet: value: bool = driver.treference.state.get(timingReference = repcap.TimingReference.Default) \n
		No command help available \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: state: No help available"""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:STATe?')
		return Conversions.str_to_bool(response)
