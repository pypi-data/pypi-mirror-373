from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SourceCls:
	"""Source commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("source", core, parent)

	def set(self, operation_mode: enums.WgenOperationMode, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:SOURce \n
		Snippet: driver.wgenerator.source.set(operation_mode = enums.WgenOperationMode.ARBGenerator, waveformGen = repcap.WaveformGen.Default) \n
		Selects the operation mode of the waveform generator- \n
			:param operation_mode:
				- FUNCgen: Enables the function generator and disables modulation, sweep, and arbitrary waveforms
				- MODulation: Enables the modulation, disables sweep and selects the sine function.
				- SWEep: Enables the sweep, disables modulation, and selects the sine function.
				- ARBGenerator: Selects the arbitrary function and disables modulation and sweep.
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')"""
		param = Conversions.enum_scalar_to_str(operation_mode, enums.WgenOperationMode)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:SOURce {param}')

	# noinspection PyTypeChecker
	def get(self, waveformGen=repcap.WaveformGen.Default) -> enums.WgenOperationMode:
		"""WGENerator<*>:SOURce \n
		Snippet: value: enums.WgenOperationMode = driver.wgenerator.source.get(waveformGen = repcap.WaveformGen.Default) \n
		Selects the operation mode of the waveform generator- \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: operation_mode:
				- FUNCgen: Enables the function generator and disables modulation, sweep, and arbitrary waveforms
				- MODulation: Enables the modulation, disables sweep and selects the sine function.
				- SWEep: Enables the sweep, disables modulation, and selects the sine function.
				- ARBGenerator: Selects the arbitrary function and disables modulation and sweep."""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:SOURce?')
		return Conversions.str_to_scalar_enum(response, enums.WgenOperationMode)
