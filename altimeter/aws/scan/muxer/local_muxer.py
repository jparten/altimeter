"""AWSScanMuxer that runs account scans one-per-thread"""
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict

from altimeter.core.artifact_io.writer import FileArtifactWriter
from altimeter.aws.scan.muxer import AWSScanMuxer
from altimeter.aws.scan.account_scan_plan import AccountScanPlan
from altimeter.aws.scan.account_scanner import AccountScanner

DEFAULT_MAX_ACCOUNT_THREADS = 32
DEFAULT_MAX_SVC_THREADS = 2


def local_account_scan(
    account_scan_plan_dict: Dict[str, Any], scan_sub_accounts: bool, output_dir: Path
) -> Dict[str, Any]:
    """Scan an account.

    Args:
        account_scan_plan_dict: AccountScanPlan data defining the scan
        scan_sub_accounts: if True, scan subaccounts of any org master accounts
        output_dir: output artifats to this Path
    """
    artifact_writer = FileArtifactWriter(output_dir=output_dir)
    account_scan_plan = AccountScanPlan.from_dict(account_scan_plan_dict=account_scan_plan_dict)
    account_scanner = AccountScanner(
        account_id=account_scan_plan.account_id,
        regions=account_scan_plan.regions,
        get_session=account_scan_plan.get_session,
        artifact_writer=artifact_writer,
        scan_sub_accounts=scan_sub_accounts,
        max_svc_threads=DEFAULT_MAX_SVC_THREADS,
    )
    return account_scanner.scan()


class LocalAWSScanMuxer(AWSScanMuxer):
    """AWSScanMuxer that runs account scans one account per thread and saves results
    to a filesystem path.

    Args:
        output_dir: output artifacts to this dir
        scan_sub_accounts: if True, scan subaccounts of any org master accounts
        max_threads: max number of scan threads to run concurrently
    """

    def __init__(
        self,
        output_dir: Path,
        scan_sub_accounts: bool,
        max_threads: int = DEFAULT_MAX_ACCOUNT_THREADS,
    ):
        super().__init__(max_threads=max_threads)
        self.output_dir = output_dir
        self.scan_sub_accounts = scan_sub_accounts

    def _schedule_account_scan(
        self, executor: ThreadPoolExecutor, account_scan_plan: AccountScanPlan
    ) -> Future:
        """Schedule a local account scan. Note that we serialize the AccountScanPlan
        because boto3 sessions are not thread safe.

        Args:
            executor: ThreadPoolExecutor to submit scan to
            account_scan_plan: AccountScanPlan defining this scan
        """
        scan_lambda = lambda: local_account_scan(
            account_scan_plan_dict=account_scan_plan.to_dict(),
            output_dir=self.output_dir,
            scan_sub_accounts=self.scan_sub_accounts,
        )
        return executor.submit(scan_lambda)
