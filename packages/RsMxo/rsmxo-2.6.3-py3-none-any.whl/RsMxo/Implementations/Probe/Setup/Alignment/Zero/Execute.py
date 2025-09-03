from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ExecuteCls:
	"""Execute commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("execute", core, parent)

	def set(self, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:ALIGnment:ZERO:EXECute \n
		Snippet: driver.probe.setup.alignment.zero.execute.set(probe = repcap.Probe.Default) \n
		Performs a self-alignment and corrects the zero point error of the R&S RT-ZISO probe. To write the alignment result to
		the non-volatile flash of the probe, use method RsMxo.Probe.Setup.Alignment.Write.set. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:ALIGnment:ZERO:EXECute')

	def set_and_wait(self, probe=repcap.Probe.Default, opc_timeout_ms: int = -1) -> None:
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		"""PROBe<*>:SETup:ALIGnment:ZERO:EXECute \n
		Snippet: driver.probe.setup.alignment.zero.execute.set_and_wait(probe = repcap.Probe.Default) \n
		Performs a self-alignment and corrects the zero point error of the R&S RT-ZISO probe. To write the alignment result to
		the non-volatile flash of the probe, use method RsMxo.Probe.Setup.Alignment.Write.set. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'PROBe{probe_cmd_val}:SETup:ALIGnment:ZERO:EXECute', opc_timeout_ms)
