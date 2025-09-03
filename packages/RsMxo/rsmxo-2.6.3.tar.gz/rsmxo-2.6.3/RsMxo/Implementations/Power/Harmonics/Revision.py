from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RevisionCls:
	"""Revision commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("revision", core, parent)

	def set(self, revision: enums.PwrHarmonicsRevision, power=repcap.Power.Default) -> None:
		"""POWer<*>:HARMonics:REVision \n
		Snippet: driver.power.harmonics.revision.set(revision = enums.PwrHarmonicsRevision.REV2011, power = repcap.Power.Default) \n
		Selects the revision of the EN61000 standard, if method RsMxo.Power.Harmonics.Standard.set is set to ENA / ENB / ENC /
		END. \n
			:param revision: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.enum_scalar_to_str(revision, enums.PwrHarmonicsRevision)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'POWer{power_cmd_val}:HARMonics:REVision {param}')

	# noinspection PyTypeChecker
	def get(self, power=repcap.Power.Default) -> enums.PwrHarmonicsRevision:
		"""POWer<*>:HARMonics:REVision \n
		Snippet: value: enums.PwrHarmonicsRevision = driver.power.harmonics.revision.get(power = repcap.Power.Default) \n
		Selects the revision of the EN61000 standard, if method RsMxo.Power.Harmonics.Standard.set is set to ENA / ENB / ENC /
		END. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: revision: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'POWer{power_cmd_val}:HARMonics:REVision?')
		return Conversions.str_to_scalar_enum(response, enums.PwrHarmonicsRevision)
