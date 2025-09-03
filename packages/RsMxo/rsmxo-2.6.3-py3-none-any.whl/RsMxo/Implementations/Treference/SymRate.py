from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SymRateCls:
	"""SymRate commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("symRate", core, parent)

	def set(self, symbol_rate: float, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:SYMRate \n
		Snippet: driver.treference.symRate.set(symbol_rate = 1.0, timingReference = repcap.TimingReference.Default) \n
		Sets the symbol rate of the data signal for the indicated timing reference. \n
			:param symbol_rate: No help available
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.decimal_value_to_str(symbol_rate)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:SYMRate {param}')

	def get(self, timingReference=repcap.TimingReference.Default) -> float:
		"""TREFerence<*>:SYMRate \n
		Snippet: value: float = driver.treference.symRate.get(timingReference = repcap.TimingReference.Default) \n
		Sets the symbol rate of the data signal for the indicated timing reference. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: symbol_rate: No help available"""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:SYMRate?')
		return Conversions.str_to_float(response)
