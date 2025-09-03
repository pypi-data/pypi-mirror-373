from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class HardCopyCls:
	"""HardCopy commands group definition. 9 total commands, 2 Subgroups, 5 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("hardCopy", core, parent)

	@property
	def immediate(self):
		"""immediate commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_immediate'):
			from .Immediate import ImmediateCls
			self._immediate = ImmediateCls(self._core, self._cmd_group)
		return self._immediate

	@property
	def device(self):
		"""device commands group. 0 Sub-classes, 2 commands."""
		if not hasattr(self, '_device'):
			from .Device import DeviceCls
			self._device = DeviceCls(self._core, self._cmd_group)
		return self._device

	def get_data(self) -> bytes:
		"""HCOPy:DATA \n
		Snippet: value: bytes = driver.hardCopy.get_data() \n
		Creates a PNG screenshot and returns the data of the image file in a binary data stream. When receiving the data, write
		them into a PNG file which you can open later. \n
			:return: picture_data: No help available
		"""
		response = self._core.io.query_bin_block('HCOPy:DATA?')
		return response

	def get_wbkg(self) -> bool:
		"""HCOPy:WBKG \n
		Snippet: value: bool = driver.hardCopy.get_wbkg() \n
		Inverts the background color, so you can picture waveforms with normal waveform colors on white background.
		If both method RsMxo.HardCopy.wbkg and method RsMxo.HardCopy.Device.inverse are ON, the instrument inverts the background
		twice, and it appears black. \n
			:return: white_background_scpi: No help available
		"""
		response = self._core.io.query_str('HCOPy:WBKG?')
		return Conversions.str_to_bool(response)

	def set_wbkg(self, white_background_scpi: bool) -> None:
		"""HCOPy:WBKG \n
		Snippet: driver.hardCopy.set_wbkg(white_background_scpi = False) \n
		Inverts the background color, so you can picture waveforms with normal waveform colors on white background.
		If both method RsMxo.HardCopy.wbkg and method RsMxo.HardCopy.Device.inverse are ON, the instrument inverts the background
		twice, and it appears black. \n
			:param white_background_scpi: No help available
		"""
		param = Conversions.bool_to_str(white_background_scpi)
		self._core.io.write(f'HCOPy:WBKG {param}')

	def get_ssd(self) -> bool:
		"""HCOPy:SSD \n
		Snippet: value: bool = driver.hardCopy.get_ssd() \n
		If enabled, the currently open dialog box is included in the screenshot. \n
			:return: shw_set_dialog_scpi: No help available
		"""
		response = self._core.io.query_str('HCOPy:SSD?')
		return Conversions.str_to_bool(response)

	def set_ssd(self, shw_set_dialog_scpi: bool) -> None:
		"""HCOPy:SSD \n
		Snippet: driver.hardCopy.set_ssd(shw_set_dialog_scpi = False) \n
		If enabled, the currently open dialog box is included in the screenshot. \n
			:param shw_set_dialog_scpi: No help available
		"""
		param = Conversions.bool_to_str(shw_set_dialog_scpi)
		self._core.io.write(f'HCOPy:SSD {param}')

	def get_isba(self) -> bool:
		"""HCOPy:ISBA \n
		Snippet: value: bool = driver.hardCopy.get_isba() \n
		If enabled, the screenshot shows the signal bar below the diagram area. \n
			:return: include_sign_bar_scpi: No help available
		"""
		response = self._core.io.query_str('HCOPy:ISBA?')
		return Conversions.str_to_bool(response)

	def set_isba(self, include_sign_bar_scpi: bool) -> None:
		"""HCOPy:ISBA \n
		Snippet: driver.hardCopy.set_isba(include_sign_bar_scpi = False) \n
		If enabled, the screenshot shows the signal bar below the diagram area. \n
			:param include_sign_bar_scpi: No help available
		"""
		param = Conversions.bool_to_str(include_sign_bar_scpi)
		self._core.io.write(f'HCOPy:ISBA {param}')

	# noinspection PyTypeChecker
	def get_destination(self) -> enums.PrintTarget:
		"""HCOPy:DESTination \n
		Snippet: value: enums.PrintTarget = driver.hardCopy.get_destination() \n
		Selects the output medium: file or clipboard. \n
			:return: medium: MMEM: saves image to a file. CLIPBOARD: directs the image to the clipboard.
		"""
		response = self._core.io.query_str('HCOPy:DESTination?')
		return Conversions.str_to_scalar_enum(response, enums.PrintTarget)

	def set_destination(self, medium: enums.PrintTarget) -> None:
		"""HCOPy:DESTination \n
		Snippet: driver.hardCopy.set_destination(medium = enums.PrintTarget.CLIPBOARD) \n
		Selects the output medium: file or clipboard. \n
			:param medium: MMEM: saves image to a file. CLIPBOARD: directs the image to the clipboard.
		"""
		param = Conversions.enum_scalar_to_str(medium, enums.PrintTarget)
		self._core.io.write(f'HCOPy:DESTination {param}')

	def clone(self) -> 'HardCopyCls':
		"""Clones the group by creating new object from it and its whole existing subgroups
		Also copies all the existing default Repeated Capabilities setting,
		which you can change independently without affecting the original group"""
		new_group = HardCopyCls(self._core, self._cmd_group.parent)
		self._cmd_group.synchronize_repcaps(new_group)
		return new_group
