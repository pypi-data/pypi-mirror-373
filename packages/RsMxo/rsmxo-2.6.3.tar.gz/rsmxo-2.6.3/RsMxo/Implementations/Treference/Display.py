from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DisplayCls:
	"""Display commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("display", core, parent)

	def set(self, display: bool, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:DISPlay \n
		Snippet: driver.treference.display.set(display = False, timingReference = repcap.TimingReference.Default) \n
		No command help available \n
			:param display: No help available
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.bool_to_str(display)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:DISPlay {param}')

	def get(self, timingReference=repcap.TimingReference.Default) -> bool:
		"""TREFerence<*>:DISPlay \n
		Snippet: value: bool = driver.treference.display.get(timingReference = repcap.TimingReference.Default) \n
		No command help available \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: display: No help available"""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:DISPlay?')
		return Conversions.str_to_bool(response)
