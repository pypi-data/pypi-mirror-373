from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UpdateCls:
	"""Update commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("update", core, parent)

	def set(self, refCurve=repcap.RefCurve.Default) -> None:
		"""REFCurve<*>:UPDate \n
		Snippet: driver.refCurve.update.set(refCurve = repcap.RefCurve.Default) \n
		Copies the selected source waveform with all its settings to the memory of the reference waveform.
		If there is a previously defined reference waveform in this memory, it is updated by the current source waveform. If the
		acquisition is running, the reference waveform is a snapshot. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
		"""
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		self._core.io.write(f'REFCurve{refCurve_cmd_val}:UPDate')

	def set_and_wait(self, refCurve=repcap.RefCurve.Default, opc_timeout_ms: int = -1) -> None:
		refCurve_cmd_val = self._cmd_group.get_repcap_cmd_value(refCurve, repcap.RefCurve)
		"""REFCurve<*>:UPDate \n
		Snippet: driver.refCurve.update.set_and_wait(refCurve = repcap.RefCurve.Default) \n
		Copies the selected source waveform with all its settings to the memory of the reference waveform.
		If there is a previously defined reference waveform in this memory, it is updated by the current source waveform. If the
		acquisition is running, the reference waveform is a snapshot. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param refCurve: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefCurve')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'REFCurve{refCurve_cmd_val}:UPDate', opc_timeout_ms)
