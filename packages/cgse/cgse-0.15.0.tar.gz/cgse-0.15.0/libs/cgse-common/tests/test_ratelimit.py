import pytest
import logging
from io import StringIO
from unittest.mock import patch, MagicMock
from contextlib import redirect_stdout

# Import the module we're testing
from egse.ratelimit import RateLimiter, rate_limit, rate_limited, rate_limited_print, rate_limited_log, _global_limiter


pytestmark = pytest.mark.skipif(True, reason="this file is not ready for testing yet")


class TestRateLimiter:
    """Test the RateLimiter class."""

    def test_initialization(self):
        """Test RateLimiter initializes with empty counters."""
        limiter = RateLimiter()
        assert len(limiter.counters) == 0
        assert len(limiter.last_executed) == 0
        assert len(limiter.suppressed_count) == 0

    def test_should_execute_basic(self):
        """Test basic should_execute functionality."""
        limiter = RateLimiter()

        # First call should not execute (1 % 3 != 0)
        should_execute, suppressed = limiter.should_execute("test", 3)
        assert not should_execute
        assert suppressed == 0

        # Second call should not execute (2 % 3 != 0)
        should_execute, suppressed = limiter.should_execute("test", 3)
        assert not should_execute
        assert suppressed == 0

        # Third call should execute (3 % 3 == 0)
        should_execute, suppressed = limiter.should_execute("test", 3)
        assert should_execute
        assert suppressed == 2  # Two previous calls were suppressed

    def test_should_execute_multiple_keys(self):
        """Test that different keys have independent counters."""
        limiter = RateLimiter()

        # Test key1
        should_execute, _ = limiter.should_execute("key1", 2)
        assert not should_execute
        should_execute, suppressed = limiter.should_execute("key1", 2)
        assert should_execute
        assert suppressed == 1

        # Test key2 (should be independent)
        should_execute, _ = limiter.should_execute("key2", 2)
        assert not should_execute
        should_execute, suppressed = limiter.should_execute("key2", 2)
        assert should_execute
        assert suppressed == 1

    def test_reset_specific_key(self):
        """Test resetting a specific key."""
        limiter = RateLimiter()

        # Build up some state
        limiter.should_execute("key1", 3)
        limiter.should_execute("key2", 3)

        assert limiter.counters["key1"] == 1
        assert limiter.counters["key2"] == 1

        # Reset only key1
        limiter.reset("key1")
        assert limiter.counters["key1"] == 0
        assert limiter.counters["key2"] == 1

    def test_reset_all_keys(self):
        """Test resetting all keys."""
        limiter = RateLimiter()

        # Build up some state
        limiter.should_execute("key1", 3)
        limiter.should_execute("key2", 3)

        assert len(limiter.counters) == 2

        # Reset all
        limiter.reset()
        assert len(limiter.counters) == 0


class TestRateLimitDecorator:
    """Test the @rate_limit decorator."""

    def test_decorator_basic_functionality(self):
        """Test basic decorator functionality."""
        call_count = 0

        @rate_limit(every_n=3, key="test_func")
        def test_func():
            nonlocal call_count
            call_count += 1
            return call_count

        # Call function 6 times
        results = []
        for i in range(6):
            result = test_func()
            results.append(result)

        # Should only execute on calls 3 and 6 (every 3rd call)
        expected_results = [None, None, 1, None, None, 2]
        assert results == expected_results
        assert call_count == 2

    def test_decorator_with_arguments(self):
        """Test decorator works with function arguments."""
        executed_args = []

        @rate_limit(every_n=2, key="test_args")
        def test_func(x, y=None):
            executed_args.append((x, y))
            return x + (y or 0)

        # Call with different arguments
        test_func(1, y=2)  # Not executed (1st call)
        test_func(3, y=4)  # Executed (2nd call)
        test_func(5, y=6)  # Not executed (3rd call)
        test_func(7, y=8)  # Executed (4th call)

        assert executed_args == [(3, 4), (7, 8)]

    def test_decorator_utility_methods(self):
        """Test decorator adds utility methods."""

        @rate_limit(every_n=2, key="test_utils")
        def test_func():
            pass

        # Test get_count method
        assert test_func.get_count() == 0
        test_func()
        assert test_func.get_count() == 1
        test_func()
        assert test_func.get_count() == 2

        # Test reset method
        test_func.reset()
        assert test_func.get_count() == 0

    def test_decorator_suppressed_output(self):
        """Test decorator shows suppressed messages."""

        @rate_limit(every_n=3, key="test_suppressed", show_suppressed=True)
        def test_func():
            return "executed"

        with patch("builtins.print") as mock_print:
            # Call function 6 times
            for i in range(6):
                test_func()

            # Should print suppressed message twice (after 3rd and 6th calls)
            expected_calls = [
                (("... 2 more similar messages suppressed",),),
                (("... 2 more similar messages suppressed",),),
            ]
            assert mock_print.call_args_list == expected_calls


