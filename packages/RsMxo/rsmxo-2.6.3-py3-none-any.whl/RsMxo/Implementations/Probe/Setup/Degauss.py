from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DegaussCls:
	"""Degauss commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("degauss", core, parent)

	def set(self, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:DEGauss \n
		Snippet: driver.probe.setup.degauss.set(probe = repcap.Probe.Default) \n
		Demagnetizes the core if it has been magnetized by switching the power on and off, or by an excessive input. Always carry
		out demagnetizing before measurement. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:DEGauss')

	def set_and_wait(self, probe=repcap.Probe.Default, opc_timeout_ms: int = -1) -> None:
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		"""PROBe<*>:SETup:DEGauss \n
		Snippet: driver.probe.setup.degauss.set_and_wait(probe = repcap.Probe.Default) \n
		Demagnetizes the core if it has been magnetized by switching the power on and off, or by an excessive input. Always carry
		out demagnetizing before measurement. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'PROBe{probe_cmd_val}:SETup:DEGauss', opc_timeout_ms)
