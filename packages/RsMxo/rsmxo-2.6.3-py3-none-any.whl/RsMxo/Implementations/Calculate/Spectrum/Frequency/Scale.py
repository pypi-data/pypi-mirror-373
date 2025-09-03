from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ScaleCls:
	"""Scale commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("scale", core, parent)

	def set(self, xaxis_mode: enums.AxisMode, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:FREQuency:SCALe \n
		Snippet: driver.calculate.spectrum.frequency.scale.set(xaxis_mode = enums.AxisMode.LIN, spectrum = repcap.Spectrum.Default) \n
		Defines the scaling method for the frequency axis (x-axis) of the spectrogram. \n
			:param xaxis_mode: LIN: linear scaling LOG: logarithmic scaling
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.enum_scalar_to_str(xaxis_mode, enums.AxisMode)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:FREQuency:SCALe {param}')

	# noinspection PyTypeChecker
	def get(self, spectrum=repcap.Spectrum.Default) -> enums.AxisMode:
		"""CALCulate:SPECtrum<*>:FREQuency:SCALe \n
		Snippet: value: enums.AxisMode = driver.calculate.spectrum.frequency.scale.get(spectrum = repcap.Spectrum.Default) \n
		Defines the scaling method for the frequency axis (x-axis) of the spectrogram. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: xaxis_mode: LIN: linear scaling LOG: logarithmic scaling"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:FREQuency:SCALe?')
		return Conversions.str_to_scalar_enum(response, enums.AxisMode)
