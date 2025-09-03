from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AcquireCls:
	"""Acquire commands group definition. 37 total commands, 5 Subgroups, 12 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("acquire", core, parent)

	@property
	def rollMode(self):
		"""rollMode commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_rollMode'):
			from .RollMode import RollModeCls
			self._rollMode = RollModeCls(self._core, self._cmd_group)
		return self._rollMode

	@property
	def history(self):
		"""history commands group. 1 Sub-classes, 11 commands."""
		if not hasattr(self, '_history'):
			from .History import HistoryCls
			self._history = HistoryCls(self._core, self._cmd_group)
		return self._history

	@property
	def symbolRate(self):
		"""symbolRate commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_symbolRate'):
			from .SymbolRate import SymbolRateCls
			self._symbolRate = SymbolRateCls(self._core, self._cmd_group)
		return self._symbolRate

	@property
	def points(self):
		"""points commands group. 0 Sub-classes, 5 commands."""
		if not hasattr(self, '_points'):
			from .Points import PointsCls
			self._points = PointsCls(self._core, self._cmd_group)
		return self._points

	@property
	def segmented(self):
		"""segmented commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_segmented'):
			from .Segmented import SegmentedCls
			self._segmented = SegmentedCls(self._core, self._cmd_group)
		return self._segmented

	def get_available(self) -> int:
		"""ACQuire:AVAilable \n
		Snippet: value: int = driver.acquire.get_available() \n
		Number of acquisitions that is saved in the memory and available for history viewing. It is also the number of
		acquisitions in a fast segmentation acquisition series. \n
			:return: acq_cnt: No help available
		"""
		response = self._core.io.query_str('ACQuire:AVAilable?')
		return Conversions.str_to_int(response)

	def get_count(self) -> int:
		"""ACQuire:COUNt \n
		Snippet: value: int = driver.acquire.get_count() \n
			INTRO_CMD_HELP: Sets the acquisition and average count, which has a double effect: \n
			- It sets the number of waveforms acquired with method RsMxo.Run.single.
			- It defines the number of waveforms used to calculate the average waveform.  \n
			:return: max_acq_cnt: No help available
		"""
		response = self._core.io.query_str('ACQuire:COUNt?')
		return Conversions.str_to_int(response)

	def set_count(self, max_acq_cnt: int) -> None:
		"""ACQuire:COUNt \n
		Snippet: driver.acquire.set_count(max_acq_cnt = 1) \n
			INTRO_CMD_HELP: Sets the acquisition and average count, which has a double effect: \n
			- It sets the number of waveforms acquired with method RsMxo.Run.single.
			- It defines the number of waveforms used to calculate the average waveform.  \n
			:param max_acq_cnt: No help available
		"""
		param = Conversions.decimal_value_to_str(max_acq_cnt)
		self._core.io.write(f'ACQuire:COUNt {param}')

	def get_current(self) -> int:
		"""ACQuire:CURRent \n
		Snippet: value: int = driver.acquire.get_current() \n
		Returns the current number of acquisitions that have been acquired. \n
			:return: curr_acq_cnt: No help available
		"""
		response = self._core.io.query_str('ACQuire:CURRent?')
		return Conversions.str_to_int(response)

	def get_average(self) -> int:
		"""ACQuire:AVERage \n
		Snippet: value: int = driver.acquire.get_average() \n
		Returns the current number of acquired waveforms that contribute to the average. \n
			:return: curr_avg_cnt: No help available
		"""
		response = self._core.io.query_str('ACQuire:AVERage?')
		return Conversions.str_to_int(response)

	# noinspection PyTypeChecker
	def get_interpolate(self) -> enums.IntpolMd:
		"""ACQuire:INTerpolate \n
		Snippet: value: enums.IntpolMd = driver.acquire.get_interpolate() \n
		Selects the interpolation method. \n
			:return: intpol_md:
				- LINear: Linear interpolation between two adjacent sample points
				- SINX: Interpolation with a sin(x) /x function.
				- SMHD: Sample/Hold causes a histogram-like interpolation."""
		response = self._core.io.query_str('ACQuire:INTerpolate?')
		return Conversions.str_to_scalar_enum(response, enums.IntpolMd)

	def set_interpolate(self, intpol_md: enums.IntpolMd) -> None:
		"""ACQuire:INTerpolate \n
		Snippet: driver.acquire.set_interpolate(intpol_md = enums.IntpolMd.LINear) \n
		Selects the interpolation method. \n
			:param intpol_md:
				- LINear: Linear interpolation between two adjacent sample points
				- SINX: Interpolation with a sin(x) /x function.
				- SMHD: Sample/Hold causes a histogram-like interpolation."""
		param = Conversions.enum_scalar_to_str(intpol_md, enums.IntpolMd)
		self._core.io.write(f'ACQuire:INTerpolate {param}')

	# noinspection PyTypeChecker
	def get_type_py(self) -> enums.AcqMd:
		"""ACQuire:TYPE \n
		Snippet: value: enums.AcqMd = driver.acquire.get_type_py() \n
		Sets how the waveform is built from the captured samples. \n
			:return: acq_md: No help available
		"""
		response = self._core.io.query_str('ACQuire:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.AcqMd)

	def set_type_py(self, acq_md: enums.AcqMd) -> None:
		"""ACQuire:TYPE \n
		Snippet: driver.acquire.set_type_py(acq_md = enums.AcqMd.AVERage) \n
		Sets how the waveform is built from the captured samples. \n
			:param acq_md: No help available
		"""
		param = Conversions.enum_scalar_to_str(acq_md, enums.AcqMd)
		self._core.io.write(f'ACQuire:TYPE {param}')

	def get_resolution(self) -> float:
		"""ACQuire:RESolution \n
		Snippet: value: float = driver.acquire.get_resolution() \n
		Returns the current resolution. The resolution is the time between two waveform samples in the waveform record.
		It considers the processing of the captured samples including interpolation. A fine resolution with low values produces a
		more precise waveform record. The resolution is the reciprocal of the sample rate. You can query the minimum and maximum
		values with <command>? MIN and <command>? MAX. \n
			:return: resolution: No help available
		"""
		response = self._core.io.query_str('ACQuire:RESolution?')
		return Conversions.str_to_float(response)

	def set_resolution(self, resolution: float) -> None:
		"""ACQuire:RESolution \n
		Snippet: driver.acquire.set_resolution(resolution = 1.0) \n
		Returns the current resolution. The resolution is the time between two waveform samples in the waveform record.
		It considers the processing of the captured samples including interpolation. A fine resolution with low values produces a
		more precise waveform record. The resolution is the reciprocal of the sample rate. You can query the minimum and maximum
		values with <command>? MIN and <command>? MAX. \n
			:param resolution: No help available
		"""
		param = Conversions.decimal_value_to_str(resolution)
		self._core.io.write(f'ACQuire:RESolution {param}')

	def get_dresolution(self) -> float:
		"""ACQuire:DRESolution \n
		Snippet: value: float = driver.acquire.get_dresolution() \n
		Returns the current digital resolution of the digital channels. \n
			:return: dig_res: No help available
		"""
		response = self._core.io.query_str('ACQuire:DRESolution?')
		return Conversions.str_to_float(response)

	def get_zresolution(self) -> float:
		"""ACQuire:ZRESolution \n
		Snippet: value: float = driver.acquire.get_zresolution() \n
		No command help available \n
			:return: zui_resolution: No help available
		"""
		response = self._core.io.query_str('ACQuire:ZRESolution?')
		return Conversions.str_to_float(response)

	def get_sr_real(self) -> float:
		"""ACQuire:SRReal \n
		Snippet: value: float = driver.acquire.get_sr_real() \n
		Returns the sample rate of the waveform after HW processing. Interpolation is not considered. This value is shown in the
		acquisition label above the diagram. You can query the minimum and maximum values with <command>? MIN and <command>? MAX. \n
			:return: hw_sample_rate: No help available
		"""
		response = self._core.io.query_str('ACQuire:SRReal?')
		return Conversions.str_to_float(response)

	def set_sr_real(self, hw_sample_rate: float) -> None:
		"""ACQuire:SRReal \n
		Snippet: driver.acquire.set_sr_real(hw_sample_rate = 1.0) \n
		Returns the sample rate of the waveform after HW processing. Interpolation is not considered. This value is shown in the
		acquisition label above the diagram. You can query the minimum and maximum values with <command>? MIN and <command>? MAX. \n
			:param hw_sample_rate: No help available
		"""
		param = Conversions.decimal_value_to_str(hw_sample_rate)
		self._core.io.write(f'ACQuire:SRReal {param}')

	def get_rl_real(self) -> int:
		"""ACQuire:RLReal \n
		Snippet: value: int = driver.acquire.get_rl_real() \n
		Returns the internal record length used by the acquisition system. \n
			:return: hw_record_len: No help available
		"""
		response = self._core.io.query_str('ACQuire:RLReal?')
		return Conversions.str_to_int(response)

	def get_po_memory(self) -> bool:
		"""ACQuire:POMemory \n
		Snippet: value: bool = driver.acquire.get_po_memory() \n
		The command returns 1 if the memory is not sufficient to process the data with the current settings. To solve the problem,
		reduce the record length or use automatic record length setting. \n
			:return: processing_out_of_memory: No help available
		"""
		response = self._core.io.query_str('ACQuire:POMemory?')
		return Conversions.str_to_bool(response)

	def clone(self) -> 'AcquireCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = AcquireCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
