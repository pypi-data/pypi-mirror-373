from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AddFrameCls:
	"""AddFrame commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("addFrame", core, parent)

	def set(self, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:NRZC:FORMat:ADDFrame \n
		Snippet: driver.sbus.nrzc.formatPy.addFrame.set(serialBus = repcap.SerialBus.Default) \n
		Appendes a new frame description to the frame list. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZC:FORMat:ADDFrame')

	def set_and_wait(self, serialBus=repcap.SerialBus.Default, opc_timeout_ms: int = -1) -> None:
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		"""SBUS<*>:NRZC:FORMat:ADDFrame \n
		Snippet: driver.sbus.nrzc.formatPy.addFrame.set_and_wait(serialBus = repcap.SerialBus.Default) \n
		Appendes a new frame description to the frame list. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SBUS{serialBus_cmd_val}:NRZC:FORMat:ADDFrame', opc_timeout_ms)
