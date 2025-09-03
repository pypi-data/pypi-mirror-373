from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SaveCls:
	"""Save commands group definition. 4 total commands, 0 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("save", core, parent)

	def set_execute(self, file_path: str) -> None:
		"""SESSion:SAVE[:EXECute] \n
		Snippet: driver.sessions.save.set_execute(file_path = 'abc') \n
		Saves the current session with selected content to the specified file. \n
			:param file_path: String parameter specifying path and filename of the target file.
		"""
		param = Conversions.value_to_quoted_str(file_path)
		self._core.io.write(f'SESSion:SAVE:EXECute {param}')

	def get_channel(self) -> bool:
		"""SESSion:SAVE:CHANnel \n
		Snippet: value: bool = driver.sessions.save.get_channel() \n
		Includes the channel waveform data in the session file. \n
			:return: ch_waveforms: No help available
		"""
		response = self._core.io.query_str('SESSion:SAVE:CHANnel?')
		return Conversions.str_to_bool(response)

	def set_channel(self, ch_waveforms: bool) -> None:
		"""SESSion:SAVE:CHANnel \n
		Snippet: driver.sessions.save.set_channel(ch_waveforms = False) \n
		Includes the channel waveform data in the session file. \n
			:param ch_waveforms: No help available
		"""
		param = Conversions.bool_to_str(ch_waveforms)
		self._core.io.write(f'SESSion:SAVE:CHANnel {param}')

	def abort(self) -> None:
		"""SESSion:SAVE:ABORt \n
		Snippet: driver.sessions.save.abort() \n
		Stops the saving process of a session file. \n
		"""
		self._core.io.write(f'SESSion:SAVE:ABORt')

	def abort_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""SESSion:SAVE:ABORt \n
		Snippet: driver.sessions.save.abort_and_wait() \n
		Stops the saving process of a session file. \n
		Same as abort, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SESSion:SAVE:ABORt', opc_timeout_ms)

	def get_reference(self) -> bool:
		"""SESSion:SAVE:REFerence \n
		Snippet: value: bool = driver.sessions.save.get_reference() \n
		Includes the reference waveform data in the session file. \n
			:return: ref_wfms: No help available
		"""
		response = self._core.io.query_str('SESSion:SAVE:REFerence?')
		return Conversions.str_to_bool(response)

	def set_reference(self, ref_wfms: bool) -> None:
		"""SESSion:SAVE:REFerence \n
		Snippet: driver.sessions.save.set_reference(ref_wfms = False) \n
		Includes the reference waveform data in the session file. \n
			:param ref_wfms: No help available
		"""
		param = Conversions.bool_to_str(ref_wfms)
		self._core.io.write(f'SESSion:SAVE:REFerence {param}')
