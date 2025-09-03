from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class EnableCls:
	"""Enable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("enable", core, parent)

	def set(self, first: bool, timingReference=repcap.TimingReference.Default) -> None:
		"""TREFerence<*>:ENABle \n
		Snippet: driver.treference.enable.set(first = False, timingReference = repcap.TimingReference.Default) \n
		Adds the indicated timing reference (ON) or removes it (OFF) . \n
			:param first: No help available
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
		"""
		param = Conversions.bool_to_str(first)
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		self._core.io.write(f'TREFerence{timingReference_cmd_val}:ENABle {param}')

	def get(self, timingReference=repcap.TimingReference.Default) -> bool:
		"""TREFerence<*>:ENABle \n
		Snippet: value: bool = driver.treference.enable.get(timingReference = repcap.TimingReference.Default) \n
		Adds the indicated timing reference (ON) or removes it (OFF) . \n
			:param timingReference: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Treference')
			:return: first: No help available"""
		timingReference_cmd_val = self._cmd_group.get_repcap_cmd_value(timingReference, repcap.TimingReference)
		response = self._core.io.query_str(f'TREFerence{timingReference_cmd_val}:ENABle?')
		return Conversions.str_to_bool(response)
