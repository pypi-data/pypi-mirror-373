from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RelBwidthCls:
	"""RelBwidth commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("relBwidth", core, parent)

	def set(self, rel_bw: float, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:CDR:SOFTware:RELBwidth \n
		Snippet: driver.treference.cdr.software.relBwidth.set(rel_bw = 1.0, timingReference = repcap.TimingReference.Default) \n
		Sets the relative bandwidth, that is the ratio of the nominal bit rate to the PLL bandwidth. \n
			:param rel_bw: No help available
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.decimal_value_to_str(rel_bw)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:RELBwidth {param}')

	def get(self, timingReference=repcap.TimingReference.Default) -> float:
		"""TREFerence<*>:CDR:SOFTware:RELBwidth \n
		Snippet: value: float = driver.treference.cdr.software.relBwidth.get(timingReference = repcap.TimingReference.Default) \n
		Sets the relative bandwidth, that is the ratio of the nominal bit rate to the PLL bandwidth. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: rel_bw: No help available"""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:RELBwidth?')
		return Conversions.str_to_float(response)
