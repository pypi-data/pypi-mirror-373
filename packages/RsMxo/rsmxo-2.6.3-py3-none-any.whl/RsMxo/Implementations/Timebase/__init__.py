from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TimebaseCls:
	"""Timebase commands group definition. 8 total commands, 2 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("timebase", core, parent)

	@property
	def roll(self):
		"""roll commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_roll'):
			from .Roll import RollCls
			self._roll = RollCls(self._core, self._cmd_group)
		return self._roll

	@property
	def horizontal(self):
		"""horizontal commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_horizontal'):
			from .Horizontal import HorizontalCls
			self._horizontal = HorizontalCls(self._core, self._cmd_group)
		return self._horizontal

	def get_divisions(self) -> int:
		"""TIMebase:DIVisions \n
		Snippet: value: int = driver.timebase.get_divisions() \n
		Returns the number of horizontal divisions on the screen. The number cannot be changed. \n
			:return: horiz_div_cnt: No help available
		"""
		response = self._core.io.query_str('TIMebase:DIVisions?')
		return Conversions.str_to_int(response)

	def get_range(self) -> float:
		"""TIMebase:RANGe \n
		Snippet: value: float = driver.timebase.get_range() \n
		Sets the time of one acquisition, which is the time across the 10 divisions of the diagram: Acquisition time = Time scale
		* 10 divisions. \n
			:return: timebase_range: No help available
		"""
		response = self._core.io.query_str('TIMebase:RANGe?')
		return Conversions.str_to_float(response)

	def set_range(self, timebase_range: float) -> None:
		"""TIMebase:RANGe \n
		Snippet: driver.timebase.set_range(timebase_range = 1.0) \n
		Sets the time of one acquisition, which is the time across the 10 divisions of the diagram: Acquisition time = Time scale
		* 10 divisions. \n
			:param timebase_range: No help available
		"""
		param = Conversions.decimal_value_to_str(timebase_range)
		self._core.io.write(f'TIMebase:RANGe {param}')

	def get_reference(self) -> float:
		"""TIMebase:REFerence \n
		Snippet: value: float = driver.timebase.get_reference() \n
		Sets the position of the reference point in % of the screen. It defines which part of the waveform is shown. \n
			:return: rescale_ctr_pos: No help available
		"""
		response = self._core.io.query_str('TIMebase:REFerence?')
		return Conversions.str_to_float(response)

	def set_reference(self, rescale_ctr_pos: float) -> None:
		"""TIMebase:REFerence \n
		Snippet: driver.timebase.set_reference(rescale_ctr_pos = 1.0) \n
		Sets the position of the reference point in % of the screen. It defines which part of the waveform is shown. \n
			:param rescale_ctr_pos: No help available
		"""
		param = Conversions.decimal_value_to_str(rescale_ctr_pos)
		self._core.io.write(f'TIMebase:REFerence {param}')

	def get_scale(self) -> float:
		"""TIMebase:SCALe \n
		Snippet: value: float = driver.timebase.get_scale() \n
		Sets the horizontal scale, the time per division, for all waveforms in the time domain, for example, channel and math
		waveforms. \n
			:return: timebase_scale: No help available
		"""
		response = self._core.io.query_str('TIMebase:SCALe?')
		return Conversions.str_to_float(response)

	def set_scale(self, timebase_scale: float) -> None:
		"""TIMebase:SCALe \n
		Snippet: driver.timebase.set_scale(timebase_scale = 1.0) \n
		Sets the horizontal scale, the time per division, for all waveforms in the time domain, for example, channel and math
		waveforms. \n
			:param timebase_scale: No help available
		"""
		param = Conversions.decimal_value_to_str(timebase_scale)
		self._core.io.write(f'TIMebase:SCALe {param}')

	def clone(self) -> 'TimebaseCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = TimebaseCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
