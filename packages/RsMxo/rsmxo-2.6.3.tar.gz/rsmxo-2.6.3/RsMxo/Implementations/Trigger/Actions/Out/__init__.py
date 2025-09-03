from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OutCls:
	"""Out commands group definition. 10 total commands, 1 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("out", core, parent)

	@property
	def overload(self):
		"""overload commands group. 1 Sub-classes, 0 commands."""
		if not hasattr(self, '_overload'):
			from .Overload import OverloadCls
			self._overload = OverloadCls(self._core, self._cmd_group)
		return self._overload

	def get_state(self) -> bool:
		"""TRIGger:ACTions:OUT:STATe \n
		Snippet: value: bool = driver.trigger.actions.out.get_state() \n
		Activates the outgoing pulse on the Trigger Out connector on the rear panel. If ON, a pulse is sent out each time when a
		trigger occurs. \n
			:return: state: No help available
		"""
		response = self._core.io.query_str('TRIGger:ACTions:OUT:STATe?')
		return Conversions.str_to_bool(response)

	def set_state(self, state: bool) -> None:
		"""TRIGger:ACTions:OUT:STATe \n
		Snippet: driver.trigger.actions.out.set_state(state = False) \n
		Activates the outgoing pulse on the Trigger Out connector on the rear panel. If ON, a pulse is sent out each time when a
		trigger occurs. \n
			:param state: No help available
		"""
		param = Conversions.bool_to_str(state)
		self._core.io.write(f'TRIGger:ACTions:OUT:STATe {param}')

	# noinspection PyTypeChecker
	def get_polarity(self) -> enums.SlopeType:
		"""TRIGger:ACTions:OUT:POLarity \n
		Snippet: value: enums.SlopeType = driver.trigger.actions.out.get_polarity() \n
		Sets the polarity of the trigger out pulse, which is the direction of the first pulse edge. \n
			:return: polarity: No help available
		"""
		response = self._core.io.query_str('TRIGger:ACTions:OUT:POLarity?')
		return Conversions.str_to_scalar_enum(response, enums.SlopeType)

	def set_polarity(self, polarity: enums.SlopeType) -> None:
		"""TRIGger:ACTions:OUT:POLarity \n
		Snippet: driver.trigger.actions.out.set_polarity(polarity = enums.SlopeType.NEGative) \n
		Sets the polarity of the trigger out pulse, which is the direction of the first pulse edge. \n
			:param polarity: No help available
		"""
		param = Conversions.enum_scalar_to_str(polarity, enums.SlopeType)
		self._core.io.write(f'TRIGger:ACTions:OUT:POLarity {param}')

	def get_delay(self) -> float:
		"""TRIGger:ACTions:OUT:DELay \n
		Snippet: value: float = driver.trigger.actions.out.get_delay() \n
		Defines the delay of the first pulse edge to the trigger point. The minimum delay is 600 ns. \n
			:return: delay: No help available
		"""
		response = self._core.io.query_str('TRIGger:ACTions:OUT:DELay?')
		return Conversions.str_to_float(response)

	def set_delay(self, delay: float) -> None:
		"""TRIGger:ACTions:OUT:DELay \n
		Snippet: driver.trigger.actions.out.set_delay(delay = 1.0) \n
		Defines the delay of the first pulse edge to the trigger point. The minimum delay is 600 ns. \n
			:param delay: No help available
		"""
		param = Conversions.decimal_value_to_str(delay)
		self._core.io.write(f'TRIGger:ACTions:OUT:DELay {param}')

	def get_plength(self) -> float:
		"""TRIGger:ACTions:OUT:PLENgth \n
		Snippet: value: float = driver.trigger.actions.out.get_plength() \n
		Sets the length of the trigger out pulse. \n
			:return: pulse_length: No help available
		"""
		response = self._core.io.query_str('TRIGger:ACTions:OUT:PLENgth?')
		return Conversions.str_to_float(response)

	def set_plength(self, pulse_length: float) -> None:
		"""TRIGger:ACTions:OUT:PLENgth \n
		Snippet: driver.trigger.actions.out.set_plength(pulse_length = 1.0) \n
		Sets the length of the trigger out pulse. \n
			:param pulse_length: No help available
		"""
		param = Conversions.decimal_value_to_str(pulse_length)
		self._core.io.write(f'TRIGger:ACTions:OUT:PLENgth {param}')

	# noinspection PyTypeChecker
	def get_source(self) -> enums.TriggerOutSource:
		"""TRIGger:ACTions:OUT:SOURce \n
		Snippet: value: enums.TriggerOutSource = driver.trigger.actions.out.get_source() \n
		Defines when the trigger out signal is initiated: at the trigger point, when waiting for the trigger, or when the
		post-trigger time is finished. \n
			:return: signal_source: TRIG = TRIGGER, POST = POSTTRIGGER, WAIT = WAITTRIGGER
		"""
		response = self._core.io.query_str('TRIGger:ACTions:OUT:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.TriggerOutSource)

	def set_source(self, signal_source: enums.TriggerOutSource) -> None:
		"""TRIGger:ACTions:OUT:SOURce \n
		Snippet: driver.trigger.actions.out.set_source(signal_source = enums.TriggerOutSource.POST) \n
		Defines when the trigger out signal is initiated: at the trigger point, when waiting for the trigger, or when the
		post-trigger time is finished. \n
			:param signal_source: TRIG = TRIGGER, POST = POSTTRIGGER, WAIT = WAITTRIGGER
		"""
		param = Conversions.enum_scalar_to_str(signal_source, enums.TriggerOutSource)
		self._core.io.write(f'TRIGger:ACTions:OUT:SOURce {param}')

	def clone(self) -> 'OutCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = OutCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
