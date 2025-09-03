from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import enums
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DefProbeCls:
	"""DefProbe commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("defProbe", core, parent)

	def set(self, select_predef_prb: enums.SelectProbe, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:ATTenuation:DEFProbe \n
		Snippet: driver.probe.setup.attenuation.defProbe.set(select_predef_prb = enums.SelectProbe.NONE, probe = repcap.Probe.Default) \n
		Selects one of the predefined probes, or a user-defined probe. \n
			:param select_predef_prb:
				- USER: Probe is not detected and not known to the instrument. Set unit and attenuation manually.
				- ZC10 | ZC20 | ZC30 | ZC03: Current probes
				- ZD01A100 | ZD01A1000: High voltage differential probes, attenuation ratio according to the setting on the probe.A100 = 100:1A1000 = 1000:1
				- ZC02100 | ZC021000: Current probes 100 A/V or 1000 A/V according to the setting on the probe.
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')"""
		param = Conversions.enum_scalar_to_str(select_predef_prb, enums.SelectProbe)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:ATTenuation:DEFProbe {param}')

	# noinspection PyTypeChecker
	def get(self, probe=repcap.Probe.Default) -> enums.SelectProbe:
		"""PROBe<*>:SETup:ATTenuation:DEFProbe \n
		Snippet: value: enums.SelectProbe = driver.probe.setup.attenuation.defProbe.get(probe = repcap.Probe.Default) \n
		Selects one of the predefined probes, or a user-defined probe. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: select_predef_prb: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:ATTenuation:DEFProbe?')
		return Conversions.str_to_scalar_enum(response, enums.SelectProbe)
