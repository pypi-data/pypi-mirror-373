from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, first: bool, refLevel=repcap.RefLevel.Default) -> None:
		"""REFLevel<*>:ENABle \n
		Snippet: driver.refLevel.enable.set(first = False, refLevel = repcap.RefLevel.Default) \n
		Enables the specified reference level. \n
			:param first: No help available
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
		"""
		param = Conversions.bool_to_str(first)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'REFLevel{refLevel_cmd_val}:ENABle {param}')

	def get(self, refLevel=repcap.RefLevel.Default) -> bool:
		"""REFLevel<*>:ENABle \n
		Snippet: value: bool = driver.refLevel.enable.get(refLevel = repcap.RefLevel.Default) \n
		Enables the specified reference level. \n
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: first: No help available"""
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'REFLevel{refLevel_cmd_val}:ENABle?')
		return Conversions.str_to_bool(response)
