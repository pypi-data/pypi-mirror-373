"""Generic async transfer operations with progress tracking."""

import asyncio
import logging
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from .core import transfer
from .constants import AsyncTransferStatus, TransferStatus

logger = logging.getLogger(__name__)


@dataclass
class TransferProgress:
    operation_id: str
    operation_name: str
    status: AsyncTransferStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress_callback: Optional[Callable[[str], None]] = None

    def update_status(
        self, status: AsyncTransferStatus, error_message: Optional[str] = None
    ):
        self.status = status
        if error_message:
            self.error_message = error_message
        if status == AsyncTransferStatus.IN_PROGRESS and self.started_at is None:
            self.started_at = datetime.now()
        elif status in [
            AsyncTransferStatus.SUCCESS,
            AsyncTransferStatus.ERROR,
            AsyncTransferStatus.INTERRUPTED,
            AsyncTransferStatus.CANCELLED,
        ]:
            self.completed_at = datetime.now()

        # Notify callback if provided
        if self.progress_callback:
            try:
                self.progress_callback(self.operation_id)
            except Exception as e:
                logger.warning(f"Progress callback failed for {self.operation_id}: {e}")


class AsyncTransferManager:
    def __init__(self):
        self._transfers: Dict[str, TransferProgress] = {}
        self._executor = ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="b10-async-transfer"
        )
        self._lock = threading.Lock()
        self._operation_counter = 0

    def _generate_operation_id(self, operation_name: str) -> str:
        with self._lock:
            self._operation_counter += 1
            return f"{operation_name}_{self._operation_counter}_{int(datetime.now().timestamp())}"

    def start_transfer_async(
        self,
        source: Path,
        dest: Path,
        callback: Callable,
        operation_name: str,
        progress_callback: Optional[Callable[[str], None]] = None,
        monitor_local: bool = True,
        monitor_b10fs: bool = True,
        **callback_kwargs,
    ) -> str:
        operation_id = self._generate_operation_id(operation_name)

        progress = TransferProgress(
            operation_id=operation_id,
            operation_name=operation_name,
            status=AsyncTransferStatus.NOT_STARTED,
            progress_callback=progress_callback,
        )

        with self._lock:
            self._transfers[operation_id] = progress

        # Submit the transfer operation to thread pool
        future = self._executor.submit(
            self._execute_transfer,
            operation_id,
            source,
            dest,
            callback,
            monitor_local,
            monitor_b10fs,
            callback_kwargs,
        )

        logger.info(f"Started async transfer operation: {operation_id}")
        return operation_id

    def _execute_transfer(
        self,
        operation_id: str,
        source: Path,
        dest: Path,
        callback: Callable,
        monitor_local: bool,
        monitor_b10fs: bool,
        callback_kwargs: Dict[str, Any],
    ) -> None:
        progress = self._transfers.get(operation_id)
        if not progress:
            logger.error(f"Progress tracking lost for operation {operation_id}")
            return

        try:
            progress.update_status(AsyncTransferStatus.IN_PROGRESS)
            logger.info(f"Starting transfer for operation {operation_id}")

            result = transfer(
                source=source,
                dest=dest,
                callback=callback,
                monitor_local=monitor_local,
                monitor_b10fs=monitor_b10fs,
                **callback_kwargs,
            )

            # Convert TransferStatus to AsyncTransferStatus
            if result == TransferStatus.SUCCESS:
                progress.update_status(AsyncTransferStatus.SUCCESS)
                logger.info(f"Transfer completed successfully: {operation_id}")
            elif result == TransferStatus.INTERRUPTED:
                progress.update_status(
                    AsyncTransferStatus.INTERRUPTED,
                    "Transfer interrupted due to insufficient disk space",
                )
                logger.warning(f"Transfer interrupted: {operation_id}")
            else:
                progress.update_status(
                    AsyncTransferStatus.ERROR, "Transfer operation failed"
                )
                logger.error(f"Transfer failed: {operation_id}")

        except Exception as e:
            progress.update_status(AsyncTransferStatus.ERROR, str(e))
            logger.error(
                f"Transfer operation {operation_id} failed with exception: {e}"
            )

    def get_transfer_status(self, operation_id: str) -> Optional[TransferProgress]:
        with self._lock:
            return self._transfers.get(operation_id)

    def is_transfer_complete(self, operation_id: str) -> bool:
        progress = self.get_transfer_status(operation_id)
        if not progress:
            return False

        return progress.status in [
            AsyncTransferStatus.SUCCESS,
            AsyncTransferStatus.ERROR,
            AsyncTransferStatus.INTERRUPTED,
            AsyncTransferStatus.CANCELLED,
        ]

    def wait_for_completion(
        self, operation_id: str, timeout: Optional[float] = None
    ) -> bool:
        start_time = datetime.now()

        while not self.is_transfer_complete(operation_id):
            if timeout and (datetime.now() - start_time).total_seconds() > timeout:
                return False
            time.sleep(0.1)  # Small delay to avoid busy waiting

        return True

    def cancel_transfer(self, operation_id: str) -> bool:
        progress = self.get_transfer_status(operation_id)
        if not progress:
            return False

        if progress.status == AsyncTransferStatus.IN_PROGRESS:
            progress.update_status(AsyncTransferStatus.CANCELLED)
            logger.info(f"Marked transfer operation as cancelled: {operation_id}")
            return True

        return False

    def cleanup_completed_transfers(self, max_age_hours: int = 24) -> int:
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cleaned_count = 0

        with self._lock:
            to_remove = []
            for operation_id, progress in self._transfers.items():
                if (
                    progress.completed_at
                    and progress.completed_at < cutoff_time
                    and self.is_transfer_complete(operation_id)
                ):
                    to_remove.append(operation_id)

            for operation_id in to_remove:
                del self._transfers[operation_id]
                cleaned_count += 1

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} completed transfer records")

        return cleaned_count

    def list_active_transfers(self) -> Dict[str, TransferProgress]:
        with self._lock:
            return {
                op_id: progress
                for op_id, progress in self._transfers.items()
                if not self.is_transfer_complete(op_id)
            }

    def shutdown(self) -> None:
        logger.info("Shutting down async transfer manager...")
        self._executor.shutdown(wait=True)


# Global instance for easy access
_transfer_manager = AsyncTransferManager()


# Generic Public API functions
def start_transfer_async(
    source: Path,
    dest: Path,
    callback: Callable,
    operation_name: str,
    progress_callback: Optional[Callable[[str], None]] = None,
    monitor_local: bool = True,
    monitor_b10fs: bool = True,
    **callback_kwargs,
) -> str:
    return _transfer_manager.start_transfer_async(
        source=source,
        dest=dest,
        callback=callback,
        operation_name=operation_name,
        progress_callback=progress_callback,
        monitor_local=monitor_local,
        monitor_b10fs=monitor_b10fs,
        **callback_kwargs,
    )


def get_transfer_status(operation_id: str) -> Optional[TransferProgress]:
    return _transfer_manager.get_transfer_status(operation_id)


def is_transfer_complete(operation_id: str) -> bool:
    return _transfer_manager.is_transfer_complete(operation_id)


def wait_for_completion(operation_id: str, timeout: Optional[float] = None) -> bool:
    return _transfer_manager.wait_for_completion(operation_id, timeout)


def cancel_transfer(operation_id: str) -> bool:
    return _transfer_manager.cancel_transfer(operation_id)


def list_active_transfers() -> Dict[str, TransferProgress]:
    return _transfer_manager.list_active_transfers()
