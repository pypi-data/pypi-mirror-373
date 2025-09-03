from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HistoryCls:
	"""History commands group definition. 12 total commands, 1 Subgroups, 11 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("history", core, parent)

	@property
	def play(self):
		"""play commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_play'):
			from .Play import PlayCls
			self._play = PlayCls(self._core, self._cmd_group)
		return self._play

	def get_start(self) -> int:
		"""ACQuire:HISTory:STARt \n
		Snippet: value: int = driver.acquire.history.get_start() \n
		Sets the index of the first (oldest) acquisition to be displayed or exported. The index is always negative. \n
			:return: strt_acq_idx: No help available
		"""
		response = self._core.io.query_str('ACQuire:HISTory:STARt?')
		return Conversions.str_to_int(response)

	def set_start(self, strt_acq_idx: int) -> None:
		"""ACQuire:HISTory:STARt \n
		Snippet: driver.acquire.history.set_start(strt_acq_idx = 1) \n
		Sets the index of the first (oldest) acquisition to be displayed or exported. The index is always negative. \n
			:param strt_acq_idx: No help available
		"""
		param = Conversions.decimal_value_to_str(strt_acq_idx)
		self._core.io.write(f'ACQuire:HISTory:STARt {param}')

	def get_stop(self) -> int:
		"""ACQuire:HISTory:STOP \n
		Snippet: value: int = driver.acquire.history.get_stop() \n
		Sets the index of the last (newest) acquisition to be displayed or exported. The newest acquisition of the complete
		acquisition series always has the index '0'. \n
			:return: stp_acq_idx: No help available
		"""
		response = self._core.io.query_str('ACQuire:HISTory:STOP?')
		return Conversions.str_to_int(response)

	def set_stop(self, stp_acq_idx: int) -> None:
		"""ACQuire:HISTory:STOP \n
		Snippet: driver.acquire.history.set_stop(stp_acq_idx = 1) \n
		Sets the index of the last (newest) acquisition to be displayed or exported. The newest acquisition of the complete
		acquisition series always has the index '0'. \n
			:param stp_acq_idx: No help available
		"""
		param = Conversions.decimal_value_to_str(stp_acq_idx)
		self._core.io.write(f'ACQuire:HISTory:STOP {param}')

	def get_current(self) -> int:
		"""ACQuire:HISTory:CURRent \n
		Snippet: value: int = driver.acquire.history.get_current() \n
		Accesses a particular acquisition in the memory to display it, or to save it. The newest acquisition always has the index
		'0'. Older acquisitions have a negative index. \n
			:return: curr_acq_idx: No help available
		"""
		response = self._core.io.query_str('ACQuire:HISTory:CURRent?')
		return Conversions.str_to_int(response)

	def set_current(self, curr_acq_idx: int) -> None:
		"""ACQuire:HISTory:CURRent \n
		Snippet: driver.acquire.history.set_current(curr_acq_idx = 1) \n
		Accesses a particular acquisition in the memory to display it, or to save it. The newest acquisition always has the index
		'0'. Older acquisitions have a negative index. \n
			:param curr_acq_idx: No help available
		"""
		param = Conversions.decimal_value_to_str(curr_acq_idx)
		self._core.io.write(f'ACQuire:HISTory:CURRent {param}')

	def get_tpacq(self) -> float:
		"""ACQuire:HISTory:TPACq \n
		Snippet: value: float = driver.acquire.history.get_tpacq() \n
		Sets the display time for one acquisition. The shorter the time, the faster the replay is. \n
			:return: time_per_acq: No help available
		"""
		response = self._core.io.query_str('ACQuire:HISTory:TPACq?')
		return Conversions.str_to_float(response)

	def set_tpacq(self, time_per_acq: float) -> None:
		"""ACQuire:HISTory:TPACq \n
		Snippet: driver.acquire.history.set_tpacq(time_per_acq = 1.0) \n
		Sets the display time for one acquisition. The shorter the time, the faster the replay is. \n
			:param time_per_acq: No help available
		"""
		param = Conversions.decimal_value_to_str(time_per_acq)
		self._core.io.write(f'ACQuire:HISTory:TPACq {param}')

	def get_state(self) -> bool:
		"""ACQuire:HISTory[:STATe] \n
		Snippet: value: bool = driver.acquire.history.get_state() \n
		Enables the history mode and allows you to save history waveforms to file. \n
			:return: state: No help available
		"""
		response = self._core.io.query_str('ACQuire:HISTory:STATe?')
		return Conversions.str_to_bool(response)

	def set_state(self, state: bool) -> None:
		"""ACQuire:HISTory[:STATe] \n
		Snippet: driver.acquire.history.set_state(state = False) \n
		Enables the history mode and allows you to save history waveforms to file. \n
			:param state: No help available
		"""
		param = Conversions.bool_to_str(state)
		self._core.io.write(f'ACQuire:HISTory:STATe {param}')

	def get_replay(self) -> bool:
		"""ACQuire:HISTory:REPLay \n
		Snippet: value: bool = driver.acquire.history.get_replay() \n
		If enabled, the replay of the history waveform sequence repeats automatically. Otherwise, the replay stops at the stop
		index set with method RsMxo.Acquire.History.stop. \n
			:return: auto_repeat: No help available
		"""
		response = self._core.io.query_str('ACQuire:HISTory:REPLay?')
		return Conversions.str_to_bool(response)

	def set_replay(self, auto_repeat: bool) -> None:
		"""ACQuire:HISTory:REPLay \n
		Snippet: driver.acquire.history.set_replay(auto_repeat = False) \n
		If enabled, the replay of the history waveform sequence repeats automatically. Otherwise, the replay stops at the stop
		index set with method RsMxo.Acquire.History.stop. \n
			:param auto_repeat: No help available
		"""
		param = Conversions.bool_to_str(auto_repeat)
		self._core.io.write(f'ACQuire:HISTory:REPLay {param}')

	def get_ts_date(self) -> str:
		"""ACQuire:HISTory:TSDate \n
		Snippet: value: str = driver.acquire.history.get_ts_date() \n
		Returns the date of the selected acquisition (method RsMxo.Acquire.History.current) . For automatic parsing of the time,
		use method RsMxo.Acquire.History.isoDate. \n
			:return: date_abs_string: String parameter with acquisition date
		"""
		response = self._core.io.query_str('ACQuire:HISTory:TSDate?')
		return trim_str_response(response)

	def get_ts_absolute(self) -> str:
		"""ACQuire:HISTory:TSABsolute \n
		Snippet: value: str = driver.acquire.history.get_ts_absolute() \n
		Returns the absolute daytime of the selected acquisition (method RsMxo.Acquire.History.current) . For automatic parsing
		of the time, use method RsMxo.Acquire.History.isoDate. \n
			:return: time_abs_string: String containing the time and unit
		"""
		response = self._core.io.query_str('ACQuire:HISTory:TSABsolute?')
		return trim_str_response(response)

	def get_ts_relative(self) -> float:
		"""ACQuire:HISTory:TSRelative \n
		Snippet: value: float = driver.acquire.history.get_ts_relative() \n
		Returns the relative time of the current acquisition - the time difference to the newest acquisition (index = 0) .
		See also: method RsMxo.Acquire.History.current. \n
			:return: time_relativ: No help available
		"""
		response = self._core.io.query_str('ACQuire:HISTory:TSRelative?')
		return Conversions.str_to_float(response)

	def get_tsr_reference(self) -> float:
		"""ACQuire:HISTory:TSRReference \n
		Snippet: value: float = driver.acquire.history.get_tsr_reference() \n
		Returns the relative time of the currently selected acquisition and the internal reference time (horizontal alignment) in
		history view in relation to the acquisition with index 0. \n
			:return: time_rel_int_ref: No help available
		"""
		response = self._core.io.query_str('ACQuire:HISTory:TSRReference?')
		return Conversions.str_to_float(response)

	def get_iso_date(self) -> str:
		"""ACQuire:HISTory:ISODate \n
		Snippet: value: str = driver.acquire.history.get_iso_date() \n
		Returns the absolute date and time of the acquisition that is selected in history view in ISO 8601 format.
		The same format is used in the header of exported waveform data files. See also: method RsMxo.Acquire.History.current) . \n
			:return: date_time_abs_string: String with absolute date and time in this order: year, month, day, hour, minutes, seconds, and milliseconds.
		"""
		response = self._core.io.query_str('ACQuire:HISTory:ISODate?')
		return trim_str_response(response)

	def clone(self) -> 'HistoryCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = HistoryCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
