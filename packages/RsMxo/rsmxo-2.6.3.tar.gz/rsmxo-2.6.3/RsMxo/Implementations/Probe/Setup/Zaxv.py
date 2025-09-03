from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ZaxvCls:
	"""Zaxv commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("zaxv", core, parent)

	def set(self, ext_att_rt_za_15: bool, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:ZAXV \n
		Snippet: driver.probe.setup.zaxv.set(ext_att_rt_za_15 = False, probe = repcap.Probe.Default) \n
		If you use the external attenuator R&S RT-ZA15 together with one of the differential active probes R&S RT-ZD10/20/30,
		enable RT-ZA15 attenuator to include the external attenuation in the measurements. \n
			:param ext_att_rt_za_15: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.bool_to_str(ext_att_rt_za_15)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:ZAXV {param}')

	def get(self, probe=repcap.Probe.Default) -> bool:
		"""PROBe<*>:SETup:ZAXV \n
		Snippet: value: bool = driver.probe.setup.zaxv.get(probe = repcap.Probe.Default) \n
		If you use the external attenuator R&S RT-ZA15 together with one of the differential active probes R&S RT-ZD10/20/30,
		enable RT-ZA15 attenuator to include the external attenuation in the measurements. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: ext_att_rt_za_15: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:ZAXV?')
		return Conversions.str_to_bool(response)
