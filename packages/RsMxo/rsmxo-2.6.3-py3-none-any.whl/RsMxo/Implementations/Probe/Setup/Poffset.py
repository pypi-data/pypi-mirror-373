from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PoffsetCls:
	"""Poffset commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("poffset", core, parent)

	def set(self, poffset: float, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:POFFset \n
		Snippet: driver.probe.setup.poffset.set(poffset = 1.0, probe = repcap.Probe.Default) \n
		Sets the positive offset to compensate a DC voltage applied to the positive input terminal (Vp) referenced to ground. \n
			:param poffset: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.decimal_value_to_str(poffset)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:POFFset {param}')

	def get(self, probe=repcap.Probe.Default) -> float:
		"""PROBe<*>:SETup:POFFset \n
		Snippet: value: float = driver.probe.setup.poffset.get(probe = repcap.Probe.Default) \n
		Sets the positive offset to compensate a DC voltage applied to the positive input terminal (Vp) referenced to ground. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: poffset: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:POFFset?')
		return Conversions.str_to_float(response)
