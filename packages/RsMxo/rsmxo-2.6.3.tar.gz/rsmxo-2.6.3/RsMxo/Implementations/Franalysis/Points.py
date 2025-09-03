from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PointsCls:
	"""Points commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("points", core, parent)

	def get_logarithmic(self) -> int:
		"""FRANalysis:POINts:LOGarithmic \n
		Snippet: value: int = driver.franalysis.points.get_logarithmic() \n
		Selects the number of points that are measured per decade, if method RsMxo.Franalysis.Points.mode is set to DECade. \n
			:return: pts_per_decade: No help available
		"""
		response = self._core.io.query_str('FRANalysis:POINts:LOGarithmic?')
		return Conversions.str_to_int(response)

	def set_logarithmic(self, pts_per_decade: int) -> None:
		"""FRANalysis:POINts:LOGarithmic \n
		Snippet: driver.franalysis.points.set_logarithmic(pts_per_decade = 1) \n
		Selects the number of points that are measured per decade, if method RsMxo.Franalysis.Points.mode is set to DECade. \n
			:param pts_per_decade: No help available
		"""
		param = Conversions.decimal_value_to_str(pts_per_decade)
		self._core.io.write(f'FRANalysis:POINts:LOGarithmic {param}')

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.PointsMode:
		"""FRANalysis:POINts:MODE \n
		Snippet: value: enums.PointsMode = driver.franalysis.points.get_mode() \n
		Selects, if the number of points for the FRA are measured as total or per decade. You can set the number of points with
		method RsMxo.Franalysis.Points.total/ method RsMxo.Franalysis.Points.logarithmic. \n
			:return: points_mode: No help available
		"""
		response = self._core.io.query_str('FRANalysis:POINts:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.PointsMode)

	def set_mode(self, points_mode: enums.PointsMode) -> None:
		"""FRANalysis:POINts:MODE \n
		Snippet: driver.franalysis.points.set_mode(points_mode = enums.PointsMode.DECade) \n
		Selects, if the number of points for the FRA are measured as total or per decade. You can set the number of points with
		method RsMxo.Franalysis.Points.total/ method RsMxo.Franalysis.Points.logarithmic. \n
			:param points_mode: No help available
		"""
		param = Conversions.enum_scalar_to_str(points_mode, enums.PointsMode)
		self._core.io.write(f'FRANalysis:POINts:MODE {param}')

	def get_total(self) -> int:
		"""FRANalysis:POINts:TOTal \n
		Snippet: value: int = driver.franalysis.points.get_total() \n
		Set the total number of points for the FRA analysis, if method RsMxo.Franalysis.Points.mode is set to TOTal. \n
			:return: total_points: No help available
		"""
		response = self._core.io.query_str('FRANalysis:POINts:TOTal?')
		return Conversions.str_to_int(response)

	def set_total(self, total_points: int) -> None:
		"""FRANalysis:POINts:TOTal \n
		Snippet: driver.franalysis.points.set_total(total_points = 1) \n
		Set the total number of points for the FRA analysis, if method RsMxo.Franalysis.Points.mode is set to TOTal. \n
			:param total_points: No help available
		"""
		param = Conversions.decimal_value_to_str(total_points)
		self._core.io.write(f'FRANalysis:POINts:TOTal {param}')
