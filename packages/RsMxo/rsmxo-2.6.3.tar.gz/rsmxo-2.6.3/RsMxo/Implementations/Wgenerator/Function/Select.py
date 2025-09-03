from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SelectCls:
	"""Select commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("select", core, parent)

	def set(self, function_type: enums.WgenFunctionType, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:FUNCtion[:SELect] \n
		Snippet: driver.wgenerator.function.select.set(function_type = enums.WgenFunctionType.ARBitrary, waveformGen = repcap.WaveformGen.Default) \n
		Selects the type of waveform to be generated. \n
			:param function_type: SINC: cardinal sine HAVer: haversine (great-circle distance between two points on a sphere)
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.enum_scalar_to_str(function_type, enums.WgenFunctionType)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:FUNCtion:SELect {param}')

	# noinspection PyTypeChecker
	def get(self, waveformGen=repcap.WaveformGen.Default) -> enums.WgenFunctionType:
		"""WGENerator<*>:FUNCtion[:SELect] \n
		Snippet: value: enums.WgenFunctionType = driver.wgenerator.function.select.get(waveformGen = repcap.WaveformGen.Default) \n
		Selects the type of waveform to be generated. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: function_type: SINC: cardinal sine HAVer: haversine (great-circle distance between two points on a sphere)"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:FUNCtion:SELect?')
		return Conversions.str_to_scalar_enum(response, enums.WgenFunctionType)
