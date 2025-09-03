from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FranalysisCls:
	"""Franalysis commands group definition. 61 total commands, 14 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("franalysis", core, parent)

	@property
	def calibration(self):
		"""calibration commands group. 1 Sub-classes, 2 commands."""
		if not hasattr(self, '_calibration'):
			from .Calibration import CalibrationCls
			self._calibration = CalibrationCls(self._core, self._cmd_group)
		return self._calibration

	@property
	def hdefinition(self):
		"""hdefinition commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_hdefinition'):
			from .Hdefinition import HdefinitionCls
			self._hdefinition = HdefinitionCls(self._core, self._cmd_group)
		return self._hdefinition

	@property
	def generator(self):
		"""generator commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_generator'):
			from .Generator import GeneratorCls
			self._generator = GeneratorCls(self._core, self._cmd_group)
		return self._generator

	@property
	def amplitude(self):
		"""amplitude commands group. 1 Sub-classes, 4 commands."""
		if not hasattr(self, '_amplitude'):
			from .Amplitude import AmplitudeCls
			self._amplitude = AmplitudeCls(self._core, self._cmd_group)
		return self._amplitude

	@property
	def frequency(self):
		"""frequency commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_frequency'):
			from .Frequency import FrequencyCls
			self._frequency = FrequencyCls(self._core, self._cmd_group)
		return self._frequency

	@property
	def gain(self):
		"""gain commands group. 0 Sub-classes, 4 commands."""
		if not hasattr(self, '_gain'):
			from .Gain import GainCls
			self._gain = GainCls(self._core, self._cmd_group)
		return self._gain

	@property
	def inputPy(self):
		"""inputPy commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_inputPy'):
			from .InputPy import InputPyCls
			self._inputPy = InputPyCls(self._core, self._cmd_group)
		return self._inputPy

	@property
	def margin(self):
		"""margin commands group. 2 Sub-classes, 1 commands."""
		if not hasattr(self, '_margin'):
			from .Margin import MarginCls
			self._margin = MarginCls(self._core, self._cmd_group)
		return self._margin

	@property
	def marker(self):
		"""marker commands group. 7 Sub-classes, 0 commands."""
		if not hasattr(self, '_marker'):
			from .Marker import MarkerCls
			self._marker = MarkerCls(self._core, self._cmd_group)
		return self._marker

	@property
	def measurement(self):
		"""measurement commands group. 2 Sub-classes, 1 commands."""
		if not hasattr(self, '_measurement'):
			from .Measurement import MeasurementCls
			self._measurement = MeasurementCls(self._core, self._cmd_group)
		return self._measurement

	@property
	def output(self):
		"""output commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_output'):
			from .Output import OutputCls
			self._output = OutputCls(self._core, self._cmd_group)
		return self._output

	@property
	def phase(self):
		"""phase commands group. 0 Sub-classes, 5 commands."""
		if not hasattr(self, '_phase'):
			from .Phase import PhaseCls
			self._phase = PhaseCls(self._core, self._cmd_group)
		return self._phase

	@property
	def points(self):
		"""points commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_points'):
			from .Points import PointsCls
			self._points = PointsCls(self._core, self._cmd_group)
		return self._points

	@property
	def result(self):
		"""result commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_result'):
			from .Result import ResultCls
			self._result = ResultCls(self._core, self._cmd_group)
		return self._result

	def get_enable(self) -> bool:
		"""FRANalysis:ENABle \n
		Snippet: value: bool = driver.franalysis.get_enable() \n
		Enables the frequency response analysis application. If the frequency response analysis is disabled, the instrument does
		not accept any FRANalysis command. You can start the analysis with method RsMxo.Franalysis.state. \n
			:return: state: No help available
		"""
		response = self._core.io.query_str('FRANalysis:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, state: bool) -> None:
		"""FRANalysis:ENABle \n
		Snippet: driver.franalysis.set_enable(state = False) \n
		Enables the frequency response analysis application. If the frequency response analysis is disabled, the instrument does
		not accept any FRANalysis command. You can start the analysis with method RsMxo.Franalysis.state. \n
			:param state: No help available
		"""
		param = Conversions.bool_to_str(state)
		self._core.io.write(f'FRANalysis:ENABle {param}')

	def get_repeat(self) -> bool:
		"""FRANalysis:REPeat \n
		Snippet: value: bool = driver.franalysis.get_repeat() \n
		Repeats the measurement, using the same parameters. \n
			:return: repeat: No help available
		"""
		response = self._core.io.query_str('FRANalysis:REPeat?')
		return Conversions.str_to_bool(response)

	def set_repeat(self, repeat: bool) -> None:
		"""FRANalysis:REPeat \n
		Snippet: driver.franalysis.set_repeat(repeat = False) \n
		Repeats the measurement, using the same parameters. \n
			:param repeat: No help available
		"""
		param = Conversions.bool_to_str(repeat)
		self._core.io.write(f'FRANalysis:REPeat {param}')

	def reset(self) -> None:
		"""FRANalysis:RESet \n
		Snippet: driver.franalysis.reset() \n
		Resets the frequency response analysis. \n
		"""
		self._core.io.write(f'FRANalysis:RESet')

	def reset_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""FRANalysis:RESet \n
		Snippet: driver.franalysis.reset_and_wait() \n
		Resets the frequency response analysis. \n
		Same as reset, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'FRANalysis:RESet', opc_timeout_ms)

	# noinspection PyTypeChecker
	def get_state(self) -> enums.ProcessState:
		"""FRANalysis:STATe \n
		Snippet: value: enums.ProcessState = driver.franalysis.get_state() \n
		Starts the frequency response analysis. \n
			:return: value: No help available
		"""
		response = self._core.io.query_str('FRANalysis:STATe?')
		return Conversions.str_to_scalar_enum(response, enums.ProcessState)

	def set_state(self, value: enums.ProcessState) -> None:
		"""FRANalysis:STATe \n
		Snippet: driver.franalysis.set_state(value = enums.ProcessState.OFF) \n
		Starts the frequency response analysis. \n
			:param value: No help available
		"""
		param = Conversions.enum_scalar_to_str(value, enums.ProcessState)
		self._core.io.write(f'FRANalysis:STATe {param}')

	def get_auto_scale(self) -> bool:
		"""FRANalysis:AUToscale \n
		Snippet: value: bool = driver.franalysis.get_auto_scale() \n
		Enables the auto scaling function for each measurement. \n
			:return: auto_scale: No help available
		"""
		response = self._core.io.query_str('FRANalysis:AUToscale?')
		return Conversions.str_to_bool(response)

	def set_auto_scale(self, auto_scale: bool) -> None:
		"""FRANalysis:AUToscale \n
		Snippet: driver.franalysis.set_auto_scale(auto_scale = False) \n
		Enables the auto scaling function for each measurement. \n
			:param auto_scale: No help available
		"""
		param = Conversions.bool_to_str(auto_scale)
		self._core.io.write(f'FRANalysis:AUToscale {param}')

	def clone(self) -> 'FranalysisCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = FranalysisCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
