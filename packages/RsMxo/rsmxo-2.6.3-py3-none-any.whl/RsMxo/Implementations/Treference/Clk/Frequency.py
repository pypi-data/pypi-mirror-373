from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrequencyCls:
	"""Frequency commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("frequency", core, parent)

	def set(self, frequency: float, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:CLK:FREQuency \n
		Snippet: driver.treference.clk.frequency.set(frequency = 1.0, timingReference = repcap.TimingReference.Default) \n
		Sets the frequency of the clock signal if method RsMxo.Treference.TypePy.set is set. \n
			:param frequency: No help available
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.decimal_value_to_str(frequency)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:CLK:FREQuency {param}')

	def get(self, timingReference=repcap.TimingReference.Default) -> float:
		"""TREFerence<*>:CLK:FREQuency \n
		Snippet: value: float = driver.treference.clk.frequency.get(timingReference = repcap.TimingReference.Default) \n
		Sets the frequency of the clock signal if method RsMxo.Treference.TypePy.set is set. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: frequency: No help available"""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:CLK:FREQuency?')
		return Conversions.str_to_float(response)
