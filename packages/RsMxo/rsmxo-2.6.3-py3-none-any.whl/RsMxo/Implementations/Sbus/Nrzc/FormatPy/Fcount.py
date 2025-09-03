from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FcountCls:
	"""Fcount commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fcount", core, parent)

	def get(self, serialBus=repcap.SerialBus.Default) -> int:
		"""SBUS<*>:NRZC:FORMat:FCOunt \n
		Snippet: value: int = driver.sbus.nrzc.formatPy.fcount.get(serialBus = repcap.SerialBus.Default) \n
		Returns the number of frame format descriptions available for a specific custom protocol. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: count: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:NRZC:FORMat:FCOunt?')
		return Conversions.str_to_int(response)
