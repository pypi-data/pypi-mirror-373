from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DcycleCls:
	"""Dcycle commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dcycle", core, parent)

	def set(self, square_duty_cycle: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:MODulation:AM:DCYCle \n
		Snippet: driver.wgenerator.modulation.am.dcycle.set(square_duty_cycle = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the duty cycle for a square waveform. The duty cycle expresses for what percentage fraction of the period, the
		waveform is active, i.e. the signal state is high. \n
			:param square_duty_cycle: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(square_duty_cycle)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:MODulation:AM:DCYCle {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:MODulation:AM:DCYCle \n
		Snippet: value: float = driver.wgenerator.modulation.am.dcycle.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the duty cycle for a square waveform. The duty cycle expresses for what percentage fraction of the period, the
		waveform is active, i.e. the signal state is high. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: square_duty_cycle: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:MODulation:AM:DCYCle?')
		return Conversions.str_to_float(response)
