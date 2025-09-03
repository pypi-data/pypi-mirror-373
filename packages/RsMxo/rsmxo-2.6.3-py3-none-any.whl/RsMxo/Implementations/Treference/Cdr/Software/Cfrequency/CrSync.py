from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class CrSyncCls:
	"""CrSync commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("crSync", core, parent)

	def set(self, clock_resync: bool, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:CDR:SOFTware:CFRequency:CRSYnc \n
		Snippet: driver.treference.cdr.software.cfrequency.crSync.set(clock_resync = False, timingReference = repcap.TimingReference.Default) \n
		Enables continuous synchronization of the clock with the data signal. \n
			:param clock_resync: No help available
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.bool_to_str(clock_resync)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:CFRequency:CRSYnc {param}')

	def get(self, timingReference=repcap.TimingReference.Default) -> bool:
		"""TREFerence<*>:CDR:SOFTware:CFRequency:CRSYnc \n
		Snippet: value: bool = driver.treference.cdr.software.cfrequency.crSync.get(timingReference = repcap.TimingReference.Default) \n
		Enables continuous synchronization of the clock with the data signal. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: clock_resync: No help available"""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:CFRequency:CRSYnc?')
		return Conversions.str_to_bool(response)
