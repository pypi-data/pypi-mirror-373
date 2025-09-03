from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PeriodCls:
	"""Period commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("period", core, parent)

	def set(self, period: float, waveformGen=repcap.WaveformGen.Default) -> None:
		"""WGENerator<*>:PERiod \n
		Snippet: driver.wgenerator.period.set(period = 1.0, waveformGen = repcap.WaveformGen.Default) \n
		Sets the period of the pulse waveform, if method RsMxo.Wgenerator.Function.Select.set is set to PULSe. \n
			:param period: No help available
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
		"""
		param = Conversions.decimal_value_to_str(period)
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		self._core.io.write(f'WGENerator{waveformGen_cmd_val}:PERiod {param}')

	def get(self, waveformGen=repcap.WaveformGen.Default) -> float:
		"""WGENerator<*>:PERiod \n
		Snippet: value: float = driver.wgenerator.period.get(waveformGen = repcap.WaveformGen.Default) \n
		Sets the period of the pulse waveform, if method RsMxo.Wgenerator.Function.Select.set is set to PULSe. \n
			:param waveformGen: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Wgenerator')
			:return: period: No help available"""
		waveformGen_cmd_val = self._cmd_group.get_repcap_cmd_value(waveformGen, repcap.WaveformGen)
		response = self._core.io.query_str(f'WGENerator{waveformGen_cmd_val}:PERiod?')
		return Conversions.str_to_float(response)
