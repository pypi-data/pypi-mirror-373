from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DelayCls:
	"""Delay commands group definition. 4 total commands, 1 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("delay", core, parent)

	@property
	def period(self):
		"""period commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_period'):
			from .Period import PeriodCls
			self._period = PeriodCls(self._core, self._cmd_group)
		return self._period

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.MeasDelayMode:
		"""FRANalysis:MEASurement:DELay:MODE \n
		Snippet: value: enums.MeasDelayMode = driver.franalysis.measurement.delay.get_mode() \n
		No command help available \n
			:return: meas_delay_mode: No help available
		"""
		response = self._core.io.query_str('FRANalysis:MEASurement:DELay:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.MeasDelayMode)

	def set_mode(self, meas_delay_mode: enums.MeasDelayMode) -> None:
		"""FRANalysis:MEASurement:DELay:MODE \n
		Snippet: driver.franalysis.measurement.delay.set_mode(meas_delay_mode = enums.MeasDelayMode.PERiod) \n
		No command help available \n
			:param meas_delay_mode: No help available
		"""
		param = Conversions.enum_scalar_to_str(meas_delay_mode, enums.MeasDelayMode)
		self._core.io.write(f'FRANalysis:MEASurement:DELay:MODE {param}')

	def get_time(self) -> float:
		"""FRANalysis:MEASurement:DELay[:TIME] \n
		Snippet: value: float = driver.franalysis.measurement.delay.get_time() \n
		Sets a time delay, that the system waits before measuring the next point of the plot. This is helpful in systems that
		need more time to adapt to the new frequency, for example if filters with significant time group delays are present.
		Available, if method RsMxo.Franalysis.Measurement.Delay.state = ON. \n
			:return: meas_delay_time: No help available
		"""
		response = self._core.io.query_str('FRANalysis:MEASurement:DELay:TIME?')
		return Conversions.str_to_float(response)

	def set_time(self, meas_delay_time: float) -> None:
		"""FRANalysis:MEASurement:DELay[:TIME] \n
		Snippet: driver.franalysis.measurement.delay.set_time(meas_delay_time = 1.0) \n
		Sets a time delay, that the system waits before measuring the next point of the plot. This is helpful in systems that
		need more time to adapt to the new frequency, for example if filters with significant time group delays are present.
		Available, if method RsMxo.Franalysis.Measurement.Delay.state = ON. \n
			:param meas_delay_time: No help available
		"""
		param = Conversions.decimal_value_to_str(meas_delay_time)
		self._core.io.write(f'FRANalysis:MEASurement:DELay:TIME {param}')

	def get_state(self) -> bool:
		"""FRANalysis:MEASurement:DELay:STATe \n
		Snippet: value: bool = driver.franalysis.measurement.delay.get_state() \n
		Enables the measurement delay. Set a measurement delay time with method RsMxo.Franalysis.Measurement.Delay.time. \n
			:return: meas_delay: No help available
		"""
		response = self._core.io.query_str('FRANalysis:MEASurement:DELay:STATe?')
		return Conversions.str_to_bool(response)

	def set_state(self, meas_delay: bool) -> None:
		"""FRANalysis:MEASurement:DELay:STATe \n
		Snippet: driver.franalysis.measurement.delay.set_state(meas_delay = False) \n
		Enables the measurement delay. Set a measurement delay time with method RsMxo.Franalysis.Measurement.Delay.time. \n
			:param meas_delay: No help available
		"""
		param = Conversions.bool_to_str(meas_delay)
		self._core.io.write(f'FRANalysis:MEASurement:DELay:STATe {param}')

	def clone(self) -> 'DelayCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = DelayCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
