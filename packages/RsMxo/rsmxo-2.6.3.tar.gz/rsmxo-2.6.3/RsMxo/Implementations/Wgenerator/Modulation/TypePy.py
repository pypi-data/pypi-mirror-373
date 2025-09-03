from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TypePyCls:
	"""TypePy commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("typePy", core, parent)

	def set(self, modulation_type: enums.ModulationType, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:MODulation:TYPE \n
		Snippet: driver.wgenerator.modulation.typePy.set(modulation_type = enums.ModulationType.AM, waveformGen = repcap.WaveformGen.Default) \n
		Selects the modulation type, which defines how the carrier signal is modified. \n
			:param modulation_type: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.enum_scalar_to_str(modulation_type, enums.ModulationType)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:MODulation:TYPE {param}')

	# noinspection PyTypeChecker
	def get(self, waveformGen=repcap.WaveformGen.Default) -> enums.ModulationType:
		"""WGENerator<*>:MODulation:TYPE \n
		Snippet: value: enums.ModulationType = driver.wgenerator.modulation.typePy.get(waveformGen = repcap.WaveformGen.Default) \n
		Selects the modulation type, which defines how the carrier signal is modified. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: modulation_type: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:MODulation:TYPE?')
		return Conversions.str_to_scalar_enum(response, enums.ModulationType)
