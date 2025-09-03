from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UlevelCls:
	"""Ulevel commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ulevel", core, parent)

	def set(self, upper_level: float, refLevel=repcap.RefLevel.Default) -> None:
		"""REFLevel<*>:ABSolute:ULEVel \n
		Snippet: driver.refLevel.absolute.ulevel.set(upper_level = 1.0, refLevel = repcap.RefLevel.Default) \n
		Sets the upper reference level in absolute values. This is required to determine a rise. \n
			:param upper_level: No help available
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
		"""
		param = Conversions.decimal_value_to_str(upper_level)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'REFLevel{refLevel_cmd_val}:ABSolute:ULEVel {param}')

	def get(self, refLevel=repcap.RefLevel.Default) -> float:
		"""REFLevel<*>:ABSolute:ULEVel \n
		Snippet: value: float = driver.refLevel.absolute.ulevel.get(refLevel = repcap.RefLevel.Default) \n
		Sets the upper reference level in absolute values. This is required to determine a rise. \n
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: upper_level: No help available"""
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'REFLevel{refLevel_cmd_val}:ABSolute:ULEVel?')
		return Conversions.str_to_float(response)
