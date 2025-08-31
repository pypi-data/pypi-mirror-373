import datetime
import logging


class TimestampFormatter(logging.Formatter):
    """
    Formatter for timestamps
    """

    def format(self, record):
        """
        Format the specified record as text with the provided date time format.
        Args:
            record: Record to format
        """
        record.asctime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return super().format(record)
