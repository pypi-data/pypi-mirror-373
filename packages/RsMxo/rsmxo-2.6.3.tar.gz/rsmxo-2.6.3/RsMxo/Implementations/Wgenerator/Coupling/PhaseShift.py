from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PhaseShiftCls:
	"""PhaseShift commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("phaseShift", core, parent)

	def set(self, phase_shift: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:COUPling:PHASeshift \n
		Snippet: driver.wgenerator.coupling.phaseShift.set(phase_shift = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the phase shift between the waveform of Gen1 and Gen2 when the frequency parameters of the two waveforms are coupled. \n
			:param phase_shift: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(phase_shift)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:COUPling:PHASeshift {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:COUPling:PHASeshift \n
		Snippet: value: float = driver.wgenerator.coupling.phaseShift.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the phase shift between the waveform of Gen1 and Gen2 when the frequency parameters of the two waveforms are coupled. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: phase_shift: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:COUPling:PHASeshift?')
		return Conversions.str_to_float(response)
