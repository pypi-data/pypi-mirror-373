from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DiagramCls:
	"""Diagram commands group definition. 7 total commands, 0 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("diagram", core, parent)

	def get_crosshair(self) -> bool:
		"""DISPlay:DIAGram:CROSshair \n
		Snippet: value: bool = driver.display.diagram.get_crosshair() \n
		If selected, a crosshair is displayed in the diagram area. A crosshair allows you to select a specific data point by its
		coordinates. \n
			:return: crosshair: No help available
		"""
		response = self._core.io.query_str('DISPlay:DIAGram:CROSshair?')
		return Conversions.str_to_bool(response)

	def set_crosshair(self, crosshair: bool) -> None:
		"""DISPlay:DIAGram:CROSshair \n
		Snippet: driver.display.diagram.set_crosshair(crosshair = False) \n
		If selected, a crosshair is displayed in the diagram area. A crosshair allows you to select a specific data point by its
		coordinates. \n
			:param crosshair: No help available
		"""
		param = Conversions.bool_to_str(crosshair)
		self._core.io.write(f'DISPlay:DIAGram:CROSshair {param}')

	def get_grid(self) -> bool:
		"""DISPlay:DIAGram:GRID \n
		Snippet: value: bool = driver.display.diagram.get_grid() \n
		If selected, a grid is displayed in the diagram area. A grid helps you associate a specific data point to its exact value
		on the x- or y-axis. \n
			:return: show: No help available
		"""
		response = self._core.io.query_str('DISPlay:DIAGram:GRID?')
		return Conversions.str_to_bool(response)

	def set_grid(self, show: bool) -> None:
		"""DISPlay:DIAGram:GRID \n
		Snippet: driver.display.diagram.set_grid(show = False) \n
		If selected, a grid is displayed in the diagram area. A grid helps you associate a specific data point to its exact value
		on the x- or y-axis. \n
			:param show: No help available
		"""
		param = Conversions.bool_to_str(show)
		self._core.io.write(f'DISPlay:DIAGram:GRID {param}')

	def get_labels(self) -> bool:
		"""DISPlay:DIAGram:LABels \n
		Snippet: value: bool = driver.display.diagram.get_labels() \n
		If selected, labels mark values on the x- and y-axes in specified intervals in the diagram. \n
			:return: show_labels: No help available
		"""
		response = self._core.io.query_str('DISPlay:DIAGram:LABels?')
		return Conversions.str_to_bool(response)

	def set_labels(self, show_labels: bool) -> None:
		"""DISPlay:DIAGram:LABels \n
		Snippet: driver.display.diagram.set_labels(show_labels = False) \n
		If selected, labels mark values on the x- and y-axes in specified intervals in the diagram. \n
			:param show_labels: No help available
		"""
		param = Conversions.bool_to_str(show_labels)
		self._core.io.write(f'DISPlay:DIAGram:LABels {param}')

	# noinspection PyTypeChecker
	def get_style(self) -> enums.DiagramStyle:
		"""DISPlay:DIAGram:STYLe \n
		Snippet: value: enums.DiagramStyle = driver.display.diagram.get_style() \n
		Selects the style in which the waveform is displayed. \n
			:return: style:
				- VECTors: The individual data points are connected by a line.
				- DOTS: Only the individual data points are displayed."""
		response = self._core.io.query_str('DISPlay:DIAGram:STYLe?')
		return Conversions.str_to_scalar_enum(response, enums.DiagramStyle)

	def set_style(self, style: enums.DiagramStyle) -> None:
		"""DISPlay:DIAGram:STYLe \n
		Snippet: driver.display.diagram.set_style(style = enums.DiagramStyle.DOTS) \n
		Selects the style in which the waveform is displayed. \n
			:param style:
				- VECTors: The individual data points are connected by a line.
				- DOTS: Only the individual data points are displayed."""
		param = Conversions.enum_scalar_to_str(style, enums.DiagramStyle)
		self._core.io.write(f'DISPlay:DIAGram:STYLe {param}')

	def get_xfixed(self) -> bool:
		"""DISPlay:DIAGram:XFIXed \n
		Snippet: value: bool = driver.display.diagram.get_xfixed() \n
		If enabled, the vertical grid lines remain in their position when the horizontal position is changed. Only the values at
		the grid lines are adapted. \n
			:return: xgrid_fixed: No help available
		"""
		response = self._core.io.query_str('DISPlay:DIAGram:XFIXed?')
		return Conversions.str_to_bool(response)

	def set_xfixed(self, xgrid_fixed: bool) -> None:
		"""DISPlay:DIAGram:XFIXed \n
		Snippet: driver.display.diagram.set_xfixed(xgrid_fixed = False) \n
		If enabled, the vertical grid lines remain in their position when the horizontal position is changed. Only the values at
		the grid lines are adapted. \n
			:param xgrid_fixed: No help available
		"""
		param = Conversions.bool_to_str(xgrid_fixed)
		self._core.io.write(f'DISPlay:DIAGram:XFIXed {param}')

	def get_yfixed(self) -> bool:
		"""DISPlay:DIAGram:YFIXed \n
		Snippet: value: bool = driver.display.diagram.get_yfixed() \n
		If enabled, the horizontal grid lines remain in their position when the position of the curve is changed. Only the values
		at the grid lines are adapted. Fixed horizontal grid lines correspond to the behavior of traditional oscilloscopes. \n
			:return: ygrid_fixed: No help available
		"""
		response = self._core.io.query_str('DISPlay:DIAGram:YFIXed?')
		return Conversions.str_to_bool(response)

	def set_yfixed(self, ygrid_fixed: bool) -> None:
		"""DISPlay:DIAGram:YFIXed \n
		Snippet: driver.display.diagram.set_yfixed(ygrid_fixed = False) \n
		If enabled, the horizontal grid lines remain in their position when the position of the curve is changed. Only the values
		at the grid lines are adapted. Fixed horizontal grid lines correspond to the behavior of traditional oscilloscopes. \n
			:param ygrid_fixed: No help available
		"""
		param = Conversions.bool_to_str(ygrid_fixed)
		self._core.io.write(f'DISPlay:DIAGram:YFIXed {param}')

	def get_fine_grid(self) -> bool:
		"""DISPlay:DIAGram:FINegrid \n
		Snippet: value: bool = driver.display.diagram.get_fine_grid() \n
		If selected, the crosshair is displayed as a ruler with scale markers. If disabled, the crosshair is shown as dashed
		lines. \n
			:return: show_fine_scale: No help available
		"""
		response = self._core.io.query_str('DISPlay:DIAGram:FINegrid?')
		return Conversions.str_to_bool(response)

	def set_fine_grid(self, show_fine_scale: bool) -> None:
		"""DISPlay:DIAGram:FINegrid \n
		Snippet: driver.display.diagram.set_fine_grid(show_fine_scale = False) \n
		If selected, the crosshair is displayed as a ruler with scale markers. If disabled, the crosshair is shown as dashed
		lines. \n
			:param show_fine_scale: No help available
		"""
		param = Conversions.bool_to_str(show_fine_scale)
		self._core.io.write(f'DISPlay:DIAGram:FINegrid {param}')
