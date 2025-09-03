from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ZcouplingCls:
	"""Zcoupling commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("zcoupling", core, parent)

	def set(self, zoom_coupling: bool, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:ZCOupling \n
		Snippet: driver.sbus.zcoupling.set(zoom_coupling = False, serialBus = repcap.SerialBus.Default) \n
		If enabled, the protocol decode zoom and result table are synchronized. \n
			:param zoom_coupling: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.bool_to_str(zoom_coupling)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:ZCOupling {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> bool:
		"""SBUS<*>:ZCOupling \n
		Snippet: value: bool = driver.sbus.zcoupling.get(serialBus = repcap.SerialBus.Default) \n
		If enabled, the protocol decode zoom and result table are synchronized. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: zoom_coupling: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:ZCOupling?')
		return Conversions.str_to_bool(response)
