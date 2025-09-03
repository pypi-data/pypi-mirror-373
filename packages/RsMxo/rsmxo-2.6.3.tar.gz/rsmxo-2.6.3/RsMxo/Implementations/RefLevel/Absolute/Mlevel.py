from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class MlevelCls:
	"""Mlevel commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mlevel", core, parent)

	def set(self, middle_level: float, refLevel=repcap.RefLevel.Default) -> None:
		"""REFLevel<*>:ABSolute:MLEVel \n
		Snippet: driver.refLevel.absolute.mlevel.set(middle_level = 1.0, refLevel = repcap.RefLevel.Default) \n
		Sets the middle reference level in absolute values. \n
			:param middle_level: No help available
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
		"""
		param = Conversions.decimal_value_to_str(middle_level)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'REFLevel{refLevel_cmd_val}:ABSolute:MLEVel {param}')

	def get(self, refLevel=repcap.RefLevel.Default) -> float:
		"""REFLevel<*>:ABSolute:MLEVel \n
		Snippet: value: float = driver.refLevel.absolute.mlevel.get(refLevel = repcap.RefLevel.Default) \n
		Sets the middle reference level in absolute values. \n
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: middle_level: No help available"""
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'REFLevel{refLevel_cmd_val}:ABSolute:MLEVel?')
		return Conversions.str_to_float(response)
