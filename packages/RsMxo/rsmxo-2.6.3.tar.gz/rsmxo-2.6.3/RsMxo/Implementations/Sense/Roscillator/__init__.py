from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RoscillatorCls:
	"""Roscillator commands group definition. 5 total commands, 2 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("roscillator", core, parent)

	@property
	def frequency(self):
		"""frequency commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_frequency'):
			from .Frequency import FrequencyCls
			self._frequency = FrequencyCls(self._core, self._cmd_group)
		return self._frequency

	@property
	def output(self):
		"""output commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_output'):
			from .Output import OutputCls
			self._output = OutputCls(self._core, self._cmd_group)
		return self._output

	# noinspection PyTypeChecker
	def get_source(self) -> enums.SourceInt:
		"""SENSe[:ROSCillator]:SOURce \n
		Snippet: value: enums.SourceInt = driver.sense.roscillator.get_source() \n
		Enables the use of an external 10 MHz reference signal instead of the internal reference clock. \n
			:return: ref_osc_source: No help available
		"""
		response = self._core.io.query_str('SENSe:ROSCillator:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.SourceInt)

	def set_source(self, ref_osc_source: enums.SourceInt) -> None:
		"""SENSe[:ROSCillator]:SOURce \n
		Snippet: driver.sense.roscillator.set_source(ref_osc_source = enums.SourceInt.EXTernal) \n
		Enables the use of an external 10 MHz reference signal instead of the internal reference clock. \n
			:param ref_osc_source: No help available
		"""
		param = Conversions.enum_scalar_to_str(ref_osc_source, enums.SourceInt)
		self._core.io.write(f'SENSe:ROSCillator:SOURce {param}')

	def get_aligval(self) -> int:
		"""SENSe[:ROSCillator]:ALIGval \n
		Snippet: value: int = driver.sense.roscillator.get_aligval() \n
		No command help available \n
			:return: alignment_value: No help available
		"""
		response = self._core.io.query_str('SENSe:ROSCillator:ALIGval?')
		return Conversions.str_to_int(response)

	def set_aligval(self, alignment_value: int) -> None:
		"""SENSe[:ROSCillator]:ALIGval \n
		Snippet: driver.sense.roscillator.set_aligval(alignment_value = 1) \n
		No command help available \n
			:param alignment_value: No help available
		"""
		param = Conversions.decimal_value_to_str(alignment_value)
		self._core.io.write(f'SENSe:ROSCillator:ALIGval {param}')

	def clone(self) -> 'RoscillatorCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = RoscillatorCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
