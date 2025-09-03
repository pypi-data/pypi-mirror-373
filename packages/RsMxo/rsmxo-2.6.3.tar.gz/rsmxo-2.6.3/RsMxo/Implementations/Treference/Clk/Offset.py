from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OffsetCls:
	"""Offset commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("offset", core, parent)

	def set(self, offset: float, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:CLK:OFFSet \n
		Snippet: driver.treference.clk.offset.set(offset = 1.0, timingReference = repcap.TimingReference.Default) \n
		Sets the offset between the clock edge and the data edge if method RsMxo.Treference.TypePy.set is set. \n
			:param offset: No help available
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.decimal_value_to_str(offset)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:CLK:OFFSet {param}')

	def get(self, timingReference=repcap.TimingReference.Default) -> float:
		"""TREFerence<*>:CLK:OFFSet \n
		Snippet: value: float = driver.treference.clk.offset.get(timingReference = repcap.TimingReference.Default) \n
		Sets the offset between the clock edge and the data edge if method RsMxo.Treference.TypePy.set is set. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: offset: No help available"""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:CLK:OFFSet?')
		return Conversions.str_to_float(response)
