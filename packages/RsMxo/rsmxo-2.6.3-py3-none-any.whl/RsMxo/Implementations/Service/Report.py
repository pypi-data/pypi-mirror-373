from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ReportCls:
	"""Report commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("report", core, parent)

	def set(self, opc_timeout_ms: int = -1) -> None:
		"""SERVice:REPort \n
		Snippet: driver.service.report.set() \n
		Creates a service report. The service report is a ZIP file with a complete bug report, all relevant setup information,
		reporting and log files, alignment files, and the instrument configuration. If a USB flash drive is connected, the report
		is saved on the USB flash drive. Otherwise, the report is saved in the user data folder /home/storage/userData. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SERVice:REPort', opc_timeout_ms)
		# OpcSyncAllowed = true
