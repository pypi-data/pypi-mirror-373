from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class StProbeCls:
	"""StProbe commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("stProbe", core, parent)

	def set(self, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:OFFSet:STPRobe \n
		Snippet: driver.probe.setup.offset.stProbe.set(probe = repcap.Probe.Default) \n
		Saves the zero adjust value in the probe box. If you connect the probe to another channel or to another Rohde & Schwarz
		oscilloscope, the value is read out again, and you can use the probe without further adjustment. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:OFFSet:STPRobe')

	def set_and_wait(self, probe=repcap.Probe.Default, opc_timeout_ms: int = -1) -> None:
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		"""PROBe<*>:SETup:OFFSet:STPRobe \n
		Snippet: driver.probe.setup.offset.stProbe.set_and_wait(probe = repcap.Probe.Default) \n
		Saves the zero adjust value in the probe box. If you connect the probe to another channel or to another Rohde & Schwarz
		oscilloscope, the value is read out again, and you can use the probe without further adjustment. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'PROBe{probe_cmd_val}:SETup:OFFSet:STPRobe', opc_timeout_ms)