class TestRateLimitedContextManager:
    """Test the rate_limited context manager."""

    def test_context_manager_basic(self):
        """Test basic context manager functionality."""
        execution_count = 0

        for i in range(5):
            with rate_limited(every_n=3, key="test_cm") as should_execute:
                if should_execute:
                    execution_count += 1

        assert execution_count == 1  # Only executed on 3rd iteration

    def test_context_manager_requires_key(self):
        """Test context manager requires a key parameter."""
        with pytest.raises(ValueError, match="Context manager requires a unique 'key' parameter"):
            with rate_limited(every_n=2) as should_execute:
                pass

    def test_context_manager_suppressed_output(self):
        """Test context manager shows suppressed messages."""
        with patch("builtins.print") as mock_print:
            for i in range(4):
                with rate_limited(every_n=2, key="test_cm_suppressed") as should_execute:
                    if should_execute:
                        pass  # Do something when executed

            # Should print suppressed message twice (after 2nd and 4th calls)
            expected_calls = [
                (("... 1 more similar operations suppressed",),),
                (("... 1 more similar operations suppressed",),),
            ]
            assert mock_print.call_args_list == expected_calls


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_rate_limited_print(self):
        """Test rate_limited_print function."""
        with patch("builtins.print") as mock_print:
            # Call rate_limited_print multiple times
            for i in range(5):
                rate_limited_print(f"Message {i}", every_n=3, key="test_print")

            # Should only print on the 3rd call, plus suppressed message
            expected_calls = [(("Message 2",),), (("... 2 more similar operations suppressed",),)]
            assert mock_print.call_args_list == expected_calls

    def test_rate_limited_print_auto_key(self):
        """Test rate_limited_print with automatic key generation."""
        with patch("builtins.print") as mock_print:
            # Same message should use same auto-generated key
            for i in range(4):
                rate_limited_print("Same message", every_n=2)

            # Should print twice (2nd and 4th calls) plus suppressed messages
            assert mock_print.call_count == 4  # 2 messages + 2 suppressed notifications

    def test_rate_limited_log(self):
        """Test rate_limited_log function."""
        # Create a logger and capture its output
        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.INFO)

        # Create a string stream to capture log output
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

        try:
            # Call rate_limited_log multiple times
            for i in range(6):
                rate_limited_log(logger, logging.WARNING, "Test warning message", every_n=3, key="test_log")

            # Get the log output
            log_output = log_stream.getvalue()

            # Should contain 2 warning messages (3rd and 6th calls)
            # Second message should include suppressed count
            assert "Test warning message" in log_output
            assert "2 more similar messages suppressed" in log_output

        finally:
            logger.removeHandler(handler)


class TestCustomLimiter:
    """Test using custom RateLimiter instances."""

    def test_custom_limiter_isolation(self):
        """Test that custom limiters are isolated from global limiter."""
        custom_limiter = RateLimiter()

        @rate_limit(every_n=2, key="test", limiter=custom_limiter)
        def custom_func():
            return "executed"

        @rate_limit(every_n=2, key="test")  # Uses global limiter
        def global_func():
            return "executed"

        # Both functions use same key but different limiters
        # So they should have independent counters

        # Call each function once (shouldn't execute)
        assert custom_func() is None
        assert global_func() is None

        # Call each function again (should execute)
        assert custom_func() == "executed"
        assert global_func() == "executed"

        # Verify they have independent state
        assert custom_limiter.counters["test"] == 2
        assert _global_limiter.counters["test"] == 2


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_every_n_equals_one(self):
        """Test rate limiting with every_n=1 (should always execute)."""

        @rate_limit(every_n=1, key="always_execute")
        def always_func():
            return "executed"

        # Should execute every time
        for i in range(3):
            assert always_func() == "executed"

    def test_large_every_n(self):
        """Test rate limiting with large every_n value."""

        @rate_limit(every_n=1000, key="rare_execute")
        def rare_func():
            return "executed"

        # Should not execute for first 999 calls
        for i in range(999):
            assert rare_func() is None

        # Should execute on 1000th call
        assert rare_func() == "executed"

    def test_suppressed_count_reset(self):
        """Test that suppressed count resets after execution."""
        limiter = RateLimiter()

        # Build up suppressions
        limiter.should_execute("test", 3)  # 1st call - suppressed
        limiter.should_execute("test", 3)  # 2nd call - suppressed
        should_execute, suppressed = limiter.should_execute("test", 3)  # 3rd call - executed

        assert should_execute
        assert suppressed == 2
        assert limiter.suppressed_count["test"] == 0  # Should be reset

        # Next call should start fresh suppression count
        limiter.should_execute("test", 3)  # 4th call - suppressed
        assert limiter.suppressed_count["test"] == 1


# Integration test
class TestIntegration:
    """Integration tests combining multiple features."""

    def test_mixed_usage_patterns(self):
        """Test using decorator and context manager with same key."""
        execution_count = 0

        @rate_limit(every_n=4, key="mixed_test")
        def decorated_func():
            nonlocal execution_count
            execution_count += 1

        # Mix decorator calls and context manager calls with same key
        for i in range(8):
            if i % 2 == 0:
                decorated_func()  # Even iterations use decorator
            else:
                with rate_limited(every_n=4, key="mixed_test") as should_execute:
                    if should_execute:
                        execution_count += 1

        # Should execute on 4th and 8th total calls
        assert execution_count == 2


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
