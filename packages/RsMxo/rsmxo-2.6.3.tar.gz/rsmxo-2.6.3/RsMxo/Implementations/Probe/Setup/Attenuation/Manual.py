from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ManualCls:
	"""Manual commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("manual", core, parent)

	def set(self, prb_att_md_manual: float, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:ATTenuation:MANual \n
		Snippet: driver.probe.setup.attenuation.manual.set(prb_att_md_manual = 1.0, probe = repcap.Probe.Default) \n
		Sets the attenuation for an unknown probe. \n
			:param prb_att_md_manual: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.decimal_value_to_str(prb_att_md_manual)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:ATTenuation:MANual {param}')

	def get(self, probe=repcap.Probe.Default) -> float:
		"""PROBe<*>:SETup:ATTenuation:MANual \n
		Snippet: value: float = driver.probe.setup.attenuation.manual.get(probe = repcap.Probe.Default) \n
		Sets the attenuation for an unknown probe. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: prb_att_md_manual: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:ATTenuation:MANual?')
		return Conversions.str_to_float(response)
