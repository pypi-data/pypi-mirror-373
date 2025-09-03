from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SelResultsCls:
	"""SelResults commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("selResults", core, parent)

	def set(self, results: enums.SelResults, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:CDR:SOFTware:SELResults \n
		Snippet: driver.treference.cdr.software.selResults.set(results = enums.SelResults.AISYnc, timingReference = repcap.TimingReference.Default) \n
		Selects when the CDR algorithm returns clock edges. \n
			:param results: ALL: all clock edges are used. AISYnc: the clock edges of the synchronization time are discarded; results are gathered after initial synchronization of the CDR.
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.enum_scalar_to_str(results, enums.SelResults)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:SELResults {param}')

	# noinspection PyTypeChecker
	def get(self, timingReference=repcap.TimingReference.Default) -> enums.SelResults:
		"""TREFerence<*>:CDR:SOFTware:SELResults \n
		Snippet: value: enums.SelResults = driver.treference.cdr.software.selResults.get(timingReference = repcap.TimingReference.Default) \n
		Selects when the CDR algorithm returns clock edges. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: results: ALL: all clock edges are used. AISYnc: the clock edges of the synchronization time are discarded; results are gathered after initial synchronization of the CDR."""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:CDR:SOFTware:SELResults?')
		return Conversions.str_to_scalar_enum(response, enums.SelResults)
