from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class NoffsetCls:
	"""Noffset commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("noffset", core, parent)

	def set(self, noffset: float, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:NOFFset \n
		Snippet: driver.probe.setup.noffset.set(noffset = 1.0, probe = repcap.Probe.Default) \n
		Sets the negative offset to compensate a DC voltage applied to the negative input terminal (Vn) referenced to ground. \n
			:param noffset: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.decimal_value_to_str(noffset)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:NOFFset {param}')

	def get(self, probe=repcap.Probe.Default) -> float:
		"""PROBe<*>:SETup:NOFFset \n
		Snippet: value: float = driver.probe.setup.noffset.get(probe = repcap.Probe.Default) \n
		Sets the negative offset to compensate a DC voltage applied to the negative input terminal (Vn) referenced to ground. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: noffset: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:NOFFset?')
		return Conversions.str_to_float(response)
