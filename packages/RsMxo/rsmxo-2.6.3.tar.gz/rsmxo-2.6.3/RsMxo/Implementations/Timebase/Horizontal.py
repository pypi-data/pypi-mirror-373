from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HorizontalCls:
	"""Horizontal commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("horizontal", core, parent)

	def get_position(self) -> float:
		"""TIMebase:HORizontal:POSition \n
		Snippet: value: float = driver.timebase.horizontal.get_position() \n
		Defines the time distance between the reference point and the trigger point, which is the zero point of the diagram. The
		horizontal position is also known as trigger offset. \n
			:return: position: No help available
		"""
		response = self._core.io.query_str('TIMebase:HORizontal:POSition?')
		return Conversions.str_to_float(response)

	def set_position(self, position: float) -> None:
		"""TIMebase:HORizontal:POSition \n
		Snippet: driver.timebase.horizontal.set_position(position = 1.0) \n
		Defines the time distance between the reference point and the trigger point, which is the zero point of the diagram. The
		horizontal position is also known as trigger offset. \n
			:param position: No help available
		"""
		param = Conversions.decimal_value_to_str(position)
		self._core.io.write(f'TIMebase:HORizontal:POSition {param}')
