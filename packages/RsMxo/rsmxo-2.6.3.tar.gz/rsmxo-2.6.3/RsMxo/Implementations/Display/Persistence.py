from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PersistenceCls:
	"""Persistence commands group definition. 4 total commands, 0 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("persistence", core, parent)

	def get_infinite(self) -> bool:
		"""DISPlay:PERSistence:INFinite \n
		Snippet: value: bool = driver.display.persistence.get_infinite() \n
		If infinite persistence is enabled, each new waveform point remains on the screen until this option is disabled.
		Use infinite persistence to display rare events in the signal. \n
			:return: state: No help available
		"""
		response = self._core.io.query_str('DISPlay:PERSistence:INFinite?')
		return Conversions.str_to_bool(response)

	def set_infinite(self, state: bool) -> None:
		"""DISPlay:PERSistence:INFinite \n
		Snippet: driver.display.persistence.set_infinite(state = False) \n
		If infinite persistence is enabled, each new waveform point remains on the screen until this option is disabled.
		Use infinite persistence to display rare events in the signal. \n
			:param state: No help available
		"""
		param = Conversions.bool_to_str(state)
		self._core.io.write(f'DISPlay:PERSistence:INFinite {param}')

	def reset(self) -> None:
		"""DISPlay:PERSistence:RESet \n
		Snippet: driver.display.persistence.reset() \n
		Resets the display, removing persistent all waveform points. \n
		"""
		self._core.io.write(f'DISPlay:PERSistence:RESet')

	def reset_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""DISPlay:PERSistence:RESet \n
		Snippet: driver.display.persistence.reset_and_wait() \n
		Resets the display, removing persistent all waveform points. \n
		Same as reset, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'DISPlay:PERSistence:RESet', opc_timeout_ms)

	def get_time(self) -> float:
		"""DISPlay:PERSistence:TIME \n
		Snippet: value: float = driver.display.persistence.get_time() \n
		Sets a time factor that controls how long the waveforms points fade away from the display. Thus, the MXO 5 emulates the
		persistence of analog phosphor screens. \n
			:return: time: No help available
		"""
		response = self._core.io.query_str('DISPlay:PERSistence:TIME?')
		return Conversions.str_to_float(response)

	def set_time(self, time: float) -> None:
		"""DISPlay:PERSistence:TIME \n
		Snippet: driver.display.persistence.set_time(time = 1.0) \n
		Sets a time factor that controls how long the waveforms points fade away from the display. Thus, the MXO 5 emulates the
		persistence of analog phosphor screens. \n
			:param time: No help available
		"""
		param = Conversions.decimal_value_to_str(time)
		self._core.io.write(f'DISPlay:PERSistence:TIME {param}')

	def get_state(self) -> bool:
		"""DISPlay:PERSistence[:STATe] \n
		Snippet: value: bool = driver.display.persistence.get_state() \n
		If enabled, each new data point in the diagram area remains on the screen for the duration defined using method RsMxo.
		Display.Persistence.time, or as long as method RsMxo.Display.Persistence.infinite is enabled. If disabled, the signal
		value is only displayed as long as it actually occurs. \n
			:return: state: No help available
		"""
		response = self._core.io.query_str('DISPlay:PERSistence:STATe?')
		return Conversions.str_to_bool(response)

	def set_state(self, state: bool) -> None:
		"""DISPlay:PERSistence[:STATe] \n
		Snippet: driver.display.persistence.set_state(state = False) \n
		If enabled, each new data point in the diagram area remains on the screen for the duration defined using method RsMxo.
		Display.Persistence.time, or as long as method RsMxo.Display.Persistence.infinite is enabled. If disabled, the signal
		value is only displayed as long as it actually occurs. \n
			:param state: No help available
		"""
		param = Conversions.bool_to_str(state)
		self._core.io.write(f'DISPlay:PERSistence:STATe {param}')
