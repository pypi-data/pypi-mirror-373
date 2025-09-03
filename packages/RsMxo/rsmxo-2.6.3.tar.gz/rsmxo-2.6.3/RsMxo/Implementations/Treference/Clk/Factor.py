from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FactorCls:
	"""Factor commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("factor", core, parent)

	def set(self, multiplier: int, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:CLK:FACTor \n
		Snippet: driver.treference.clk.factor.set(multiplier = 1, timingReference = repcap.TimingReference.Default) \n
		Sets a value for the clock multiplier if method RsMxo.Treference.TypePy.set is set. The muliplier is the ratio of an
		internal clock rate to the externally supplied clock. It defines the number of samples per clock interval. \n
			:param multiplier: No help available
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.decimal_value_to_str(multiplier)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:CLK:FACTor {param}')

	def get(self, timingReference=repcap.TimingReference.Default) -> int:
		"""TREFerence<*>:CLK:FACTor \n
		Snippet: value: int = driver.treference.clk.factor.get(timingReference = repcap.TimingReference.Default) \n
		Sets a value for the clock multiplier if method RsMxo.Treference.TypePy.set is set. The muliplier is the ratio of an
		internal clock rate to the externally supplied clock. It defines the number of samples per clock interval. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: multiplier: No help available"""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:CLK:FACTor?')
		return Conversions.str_to_int(response)
