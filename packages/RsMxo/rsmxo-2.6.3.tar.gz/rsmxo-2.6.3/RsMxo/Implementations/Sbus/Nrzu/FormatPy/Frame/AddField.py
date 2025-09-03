from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AddFieldCls:
	"""AddField commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("addField", core, parent)

	def set(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> None:
		"""SBUS<*>:NRZU:FORMat:FRAMe<*>:ADDField \n
		Snippet: driver.sbus.nrzu.formatPy.frame.addField.set(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Appends a new field description to the selected frame description. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
		"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:NRZU:FORMat:FRAMe{frame_cmd_val}:ADDField')

	def set_and_wait(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, opc_timeout_ms: int = -1) -> None:
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		"""SBUS<*>:NRZU:FORMat:FRAMe<*>:ADDField \n
		Snippet: driver.sbus.nrzu.formatPy.frame.addField.set_and_wait(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Appends a new field description to the selected frame description. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SBUS{serialBus_cmd_val}:NRZU:FORMat:FRAMe{frame_cmd_val}:ADDField', opc_timeout_ms)
