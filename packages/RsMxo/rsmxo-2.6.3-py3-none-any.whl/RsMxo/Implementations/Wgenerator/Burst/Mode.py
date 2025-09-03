from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ModeCls:
	"""Mode commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("mode", core, parent)

	def set(self, run_mode: enums.WgenRunMode, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:BURSt:MODE \n
		Snippet: driver.wgenerator.burst.mode.set(run_mode = enums.WgenRunMode.REPetitive, waveformGen = repcap.WaveformGen.Default) \n
		No command help available \n
			:param run_mode: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.enum_scalar_to_str(run_mode, enums.WgenRunMode)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:BURSt:MODE {param}')

	# noinspection PyTypeChecker
	def get(self, waveformGen=repcap.WaveformGen.Default) -> enums.WgenRunMode:
		"""WGENerator<*>:BURSt:MODE \n
		Snippet: value: enums.WgenRunMode = driver.wgenerator.burst.mode.get(waveformGen = repcap.WaveformGen.Default) \n
		No command help available \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: run_mode: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:BURSt:MODE?')
		return Conversions.str_to_scalar_enum(response, enums.WgenRunMode)
