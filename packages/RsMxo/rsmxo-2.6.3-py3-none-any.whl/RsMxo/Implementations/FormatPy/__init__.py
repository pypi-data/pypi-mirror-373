from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FormatPyCls:
	"""FormatPy commands group definition. 3 total commands, 1 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("formatPy", core, parent)

	@property
	def data(self):
		"""data commands group. 0 Sub-classes, 1 commands."""
		if not hasattr(self, '_data'):
			from .Data import DataCls
			self._data = DataCls(self._core, self._cmd_group)
		return self._data

	# noinspection PyTypeChecker
	def get_border(self) -> enums.ByteOrder:
		"""FORMat:BORDer \n
		Snippet: value: enums.ByteOrder = driver.formatPy.get_border() \n
		Sets the endianness. The command is only relevant for data in integer and float format. \n
			:return: byte_order: LSB first: little endian, least significant byte first MSB first: big endian, most significant byte first
		"""
		response = self._core.io.query_str('FORMat:BORDer?')
		return Conversions.str_to_scalar_enum(response, enums.ByteOrder)

	def set_border(self, byte_order: enums.ByteOrder) -> None:
		"""FORMat:BORDer \n
		Snippet: driver.formatPy.set_border(byte_order = enums.ByteOrder.LSBFirst) \n
		Sets the endianness. The command is only relevant for data in integer and float format. \n
			:param byte_order: LSB first: little endian, least significant byte first MSB first: big endian, most significant byte first
		"""
		param = Conversions.enum_scalar_to_str(byte_order, enums.ByteOrder)
		self._core.io.write(f'FORMat:BORDer {param}')

	# noinspection PyTypeChecker
	def get_bpattern(self) -> enums.SbusDataFormat:
		"""FORMat:BPATtern \n
		Snippet: value: enums.SbusDataFormat = driver.formatPy.get_bpattern() \n
		Sets the number format for remote bit pattern queries on serial protocols. \n
			:return: bt_patt_fmt: No help available
		"""
		response = self._core.io.query_str('FORMat:BPATtern?')
		return Conversions.str_to_scalar_enum(response, enums.SbusDataFormat)

	def set_bpattern(self, bt_patt_fmt: enums.SbusDataFormat) -> None:
		"""FORMat:BPATtern \n
		Snippet: driver.formatPy.set_bpattern(bt_patt_fmt = enums.SbusDataFormat.ASCII) \n
		Sets the number format for remote bit pattern queries on serial protocols. \n
			:param bt_patt_fmt: No help available
		"""
		param = Conversions.enum_scalar_to_str(bt_patt_fmt, enums.SbusDataFormat)
		self._core.io.write(f'FORMat:BPATtern {param}')

	def clone(self) -> 'FormatPyCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = FormatPyCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
