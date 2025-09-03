from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PointCls:
	"""Point commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("point", core, parent)

	def get_display(self) -> bool:
		"""FRANalysis:MEASurement:POINt[:DISPlay] \n
		Snippet: value: bool = driver.franalysis.measurement.point.get_display() \n
		Enables the display of the measurement points for the frequency response analysis. \n
			:return: points: No help available
		"""
		response = self._core.io.query_str('FRANalysis:MEASurement:POINt:DISPlay?')
		return Conversions.str_to_bool(response)

	def set_display(self, points: bool) -> None:
		"""FRANalysis:MEASurement:POINt[:DISPlay] \n
		Snippet: driver.franalysis.measurement.point.set_display(points = False) \n
		Enables the display of the measurement points for the frequency response analysis. \n
			:param points: No help available
		"""
		param = Conversions.bool_to_str(points)
		self._core.io.write(f'FRANalysis:MEASurement:POINt:DISPlay {param}')
