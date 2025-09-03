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

	def set(self, unit: enums.MagnitudeUnit, spectrum=repcap.Spectrum.Default) -> None:
		"""CALCulate:SPECtrum<*>:MAGNitude:SCALe \n
		Snippet: driver.calculate.spectrum.magnitude.scale.set(unit = enums.MagnitudeUnit.DB, spectrum = repcap.Spectrum.Default) \n
		Sets the unit for the y-axis. \n
			:param unit: No help available
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
		"""
		param = Conversions.enum_scalar_to_str(unit, enums.MagnitudeUnit)
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		self._core.io.write(f'CALCulate:SPECtrum{spectrum_cmd_val}:MAGNitude:SCALe {param}')

	# noinspection PyTypeChecker
	def get(self, spectrum=repcap.Spectrum.Default) -> enums.MagnitudeUnit:
		"""CALCulate:SPECtrum<*>:MAGNitude:SCALe \n
		Snippet: value: enums.MagnitudeUnit = driver.calculate.spectrum.magnitude.scale.get(spectrum = repcap.Spectrum.Default) \n
		Sets the unit for the y-axis. \n
			:param spectrum: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Spectrum')
			:return: unit: No help available"""
		spectrum_cmd_val = self._cmd_group.get_repcap_cmd_value(spectrum, repcap.Spectrum)
		response = self._core.io.query_str(f'CALCulate:SPECtrum{spectrum_cmd_val}:MAGNitude:SCALe?')
		return Conversions.str_to_scalar_enum(response, enums.MagnitudeUnit)
