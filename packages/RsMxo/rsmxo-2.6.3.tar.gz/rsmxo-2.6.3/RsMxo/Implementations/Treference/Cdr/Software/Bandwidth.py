from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BandwidthCls:
	"""Bandwidth commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("bandwidth", core, parent)

	def set(self, bandwidth: float, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:CDR:SOFTware:BWIDth \n
		Snippet: driver.treference.cdr.software.bandwidth.set(bandwidth = 1.0, timingReference = repcap.TimingReference.Default) \n
		Sets the PLL bandwidth. It defines the part of the spectrum that the PLL can follow during synchronization. \n
			:param bandwidth: No help available
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.decimal_value_to_str(bandwidth)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:BWIDth {param}')

	def get(self, timingReference=repcap.TimingReference.Default) -> float:
		"""TREFerence<*>:CDR:SOFTware:BWIDth \n
		Snippet: value: float = driver.treference.cdr.software.bandwidth.get(timingReference = repcap.TimingReference.Default) \n
		Sets the PLL bandwidth. It defines the part of the spectrum that the PLL can follow during synchronization. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: bandwidth: No help available"""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:BWIDth?')
		return Conversions.str_to_float(response)
