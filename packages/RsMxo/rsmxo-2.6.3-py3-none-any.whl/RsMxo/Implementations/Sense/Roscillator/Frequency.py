from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrequencyCls:
	"""Frequency commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("frequency", core, parent)

	# noinspection PyTypeChecker
	def get_value(self) -> enums.InputSelection:
		"""SENSe[:ROSCillator]:FREQuency[:VALue] \n
		Snippet: value: enums.InputSelection = driver.sense.roscillator.frequency.get_value() \n
		No command help available \n
			:return: input_selection: No help available
		"""
		response = self._core.io.query_str('SENSe:ROSCillator:FREQuency:VALue?')
		return Conversions.str_to_scalar_enum(response, enums.InputSelection)

	def set_value(self, input_selection: enums.InputSelection) -> None:
		"""SENSe[:ROSCillator]:FREQuency[:VALue] \n
		Snippet: driver.sense.roscillator.frequency.set_value(input_selection = enums.InputSelection.GHZ1) \n
		No command help available \n
			:param input_selection: No help available
		"""
		param = Conversions.enum_scalar_to_str(input_selection, enums.InputSelection)
		self._core.io.write(f'SENSe:ROSCillator:FREQuency:VALue {param}')

	def get_variable(self) -> float:
		"""SENSe[:ROSCillator]:FREQuency:VARiable \n
		Snippet: value: float = driver.sense.roscillator.frequency.get_variable() \n
		No command help available \n
			:return: variable_freq: No help available
		"""
		response = self._core.io.query_str('SENSe:ROSCillator:FREQuency:VARiable?')
		return Conversions.str_to_float(response)

	def set_variable(self, variable_freq: float) -> None:
		"""SENSe[:ROSCillator]:FREQuency:VARiable \n
		Snippet: driver.sense.roscillator.frequency.set_variable(variable_freq = 1.0) \n
		No command help available \n
			:param variable_freq: No help available
		"""
		param = Conversions.decimal_value_to_str(variable_freq)
		self._core.io.write(f'SENSe:ROSCillator:FREQuency:VARiable {param}')
