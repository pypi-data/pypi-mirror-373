import unittest
from unittest.mock import patch, MagicMock
from wintop.wintop import WinTop

class TestWinTop(unittest.TestCase):
    def setUp(self):
        self.wintop = WinTop(update_interval=0.1, process_limit=5)

    def test_format_bytes(self):
        self.assertEqual(self.wintop.format_bytes(0), "   0B")
        self.assertEqual(self.wintop.format_bytes(1023), "1023.0B")
        self.assertEqual(self.wintop.format_bytes(1024), "   1.0K")
        self.assertEqual(self.wintop.format_bytes(1024 * 1024), "   1.0M")

    def test_format_rate(self):
        self.assertEqual(self.wintop.format_rate(999), "   999B/s")
        self.assertEqual(self.wintop.format_rate(1024), "     1K/s")
        self.assertEqual(self.wintop.format_rate(1024 * 1024), "     1M/s")

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_partitions')
    @patch('psutil.disk_usage')
    def test_get_system_info(self, mock_disk_usage, mock_disk_partitions, 
                           mock_virtual_memory, mock_cpu_percent):
        # Setup mocks
        mock_cpu_percent.return_value = 50.0
        mock_virtual_memory.return_value = MagicMock(
            total=8589934592, used=4294967296, percent=50.0
        )
        mock_disk_partitions.return_value = [MagicMock(mountpoint='C:\\')]
        mock_disk_usage.return_value = MagicMock(
            total=107374182400, used=53687091200, free=53687091200, percent=50.0
        )

        info = self.wintop.get_system_info()
        self.assertEqual(info['cpu']['percent'], 50.0)
        self.assertEqual(info['memory']['percent'], 50.0)
        self.assertEqual(info['disk'].percent, 50.0)

    def test_run_terminates(self):
        with patch.object(self.wintop, 'running', new_callable=lambda: [True, False]):
            with patch.object(self.wintop, 'get_system_info') as mock_info:
                with patch.object(self.wintop, 'get_processes_with_io') as mock_procs:
                    mock_info.return_value = {}
                    mock_procs.return_value = []
                    self.wintop.run()  # Should terminate after one iteration

if __name__ == '__main__':
    unittest.main()