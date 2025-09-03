from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AcCouplingCls:
	"""AcCoupling commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("acCoupling", core, parent)

	def set(self, probe_cpl_ac: bool, probe=repcap.Probe.Default) -> None:
		"""PROBe<*>:SETup:ACCoupling \n
		Snippet: driver.probe.setup.acCoupling.set(probe_cpl_ac = False, probe = repcap.Probe.Default) \n
		Enables AC coupling in R&S RT-ZPR power rail probes, which removes DC and very low-frequency components. The R&S RT-ZPR
		probe requires 50 Ω input termination, for which the channel AC coupling is not available. The probe setting allows AC
		coupling also at 50 Ω inputs. \n
			:param probe_cpl_ac: No help available
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
		"""
		param = Conversions.bool_to_str(probe_cpl_ac)
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		self._core.io.write(f'PROBe{probe_cmd_val}:SETup:ACCoupling {param}')

	def get(self, probe=repcap.Probe.Default) -> bool:
		"""PROBe<*>:SETup:ACCoupling \n
		Snippet: value: bool = driver.probe.setup.acCoupling.get(probe = repcap.Probe.Default) \n
		Enables AC coupling in R&S RT-ZPR power rail probes, which removes DC and very low-frequency components. The R&S RT-ZPR
		probe requires 50 Ω input termination, for which the channel AC coupling is not available. The probe setting allows AC
		coupling also at 50 Ω inputs. \n
			:param probe: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Probe')
			:return: probe_cpl_ac: No help available"""
		probe_cmd_val = self._cmd_group.get_repcap_cmd_value(probe, repcap.Probe)
		response = self._core.io.query_str(f'PROBe{probe_cmd_val}:SETup:ACCoupling?')
		return Conversions.str_to_bool(response)
