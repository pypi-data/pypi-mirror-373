from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DmOffsetCls:
	"""DmOffset commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dmOffset", core, parent)

	def set(self, dm_offset: float, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:DMOFfset \n
		Snippet: driver.probe.setup.dmOffset.set(dm_offset = 1.0, probe = repcap.Probe.Default) \n
		Sets the differential offset to compensate a DC voltage applied between the positive (Vp) and the negative (Vn) input
		terminal at the probe tip. \n
			:param dm_offset: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.decimal_value_to_str(dm_offset)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:DMOFfset {param}')

	def get(self, probe=repcap.Probe.Default) -> float:
		"""PROBe<*>:SETup:DMOFfset \n
		Snippet: value: float = driver.probe.setup.dmOffset.get(probe = repcap.Probe.Default) \n
		Sets the differential offset to compensate a DC voltage applied between the positive (Vp) and the negative (Vn) input
		terminal at the probe tip. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: dm_offset: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:DMOFfset?')
		return Conversions.str_to_float(response)
