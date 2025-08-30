import unittest
import time
from velocity.misc.timer import Timer


class TestTimer(unittest.TestCase):
    def test_initialization(self):
        """Test that a Timer object is initialized with the correct label and zero elapsed time."""
        timer = Timer("Test Timer")
        self.assertEqual(timer._label, "Test Timer")
        self.assertIsNotNone(timer._start)
        self.assertEqual(timer._diff, None)

    def test_start(self):
        """Test that calling start() resets the timer's start time and clears any previous elapsed time."""
        timer = Timer("Test Timer")
        time.sleep(0.1)
        timer.stop()
        initial_diff = timer._diff

        timer.start()
        self.assertEqual(timer._diff, None)  # _diff should be reset
        self.assertNotEqual(timer._start, None)  # start time should be reset
        self.assertLess(
            timer.elapsed(), initial_diff
        )  # elapsed time should be smaller after restart

    def test_stop(self):
        """Test that stop() records the correct elapsed time."""
        timer = Timer("Test Timer")
        time.sleep(0.1)
        timer.stop()
        self.assertGreater(timer._diff, 0)
        self.assertAlmostEqual(
            timer._diff, timer.elapsed(), delta=0.01
        )  # check recorded time

    def test_elapsed_during_run(self):
        """Test that elapsed() shows increasing time while the timer is running."""
        timer = Timer("Test Timer")
        time.sleep(0.1)
        elapsed_1 = timer.elapsed()
        time.sleep(0.1)
        elapsed_2 = timer.elapsed()
        self.assertGreater(elapsed_2, elapsed_1)  # time should increase while running

    def test_str_running_timer(self):
        """Test the __str__ representation while the timer is running."""
        timer = Timer("Running Timer")
        time.sleep(0.1)
        output = str(timer)
        self.assertIn("Running Timer:", output)
        self.assertIn("s", output)  # Should include seconds in the output

    def test_str_stopped_timer(self):
        """Test the __str__ representation after stopping the timer."""
        timer = Timer("Stopped Timer")
        time.sleep(0.1)
        timer.stop()
        output = str(timer)
        self.assertIn("Stopped Timer:", output)
        self.assertIn("s", output)  # Should include seconds in the output
        self.assertEqual(float(output.split(": ")[1][:-2]), float(f"{timer._diff:.4f}"))

    def test_stop_without_start_error(self):
        """Test that stopping a timer without starting it does not raise errors."""
        timer = Timer("Test Timer")
        timer.start()  # reset start
        timer.stop()
        self.assertGreater(timer._diff, 0)  # timer should stop correctly


if __name__ == "__main__":
    unittest.main()
