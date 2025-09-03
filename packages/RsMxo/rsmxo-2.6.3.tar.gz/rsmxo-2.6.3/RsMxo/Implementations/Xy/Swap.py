from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SwapCls:
	"""Swap commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("swap", core, parent)

	def set(self, xyAxis=repcap.XyAxis.Default) -> None:
		"""XY<*>:SWAP \n
		Snippet: driver.xy.swap.set(xyAxis = repcap.XyAxis.Default) \n
		Replaces the source of the x-axis with the source of the y-axis and vice versa. \n
			:param xyAxis: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Xy')
		"""
		xyAxis_cmd_val = self._cmd_group.get_repcap_cmd_value(xyAxis, repcap.XyAxis)
		self._core.io.write(f'XY{xyAxis_cmd_val}:SWAP')

	def set_and_wait(self, xyAxis=repcap.XyAxis.Default, opc_timeout_ms: int = -1) -> None:
		xyAxis_cmd_val = self._cmd_group.get_repcap_cmd_value(xyAxis, repcap.XyAxis)
		"""XY<*>:SWAP \n
		Snippet: driver.xy.swap.set_and_wait(xyAxis = repcap.XyAxis.Default) \n
		Replaces the source of the x-axis with the source of the y-axis and vice versa. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param xyAxis: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Xy')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'XY{xyAxis_cmd_val}:SWAP', opc_timeout_ms)
