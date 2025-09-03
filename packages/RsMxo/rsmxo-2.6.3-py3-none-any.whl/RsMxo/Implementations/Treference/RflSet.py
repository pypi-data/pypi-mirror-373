from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RflSetCls:
	"""RflSet commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rflSet", core, parent)

	def set(self, ref_lev_set: float, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:RFLSet \n
		Snippet: driver.treference.rflSet.set(ref_lev_set = 1.0, timingReference = repcap.TimingReference.Default) \n
		Selects the set of reference levels that is used for the timing reference measurements. \n
			:param ref_lev_set: 1 to 8, index of the reference level set Number of the reference level set. Define the reference level set before you use it.
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.decimal_value_to_str(ref_lev_set)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:RFLSet {param}')

	def get(self, timingReference=repcap.TimingReference.Default) -> float:
		"""TREFerence<*>:RFLSet \n
		Snippet: value: float = driver.treference.rflSet.get(timingReference = repcap.TimingReference.Default) \n
		Selects the set of reference levels that is used for the timing reference measurements. \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: ref_lev_set: No help available"""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:RFLSet?')
		return Conversions.str_to_float(response)
