from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DampingCls:
	"""Damping commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("damping", core, parent)

	def set(self, damping: float, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:CDR:SOFTware:PLL:DAMPing \n
		Snippet: driver.treference.cdr.software.pll.damping.set(damping = 1.0, timingReference = repcap.TimingReference.Default) \n
		Sets the damping factor, which is only relevant for second order PLL. \n
			:param damping: No help available
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.decimal_value_to_str(damping)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:PLL:DAMPing {param}')

	def get(self, timingReference=repcap.TimingReference.Default) -> float:
		"""TREFerence<*>:CDR:SOFTware:PLL:DAMPing \n
		Snippet: value: float = driver.treference.cdr.software.pll.damping.get(timingReference = repcap.TimingReference.Default) \n
		Sets the damping factor, which is only relevant for second order PLL. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: damping: No help available"""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:PLL:DAMPing?')
		return Conversions.str_to_float(response)
