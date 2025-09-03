from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class OpCodeCls:
	"""OpCode commands group definition. 14 total commands, 4 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("opCode", core, parent)

	@property
	def size(self):
		"""size commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_size'):
			from .Size import SizeCls
			self._size = SizeCls(self._core, self._cmd_group)
		return self._size

	@property
	def append(self):
		"""append commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_append'):
			from .Append import AppendCls
			self._append = AppendCls(self._core, self._cmd_group)
		return self._append

	@property
	def dall(self):
		"""dall commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_dall'):
			from .Dall import DallCls
			self._dall = DallCls(self._core, self._cmd_group)
		return self._dall

	@property
	def item(self):
		"""item commands group. 9 Sub-classes, 0 commands."""
		if not hasattr(self, '_item'):
			from .Item import ItemCls
			self._item = ItemCls(self._core, self._cmd_group)
		return self._item

	def delete(self, index: int, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:QSPI:OPCode:DELete \n
		Snippet: driver.sbus.qspi.opCode.delete(index = 1, serialBus = repcap.SerialBus.Default) \n
		Deletes the opcode with the selected index. \n
			:param index: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(index)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:DELete {param}')

	def reset(self, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:QSPI:OPCode:RESet \n
		Snippet: driver.sbus.qspi.opCode.reset(serialBus = repcap.SerialBus.Default) \n
		Resets the opcode fields to the predefined values. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:RESet')

	def reset_and_wait(self, serialBus=repcap.SerialBus.Default, opc_timeout_ms: int = -1) -> None:
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		"""SBUS<*>:QSPI:OPCode:RESet \n
		Snippet: driver.sbus.qspi.opCode.reset_and_wait(serialBus = repcap.SerialBus.Default) \n
		Resets the opcode fields to the predefined values. \n
		Same as reset, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SBUS{serialBus_cmd_val}:QSPI:OPCode:RESet', opc_timeout_ms)

	def clone(self) -> 'OpCodeCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = OpCodeCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
