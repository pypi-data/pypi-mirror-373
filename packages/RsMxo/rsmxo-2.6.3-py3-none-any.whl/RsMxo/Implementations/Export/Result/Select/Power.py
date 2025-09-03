from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.RepeatedCapability import RepeatedCapability
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PowerCls:
	"""Power commands group definition. 1 total commands, 0 Subgroups, 1 group commands
	Repeated Capability: Power, default value after init: Power.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("power", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_power_get', 'repcap_power_set', repcap.Power.Nr1)

	def repcap_power_set(self, power: repcap.Power) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to Power.Default.
		Default value after init: Power.Nr1"""
		self._cmd_group.set_repcap_enum_value(power)

	def repcap_power_get(self) -> repcap.Power:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	def set(self, export_results: bool, power=repcap.Power.Default) -> None:
		"""EXPort:RESult:SELect:POWer<*> \n
		Snippet: driver.export.result.select.power.set(export_results = False, power = repcap.Power.Default) \n
		If enabled, includes the results of selected power analysis measurement in the results export file. \n
			:param export_results: No help available
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
		"""
		param = Conversions.bool_to_str(export_results)
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		self._core.io.write(f'EXPort:RESult:SELect:POWer{power_cmd_val} {param}')

	def get(self, power=repcap.Power.Default) -> bool:
		"""EXPort:RESult:SELect:POWer<*> \n
		Snippet: value: bool = driver.export.result.select.power.get(power = repcap.Power.Default) \n
		If enabled, includes the results of selected power analysis measurement in the results export file. \n
			:param power: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Power')
			:return: export_results: No help available"""
		power_cmd_val = self._cmd_group.get_repcap_cmd_value(power, repcap.Power)
		response = self._core.io.query_str(f'EXPort:RESult:SELect:POWer{power_cmd_val}?')
		return Conversions.str_to_bool(response)

	def clone(self) -> 'PowerCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = PowerCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
