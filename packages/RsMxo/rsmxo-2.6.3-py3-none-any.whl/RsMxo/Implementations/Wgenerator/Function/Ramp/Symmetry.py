from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SymmetryCls:
	"""Symmetry commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("symmetry", core, parent)

	def set(self, ramp_symmetry: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:FUNCtion:RAMP[:SYMMetry] \n
		Snippet: driver.wgenerator.function.ramp.symmetry.set(ramp_symmetry = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the symmetry of a ramp waveform, the percentage of time the waveform is rising. By changing the symmetry of the ramp,
		you can create, for example, triangular waveforms. \n
			:param ramp_symmetry: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(ramp_symmetry)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:FUNCtion:RAMP:SYMMetry {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:FUNCtion:RAMP[:SYMMetry] \n
		Snippet: value: float = driver.wgenerator.function.ramp.symmetry.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the symmetry of a ramp waveform, the percentage of time the waveform is rising. By changing the symmetry of the ramp,
		you can create, for example, triangular waveforms. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: ramp_symmetry: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:FUNCtion:RAMP:SYMMetry?')
		return Conversions.str_to_float(response)
