from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from ....Internal.RepeatedCapability import RepeatedCapability
from .... import enums
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RefLevelCls:
	"""RefLevel commands group definition. 1 total commands, 0 Subgroups, 1 group commands
	Repeated Capability: RefLevel, default value after init: RefLevel.Nr1"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("refLevel", core, parent)
		self._cmd_group.rep_cap = RepeatedCapability(self._cmd_group.group_name, 'repcap_refLevel_get', 'repcap_refLevel_set', repcap.RefLevel.Nr1)

	def repcap_refLevel_set(self, refLevel: repcap.RefLevel) -> None:
		"""Repeated Capability default value numeric suffix.
		This value is used, if you do not explicitely set it in the child set/get methods, or if you leave it to RefLevel.Default.
		Default value after init: RefLevel.Nr1"""
		self._cmd_group.set_repcap_enum_value(refLevel)

	def repcap_refLevel_get(self) -> repcap.RefLevel:
		"""Returns the current default repeated capability for the child set/get methods"""
		# noinspection PyTypeChecker
		return self._cmd_group.get_repcap_enum_value()

	def set(self, reference_level: enums.ReferenceLevel, measIndex=repcap.MeasIndex.Default, refLevel=repcap.RefLevel.Default) -> None:
		"""MEASurement<*>:JITTer:REFLevel<*> \n
		Snippet: driver.measurement.jitter.refLevel.set(reference_level = enums.ReferenceLevel.LOWer, measIndex = repcap.MeasIndex.Default, refLevel = repcap.RefLevel.Default) \n
		Selects the reference level that is used for the measurement and for the indicated measurement source. Each source of the
		measurement can have its own reference level . \n
			:param reference_level: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
		"""
		param = Conversions.enum_scalar_to_str(reference_level, enums.ReferenceLevel)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:JITTer:REFLevel{refLevel_cmd_val} {param}')

	# noinspection PyTypeChecker
	def get(self, measIndex=repcap.MeasIndex.Default, refLevel=repcap.RefLevel.Default) -> enums.ReferenceLevel:
		"""MEASurement<*>:JITTer:REFLevel<*> \n
		Snippet: value: enums.ReferenceLevel = driver.measurement.jitter.refLevel.get(measIndex = repcap.MeasIndex.Default, refLevel = repcap.RefLevel.Default) \n
		Selects the reference level that is used for the measurement and for the indicated measurement source. Each source of the
		measurement can have its own reference level . \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:param refLevel: optional repeated capability selector. Default value: Nr1 (settable in the interface 'RefLevel')
			:return: reference_level: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		refLevel_cmd_val = self._cmd_group.get_repcap_cmd_value(refLevel, repcap.RefLevel)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:JITTer:REFLevel{refLevel_cmd_val}?')
		return Conversions.str_to_scalar_enum(response, enums.ReferenceLevel)

	def clone(self) -> 'RefLevelCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = RefLevelCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
