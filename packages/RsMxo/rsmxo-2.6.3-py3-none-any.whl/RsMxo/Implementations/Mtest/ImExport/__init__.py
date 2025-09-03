from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ImExportCls:
	"""ImExport commands group definition. 3 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("imExport", core, parent)

	@property
	def name(self):
		"""name commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_name'):
			from .Name import NameCls
			self._name = NameCls(self._core, self._cmd_group)
		return self._name

	def save(self, maskTest=repcap.MaskTest.Default) -> None:
		"""MTESt<*>:IMEXport:SAVE \n
		Snippet: driver.mtest.imExport.save(maskTest = repcap.MaskTest.Default) \n
		Saves the mask test to the file selected by method RsMxo.Mtest.ImExport.Name.set. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
		"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		self._core.io.write(f'MTESt{maskTest_cmd_val}:IMEXport:SAVE')

	def save_and_wait(self, maskTest=repcap.MaskTest.Default, opc_timeout_ms: int = -1) -> None:
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		"""MTESt<*>:IMEXport:SAVE \n
		Snippet: driver.mtest.imExport.save_and_wait(maskTest = repcap.MaskTest.Default) \n
		Saves the mask test to the file selected by method RsMxo.Mtest.ImExport.Name.set. \n
		Same as save, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'MTESt{maskTest_cmd_val}:IMEXport:SAVE', opc_timeout_ms)

	def open(self, maskTest=repcap.MaskTest.Default) -> None:
		"""MTESt<*>:IMEXport:OPEN \n
		Snippet: driver.mtest.imExport.open(maskTest = repcap.MaskTest.Default) \n
		Opens and loads the mask selected by method RsMxo.Mtest.ImExport.Name.set. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
		"""
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		self._core.io.write(f'MTESt{maskTest_cmd_val}:IMEXport:OPEN')

	def open_and_wait(self, maskTest=repcap.MaskTest.Default, opc_timeout_ms: int = -1) -> None:
		maskTest_cmd_val = self._cmd_group.get_repcap_cmd_value(maskTest, repcap.MaskTest)
		"""MTESt<*>:IMEXport:OPEN \n
		Snippet: driver.mtest.imExport.open_and_wait(maskTest = repcap.MaskTest.Default) \n
		Opens and loads the mask selected by method RsMxo.Mtest.ImExport.Name.set. \n
		Same as open, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param maskTest: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Mtest')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'MTESt{maskTest_cmd_val}:IMEXport:OPEN', opc_timeout_ms)

	def clone(self) -> 'ImExportCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ImExportCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
