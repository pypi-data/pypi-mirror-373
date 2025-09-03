from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RollModeCls:
	"""RollMode commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rollMode", core, parent)

	def get_points(self) -> int:
		"""ACQuire:ROLLmode:POINts \n
		Snippet: value: int = driver.acquire.rollMode.get_points() \n
		Returns the record length of the roll mode. In roll mode, the complete record is always captured, independently of the
		displayed waveform. To process and analyze the complete roll waveform, enable method RsMxo.Acquire.RollMode.osCapture. \n
			:return: record_length: No help available
		"""
		response = self._core.io.query_str('ACQuire:ROLLmode:POINts?')
		return Conversions.str_to_int(response)

	def get_os_capture(self) -> bool:
		"""ACQuire:ROLLmode:OSCapture \n
		Snippet: value: bool = driver.acquire.rollMode.get_os_capture() \n
		If enabled, the analyzable waveform in roll mode is extended. You can run the roll mode, stop the acquisition after some
		time, and analyze the data that is on the display and in the unvisible area on the left. \n
			:return: off_screen_capture: No help available
		"""
		response = self._core.io.query_str('ACQuire:ROLLmode:OSCapture?')
		return Conversions.str_to_bool(response)

	def set_os_capture(self, off_screen_capture: bool) -> None:
		"""ACQuire:ROLLmode:OSCapture \n
		Snippet: driver.acquire.rollMode.set_os_capture(off_screen_capture = False) \n
		If enabled, the analyzable waveform in roll mode is extended. You can run the roll mode, stop the acquisition after some
		time, and analyze the data that is on the display and in the unvisible area on the left. \n
			:param off_screen_capture: No help available
		"""
		param = Conversions.bool_to_str(off_screen_capture)
		self._core.io.write(f'ACQuire:ROLLmode:OSCapture {param}')
