from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SegmentedCls:
	"""Segmented commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("segmented", core, parent)

	def get_state(self) -> bool:
		"""ACQuire:SEGMented:STATe \n
		Snippet: value: bool = driver.acquire.segmented.get_state() \n
		If fast segmentation is enabled, the acquisitions are performed as fast as possible, without processing and displaying
		the waveforms. When acquisition has been stopped, the data is processed and the latest waveform is displayed.
		Older waveforms are stored in segments. You can display and analyze the segments using the history. \n
			:return: state: No help available
		"""
		response = self._core.io.query_str('ACQuire:SEGMented:STATe?')
		return Conversions.str_to_bool(response)

	def set_state(self, state: bool) -> None:
		"""ACQuire:SEGMented:STATe \n
		Snippet: driver.acquire.segmented.set_state(state = False) \n
		If fast segmentation is enabled, the acquisitions are performed as fast as possible, without processing and displaying
		the waveforms. When acquisition has been stopped, the data is processed and the latest waveform is displayed.
		Older waveforms are stored in segments. You can display and analyze the segments using the history. \n
			:param state: No help available
		"""
		param = Conversions.bool_to_str(state)
		self._core.io.write(f'ACQuire:SEGMented:STATe {param}')

	def get_auto_replay(self) -> bool:
		"""ACQuire:SEGMented:AUToreplay \n
		Snippet: value: bool = driver.acquire.segmented.get_auto_replay() \n
		No command help available \n
			:return: replay_after_acq: No help available
		"""
		response = self._core.io.query_str('ACQuire:SEGMented:AUToreplay?')
		return Conversions.str_to_bool(response)

	def set_auto_replay(self, replay_after_acq: bool) -> None:
		"""ACQuire:SEGMented:AUToreplay \n
		Snippet: driver.acquire.segmented.set_auto_replay(replay_after_acq = False) \n
		No command help available \n
			:param replay_after_acq: No help available
		"""
		param = Conversions.bool_to_str(replay_after_acq)
		self._core.io.write(f'ACQuire:SEGMented:AUToreplay {param}')

	def get_max(self) -> bool:
		"""ACQuire:SEGMented:MAX \n
		Snippet: value: bool = driver.acquire.segmented.get_max() \n
		If ON, the instrument acquires the maximum number of segments that can be stored in the memory. The maximum number
		depends on the current sample rate and record length settings. If OFF, define the number of segments in a fast
		segmentation cycle with method RsMxo.Acquire.count. \n
			:return: max_acqs: No help available
		"""
		response = self._core.io.query_str('ACQuire:SEGMented:MAX?')
		return Conversions.str_to_bool(response)

	def set_max(self, max_acqs: bool) -> None:
		"""ACQuire:SEGMented:MAX \n
		Snippet: driver.acquire.segmented.set_max(max_acqs = False) \n
		If ON, the instrument acquires the maximum number of segments that can be stored in the memory. The maximum number
		depends on the current sample rate and record length settings. If OFF, define the number of segments in a fast
		segmentation cycle with method RsMxo.Acquire.count. \n
			:param max_acqs: No help available
		"""
		param = Conversions.bool_to_str(max_acqs)
		self._core.io.write(f'ACQuire:SEGMented:MAX {param}')
