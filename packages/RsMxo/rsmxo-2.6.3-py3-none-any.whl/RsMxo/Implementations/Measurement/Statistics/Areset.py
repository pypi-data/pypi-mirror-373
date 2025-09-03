from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AresetCls:
	"""Areset commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("areset", core, parent)

	def set(self, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:STATistics:ARESet \n
		Snippet: driver.measurement.statistics.areset.set(measIndex = repcap.MeasIndex.Default) \n
		Resets the statistics for all measurements. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:STATistics:ARESet')

	def set_and_wait(self, measIndex=repcap.MeasIndex.Default, opc_timeout_ms: int = -1) -> None:
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		"""MEASurement<*>:STATistics:ARESet \n
		Snippet: driver.measurement.statistics.areset.set_and_wait(measIndex = repcap.MeasIndex.Default) \n
		Resets the statistics for all measurements. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'MEASurement{measIndex_cmd_val}:STATistics:ARESet', opc_timeout_ms)
