from ..Internal.Core import Core
from ..Internal.CommandsGroup import CommandsGroup
from ..Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HdefinitionCls:
	"""Hdefinition commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("hdefinition", core, parent)

	def get_state(self) -> bool:
		"""HDEFinition:STATe \n
		Snippet: value: bool = driver.hdefinition.get_state() \n
		Enables high definition mode, which increases the numeric resolution of the waveform signal. \n
			:return: state: ON: high definition mode OFF: normal oscilloscope mode
		"""
		response = self._core.io.query_str('HDEFinition:STATe?')
		return Conversions.str_to_bool(response)

	def set_state(self, state: bool) -> None:
		"""HDEFinition:STATe \n
		Snippet: driver.hdefinition.set_state(state = False) \n
		Enables high definition mode, which increases the numeric resolution of the waveform signal. \n
			:param state: ON: high definition mode OFF: normal oscilloscope mode
		"""
		param = Conversions.bool_to_str(state)
		self._core.io.write(f'HDEFinition:STATe {param}')

	def get_bandwidth(self) -> float:
		"""HDEFinition:BWIDth \n
		Snippet: value: float = driver.hdefinition.get_bandwidth() \n
		Sets the filter bandwidth for the high definition mode. \n
			:return: bandwidth: No help available
		"""
		response = self._core.io.query_str('HDEFinition:BWIDth?')
		return Conversions.str_to_float(response)

	def set_bandwidth(self, bandwidth: float) -> None:
		"""HDEFinition:BWIDth \n
		Snippet: driver.hdefinition.set_bandwidth(bandwidth = 1.0) \n
		Sets the filter bandwidth for the high definition mode. \n
			:param bandwidth: No help available
		"""
		param = Conversions.decimal_value_to_str(bandwidth)
		self._core.io.write(f'HDEFinition:BWIDth {param}')

	def get_resolution(self) -> float:
		"""HDEFinition:RESolution \n
		Snippet: value: float = driver.hdefinition.get_resolution() \n
		Displays the resulting vertical resolution in high definition mode. The higher the filter bandwidth, the lower the
		resolution. \n
			:return: resolution: No help available
		"""
		response = self._core.io.query_str('HDEFinition:RESolution?')
		return Conversions.str_to_float(response)
