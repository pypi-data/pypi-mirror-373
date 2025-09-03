from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MiddleCls:
	"""Middle commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("middle", core, parent)

	def set(self, mid_ref_lev_rel: float, refLevel=repcap.RefLevel.Default) -> None:
		"""REFLevel<*>:RELative:MIDDle \n
		Snippet: driver.refLevel.relative.middle.set(mid_ref_lev_rel = 1.0, refLevel = repcap.RefLevel.Default) \n
		Sets the middle relative reference level if method RsMxo.RefLevel.Relative.Mode.set is set to USER. \n
			:param mid_ref_lev_rel: No help available
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
		"""
		param = Conversions.decimal_value_to_str(mid_ref_lev_rel)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'REFLevel{refLevel_cmd_val}:RELative:MIDDle {param}')

	def get(self, refLevel=repcap.RefLevel.Default) -> float:
		"""REFLevel<*>:RELative:MIDDle \n
		Snippet: value: float = driver.refLevel.relative.middle.get(refLevel = repcap.RefLevel.Default) \n
		Sets the middle relative reference level if method RsMxo.RefLevel.Relative.Mode.set is set to USER. \n
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: mid_ref_lev_rel: No help available"""
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'REFLevel{refLevel_cmd_val}:RELative:MIDDle?')
		return Conversions.str_to_float(response)
