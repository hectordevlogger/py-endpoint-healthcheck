from unittest.mock import MagicMock, patch

from checker import check_endpoint, run_checks


def test_healthy_endpoint():
    mock_resp = MagicMock()
    mock_resp.getcode.return_value = 200
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None

    with patch("checker.urlopen", return_value=mock_resp):
        res = check_endpoint("https://example.com/health")
        assert res.ok is True
        assert res.status_code == 200
        assert res.error is None


def test_run_checks_skips_blank_urls():
    mock_resp = MagicMock()
    mock_resp.getcode.return_value = 204
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None

    with patch("checker.urlopen", return_value=mock_resp):
        results = run_checks(["https://api.example.local", "  ", ""])
        assert len(results) == 1
        assert results[0].ok is True

        * `java-rate-limiter/src/main/java/com/example/ratelimiter/TokenBucketRateLimiter.java`
```java
package com.example.ratelimiter;

import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

public class TokenBucketRateLimiter {

    private final double capacity;
    private final double refillTokensPerSecond;
    private final ConcurrentHashMap<String, Bucket> buckets = new ConcurrentHashMap<>();

    public TokenBucketRateLimiter(double capacity, double refillTokensPerSecond) {
        if (capacity <= 0.0) {
            throw new IllegalArgumentException("Capacity must be greater than zero");
        }
        if (refillTokensPerSecond <= 0.0) {
            throw new IllegalArgumentException("Refill rate must be greater than zero");
        }
        this.capacity = capacity;
        this.refillTokensPerSecond = refillTokensPerSecond;
    }

    public boolean tryAcquire(String key) {
        return tryAcquire(key, 1.0, System.nanoTime());
    }

    public boolean tryAcquire(String key, double tokens, long nowNanos) {
        Objects.requireNonNull(key, "key must not be null");
        if (tokens <= 0.0 || tokens > capacity) {
            throw new IllegalArgumentException("Invalid token request amount: " + tokens);
        }

        Bucket bucket = buckets.computeIfAbsent(key, k -> new Bucket(capacity, nowNanos));
        return bucket.consume(tokens, nowNanos, capacity, refillTokensPerSecond);
    }

    private static final class Bucket {
        private final ReentrantLock lock = new ReentrantLock();
        private double availableTokens;
        private long lastRefillNanos;

        Bucket(double initialTokens, long nowNanos) {
            this.availableTokens = initialTokens;
            this.lastRefillNanos = nowNanos;
        }

        boolean consume(double tokens, long nowNanos, double maxCapacity, double refillRatePerSec) {
            lock.lock();
            try {
                if (nowNanos > lastRefillNanos) {
                    double elapsedSeconds = (nowNanos - lastRefillNanos) / 1_000_000_000.0;
                    double replenished = elapsedSeconds * refillRatePerSec;
                    availableTokens = Math.min(maxCapacity, availableTokens + replenished);
                    lastRefillNanos = nowNanos;
                }

                if (availableTokens >= tokens) {
                    availableTokens -= tokens;
                    return true;
                }
                return false;
            } finally {
                lock.unlock();
            }
        }
    }
}