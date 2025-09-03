from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AmplitudeCls:
	"""Amplitude commands group definition. 11 total commands, 1 Subgroups, 4 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("amplitude", core, parent)

	@property
	def profile(self):
		"""profile commands group. 3 Sub-classes, 2 commands."""
		if not hasattr(self, '_profile'):
			from .Profile import ProfileCls
			self._profile = ProfileCls(self._core, self._cmd_group)
		return self._profile

	def get_enable(self) -> bool:
		"""FRANalysis:AMPLitude:ENABle \n
		Snippet: value: bool = driver.franalysis.amplitude.get_enable() \n
		Enables the amplitude signal for the frequency response analysis. You can then define the amplitude profile of the signal. \n
			:return: state: No help available
		"""
		response = self._core.io.query_str('FRANalysis:AMPLitude:ENABle?')
		return Conversions.str_to_bool(response)

	def set_enable(self, state: bool) -> None:
		"""FRANalysis:AMPLitude:ENABle \n
		Snippet: driver.franalysis.amplitude.set_enable(state = False) \n
		Enables the amplitude signal for the frequency response analysis. You can then define the amplitude profile of the signal. \n
			:param state: No help available
		"""
		param = Conversions.bool_to_str(state)
		self._core.io.write(f'FRANalysis:AMPLitude:ENABle {param}')

	# noinspection PyTypeChecker
	def get_mode(self) -> enums.AmplitudeMode:
		"""FRANalysis:AMPLitude:MODE \n
		Snippet: value: enums.AmplitudeMode = driver.franalysis.amplitude.get_mode() \n
		Selects, if the amplitude is a constant value (method RsMxo.Franalysis.Generator.amplitude) or is defined as an amplitude
		profile. \n
			:return: amplitude_mode: No help available
		"""
		response = self._core.io.query_str('FRANalysis:AMPLitude:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.AmplitudeMode)

	def set_mode(self, amplitude_mode: enums.AmplitudeMode) -> None:
		"""FRANalysis:AMPLitude:MODE \n
		Snippet: driver.franalysis.amplitude.set_mode(amplitude_mode = enums.AmplitudeMode.CONStant) \n
		Selects, if the amplitude is a constant value (method RsMxo.Franalysis.Generator.amplitude) or is defined as an amplitude
		profile. \n
			:param amplitude_mode: No help available
		"""
		param = Conversions.enum_scalar_to_str(amplitude_mode, enums.AmplitudeMode)
		self._core.io.write(f'FRANalysis:AMPLitude:MODE {param}')

	def get_offset(self) -> float:
		"""FRANalysis:AMPLitude:OFFSet \n
		Snippet: value: float = driver.franalysis.amplitude.get_offset() \n
		Sets a vertical offset of the amplitude waveform. \n
			:return: vertical_offset: No help available
		"""
		response = self._core.io.query_str('FRANalysis:AMPLitude:OFFSet?')
		return Conversions.str_to_float(response)

	def set_offset(self, vertical_offset: float) -> None:
		"""FRANalysis:AMPLitude:OFFSet \n
		Snippet: driver.franalysis.amplitude.set_offset(vertical_offset = 1.0) \n
		Sets a vertical offset of the amplitude waveform. \n
			:param vertical_offset: No help available
		"""
		param = Conversions.decimal_value_to_str(vertical_offset)
		self._core.io.write(f'FRANalysis:AMPLitude:OFFSet {param}')

	def get_scale(self) -> float:
		"""FRANalysis:AMPLitude:SCALe \n
		Snippet: value: float = driver.franalysis.amplitude.get_scale() \n
		Sets the vertical scale for the amplitude waveform. \n
			:return: vertical_scale: No help available
		"""
		response = self._core.io.query_str('FRANalysis:AMPLitude:SCALe?')
		return Conversions.str_to_float(response)

	def set_scale(self, vertical_scale: float) -> None:
		"""FRANalysis:AMPLitude:SCALe \n
		Snippet: driver.franalysis.amplitude.set_scale(vertical_scale = 1.0) \n
		Sets the vertical scale for the amplitude waveform. \n
			:param vertical_scale: No help available
		"""
		param = Conversions.decimal_value_to_str(vertical_scale)
		self._core.io.write(f'FRANalysis:AMPLitude:SCALe {param}')

	def clone(self) -> 'AmplitudeCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = AmplitudeCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
