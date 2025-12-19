package com.pricing.config;

import com.google.common.util.concurrent.RateLimiter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RateLimitConfig {
    
    @Bean
    public RateLimiter rateLimiter() {
        // 10,000 requests per second
        return RateLimiter.create(10000.0);
    }
}