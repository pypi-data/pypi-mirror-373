from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.RepeatedCapability import RepeatedCapability
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ThresholdCls:
	"""Threshold commands group definition. 1 total commands, 0 Subgroups, 1 group commands
	Repeated Capability: ThrHold, default value after init: ThrHold.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("threshold", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_thrHold_get', 'repcap_thrHold_set', repcap.ThrHold.Nr1)

	def repcap_thrHold_set(self, thrHold: repcap.ThrHold) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to ThrHold.Default.
		Default value after init: ThrHold.Nr1"""
		self._cmd_group.set_repcap_enum_value(thrHold)

	def repcap_thrHold_get(self) -> repcap.ThrHold:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	def set(self, threshold: float, pwrBus=repcap.PwrBus.Default, thrHold=repcap.ThrHold.Default) -> None:
		"""PBUS<*>:THReshold<*> \n
		Snippet: driver.pbus.threshold.set(threshold = 1.0, pwrBus = repcap.PwrBus.Default, thrHold = repcap.ThrHold.Default) \n
		Sets the logical threshold for the indicated channel group. Alternatively you can use the following commands:
			INTRO_CMD_HELP: Bits: \n
			- To select from a list of predefined technologies: method RsMxo.Pbus.Technology.set
			- For logic 1: method RsMxo.Digital.Threshold.set
		See also method RsMxo.Digital.ThCoupling.set. \n
			:param threshold: No help available
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:param thrHold: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Threshold')
		"""
		param = Conversions.decimal_value_to_str(threshold)
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		thrHold_cmd_val = self._cmd_group.get_repcap_cmd_value(thrHold, repcap.ThrHold)
		self._core.io.write(f'PBUS{pwrBus_cmd_val}:THReshold{thrHold_cmd_val} {param}')

	def get(self, pwrBus=repcap.PwrBus.Default, thrHold=repcap.ThrHold.Default) -> float:
		"""PBUS<*>:THReshold<*> \n
		Snippet: value: float = driver.pbus.threshold.get(pwrBus = repcap.PwrBus.Default, thrHold = repcap.ThrHold.Default) \n
		Sets the logical threshold for the indicated channel group. Alternatively you can use the following commands:
			INTRO_CMD_HELP: Bits: \n
			- To select from a list of predefined technologies: method RsMxo.Pbus.Technology.set
			- For logic 1: method RsMxo.Digital.Threshold.set
		See also method RsMxo.Digital.ThCoupling.set. \n
			:param pwrBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Pbus')
			:param thrHold: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Threshold')
			:return: threshold: No help available"""
		pwrBus_cmd_val = self._cmd_group.get_repcap_cmd_value(pwrBus, repcap.PwrBus)
		thrHold_cmd_val = self._cmd_group.get_repcap_cmd_value(thrHold, repcap.ThrHold)
		response = self._core.io.query_str(f'PBUS{pwrBus_cmd_val}:THReshold{thrHold_cmd_val}?')
		return Conversions.str_to_float(response)

	def clone(self) -> 'ThresholdCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = ThresholdCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
