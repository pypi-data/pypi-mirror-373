from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FunctionCls:
	"""Function commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("function", core, parent)

	def set(self, signal_type: enums.WgenSignalType, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:MODulation:AM[:FUNCtion] \n
		Snippet: driver.wgenerator.modulation.am.function.set(signal_type = enums.WgenSignalType.RAMP, waveformGen = repcap.WaveformGen.Default) \n
		Selects the type of the modulating signal for AM modulation. \n
			:param signal_type: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.enum_scalar_to_str(signal_type, enums.WgenSignalType)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:MODulation:AM:FUNCtion {param}')

	# noinspection PyTypeChecker
	def get(self, waveformGen=repcap.WaveformGen.Default) -> enums.WgenSignalType:
		"""WGENerator<*>:MODulation:AM[:FUNCtion] \n
		Snippet: value: enums.WgenSignalType = driver.wgenerator.modulation.am.function.get(waveformGen = repcap.WaveformGen.Default) \n
		Selects the type of the modulating signal for AM modulation. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: signal_type: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:MODulation:AM:FUNCtion?')
		return Conversions.str_to_scalar_enum(response, enums.WgenSignalType)
