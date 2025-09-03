from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class XdataCls:
	"""Xdata commands group definition. 10 total commands, 3 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("xdata", core, parent)

	@property
	def sdt(self):
		"""sdt commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_sdt'):
			from .Sdt import SdtCls
			self._sdt = SdtCls(self._core, self._cmd_group)
		return self._sdt

	@property
	def vcid(self):
		"""vcid commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_vcid'):
			from .Vcid import VcidCls
			self._vcid = VcidCls(self._core, self._cmd_group)
		return self._vcid

	@property
	def af(self):
		"""af commands group. 0 Sub-classes, 3 commands."""
		if not hasattr(self, '_af'):
			from .Af import AfCls
			self._af = AfCls(self._core, self._cmd_group)
		return self._af

	# noinspection PyTypeChecker
	def get_sec(self) -> enums.SbusBitState:
		"""TRIGger:SBHW:CAN:XDATa:SEC \n
		Snippet: value: enums.SbusBitState = driver.trigger.sbhw.can.xdata.get_sec() \n
		Sets a value for the simple extended content (SEC) field. It indicates, if the CAN XL data frame uses the CADsec protocol. \n
			:return: sec_bit: No help available
		"""
		response = self._core.io.query_str('TRIGger:SBHW:CAN:XDATa:SEC?')
		return Conversions.str_to_scalar_enum(response, enums.SbusBitState)

	def set_sec(self, sec_bit: enums.SbusBitState) -> None:
		"""TRIGger:SBHW:CAN:XDATa:SEC \n
		Snippet: driver.trigger.sbhw.can.xdata.set_sec(sec_bit = enums.SbusBitState.DC) \n
		Sets a value for the simple extended content (SEC) field. It indicates, if the CAN XL data frame uses the CADsec protocol. \n
			:param sec_bit: No help available
		"""
		param = Conversions.enum_scalar_to_str(sec_bit, enums.SbusBitState)
		self._core.io.write(f'TRIGger:SBHW:CAN:XDATa:SEC {param}')

	def clone(self) -> 'XdataCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = XdataCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
