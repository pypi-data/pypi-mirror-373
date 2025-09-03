from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HoldoffCls:
	"""Holdoff commands group definition. 7 total commands, 0 Subgroups, 7 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("holdoff", core, parent)

	def get_auto_time(self) -> float:
		"""TRIGger:HOLDoff:AUTotime \n
		Snippet: value: float = driver.trigger.holdoff.get_auto_time() \n
		Returns the resulting holdoff time, if method RsMxo.Trigger.Holdoff.mode is set to AUTO: Auto time = Auto time scaling *
		Horizontal scale. The auto time scaling factor is defined with method RsMxo.Trigger.Holdoff.scaling. \n
			:return: auto_time: No help available
		"""
		response = self._core.io.query_str('TRIGger:HOLDoff:AUTotime?')
		return Conversions.str_to_float(response)

	def get_events(self) -> int:
		"""TRIGger:HOLDoff:EVENts \n
		Snippet: value: int = driver.trigger.holdoff.get_events() \n
		Defines the number of triggers to be skipped, if method RsMxo.Trigger.Holdoff.mode is set to EVENts. The next trigger
		only occurs when this number of events is reached. \n
			:return: events: No help available
		"""
		response = self._core.io.query_str('TRIGger:HOLDoff:EVENts?')
		return Conversions.str_to_int(response)

	def set_events(self, events: int) -> None:
		"""TRIGger:HOLDoff:EVENts \n
		Snippet: driver.trigger.holdoff.set_events(events = 1) \n
		Defines the number of triggers to be skipped, if method RsMxo.Trigger.Holdoff.mode is set to EVENts. The next trigger
		only occurs when this number of events is reached. \n
			:param events: No help available
		"""
		param = Conversions.decimal_value_to_str(events)
		self._core.io.write(f'TRIGger:HOLDoff:EVENts {param}')

	def get_max(self) -> float:
		"""TRIGger:HOLDoff:MAX \n
		Snippet: value: float = driver.trigger.holdoff.get_max() \n
		Defines the upper limit for the random time holdoff, if method RsMxo.Trigger.Holdoff.mode is set to RANDom. \n
			:return: random_max_time: No help available
		"""
		response = self._core.io.query_str('TRIGger:HOLDoff:MAX?')
		return Conversions.str_to_float(response)

	def set_max(self, random_max_time: float) -> None:
		"""TRIGger:HOLDoff:MAX \n
		Snippet: driver.trigger.holdoff.set_max(random_max_time = 1.0) \n
		Defines the upper limit for the random time holdoff, if method RsMxo.Trigger.Holdoff.mode is set to RANDom. \n
			:param random_max_time: No help available
		"""
		param = Conversions.decimal_value_to_str(random_max_time)
		self._core.io.write(f'TRIGger:HOLDoff:MAX {param}')

	def get_min(self) -> float:
		"""TRIGger:HOLDoff:MIN \n
		Snippet: value: float = driver.trigger.holdoff.get_min() \n
		Defines the lower limit for the random time holdoff, if method RsMxo.Trigger.Holdoff.mode is set to RANDom. \n
			:return: random_min_time: No help available
		"""
		response = self._core.io.query_str('TRIGger:HOLDoff:MIN?')
		return Conversions.str_to_float(response)

	def set_min(self, random_min_time: float) -> None:
		"""TRIGger:HOLDoff:MIN \n
		Snippet: driver.trigger.holdoff.set_min(random_min_time = 1.0) \n
		Defines the lower limit for the random time holdoff, if method RsMxo.Trigger.Holdoff.mode is set to RANDom. \n
			:param random_min_time: No help available
		"""
		param = Conversions.decimal_value_to_str(random_min_time)
		self._core.io.write(f'TRIGger:HOLDoff:MIN {param}')

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.TriggerHoldoffMode:
		"""TRIGger:HOLDoff:MODE \n
		Snippet: value: enums.TriggerHoldoffMode = driver.trigger.holdoff.get_mode() \n
		Selects the method to define the holdoff condition. The trigger holdoff defines when the next trigger after the current
		will be recognized. Thus, it affects the next trigger to occur after the current one. Holdoff helps to obtain stable
		triggering when the oscilloscope is triggering on undesired events. Holdoff settings are not available if the trigger
		source is an external trigger input or serial bus, and if you trigger on a sequence of events. \n
			:return: mode:
				- TIME: Defines the holdoff directly as a time period. The next trigger occurs only after the holdoff time has passed, which is defined using TRIGger:HOLDoff:TIME) .
				- EVENts: Defines the holdoff as a number of trigger events. The next trigger occurs only when this number of events is reached. The number of triggers to be skipped is defined with TRIGger:HOLDoff:EVENts.
				- RANDom: Defines the holdoff as a random time limited by TRIGger:HOLDoff:MIN and TRIGger:HOLDoff:MAX. For each acquisition cycle, the instrument selects a new random holdoff time from the specified range.
				- AUTO: The holdoff time is calculated automatically based on the current horizontal scale.
				- OFF: No holdoff"""
		response = self._core.io.query_str('TRIGger:HOLDoff:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerHoldoffMode)

	def set_mode(self, mode: enums.TriggerHoldoffMode) -> None:
		"""TRIGger:HOLDoff:MODE \n
		Snippet: driver.trigger.holdoff.set_mode(mode = enums.TriggerHoldoffMode.AUTO) \n
		Selects the method to define the holdoff condition. The trigger holdoff defines when the next trigger after the current
		will be recognized. Thus, it affects the next trigger to occur after the current one. Holdoff helps to obtain stable
		triggering when the oscilloscope is triggering on undesired events. Holdoff settings are not available if the trigger
		source is an external trigger input or serial bus, and if you trigger on a sequence of events. \n
			:param mode:
				- TIME: Defines the holdoff directly as a time period. The next trigger occurs only after the holdoff time has passed, which is defined using TRIGger:HOLDoff:TIME) .
				- EVENts: Defines the holdoff as a number of trigger events. The next trigger occurs only when this number of events is reached. The number of triggers to be skipped is defined with TRIGger:HOLDoff:EVENts.
				- RANDom: Defines the holdoff as a random time limited by TRIGger:HOLDoff:MIN and TRIGger:HOLDoff:MAX. For each acquisition cycle, the instrument selects a new random holdoff time from the specified range.
				- AUTO: The holdoff time is calculated automatically based on the current horizontal scale.
				- OFF: No holdoff"""
		param = Conversions.enum_scalar_to_str(mode, enums.TriggerHoldoffMode)
		self._core.io.write(f'TRIGger:HOLDoff:MODE {param}')

	def get_scaling(self) -> float:
		"""TRIGger:HOLDoff:SCALing \n
		Snippet: value: float = driver.trigger.holdoff.get_scaling() \n
		Sets the auto time scaling factor that the horizontal scale is multipied with, if method RsMxo.Trigger.Holdoff.mode is
		set to AUTO. Auto time = Auto time scaling * Horizontal scale The next trigger occurs only after this time has passed. \n
			:return: auto_time_scl: No help available
		"""
		response = self._core.io.query_str('TRIGger:HOLDoff:SCALing?')
		return Conversions.str_to_float(response)

	def set_scaling(self, auto_time_scl: float) -> None:
		"""TRIGger:HOLDoff:SCALing \n
		Snippet: driver.trigger.holdoff.set_scaling(auto_time_scl = 1.0) \n
		Sets the auto time scaling factor that the horizontal scale is multipied with, if method RsMxo.Trigger.Holdoff.mode is
		set to AUTO. Auto time = Auto time scaling * Horizontal scale The next trigger occurs only after this time has passed. \n
			:param auto_time_scl: No help available
		"""
		param = Conversions.decimal_value_to_str(auto_time_scl)
		self._core.io.write(f'TRIGger:HOLDoff:SCALing {param}')

	def get_time(self) -> float:
		"""TRIGger:HOLDoff:TIME \n
		Snippet: value: float = driver.trigger.holdoff.get_time() \n
		Defines the holdoff time period, if method RsMxo.Trigger.Holdoff.mode is set to TIME. The next trigger occurs only after
		this time has passed. \n
			:return: time: No help available
		"""
		response = self._core.io.query_str('TRIGger:HOLDoff:TIME?')
		return Conversions.str_to_float(response)

	def set_time(self, time: float) -> None:
		"""TRIGger:HOLDoff:TIME \n
		Snippet: driver.trigger.holdoff.set_time(time = 1.0) \n
		Defines the holdoff time period, if method RsMxo.Trigger.Holdoff.mode is set to TIME. The next trigger occurs only after
		this time has passed. \n
			:param time: No help available
		"""
		param = Conversions.decimal_value_to_str(time)
		self._core.io.write(f'TRIGger:HOLDoff:TIME {param}')
