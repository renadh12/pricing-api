package com.pricing.controller;

import com.google.common.util.concurrent.RateLimiter;
import com.pricing.model.PriceData;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/prices")
public class PricingApiController {
    
    private static final Logger log = LoggerFactory.getLogger(PricingApiController.class);
    private static final ResponseEntity<PriceData> NOT_FOUND = ResponseEntity.notFound().build();
    private static final ResponseEntity<PriceData> RATE_LIMITED = ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).build();
    
    private final RedisTemplate<String, PriceData> redisTemplate;
    private final RateLimiter rateLimiter;
    
    @Autowired
    public PricingApiController(
            RedisTemplate<String, PriceData> redisTemplate,
            RateLimiter rateLimiter) {
        this.redisTemplate = redisTemplate;
        this.rateLimiter = rateLimiter;
    }
    
    @GetMapping("/{symbol}")
    public ResponseEntity<PriceData> getPrice(@PathVariable String symbol) {
        if (!rateLimiter.tryAcquire()) {
            log.warn("Rate limit exceeded for symbol: {}", symbol);
            return RATE_LIMITED;
        }
        
            String key = "price:" + symbol.toUpperCase();
            PriceData price = redisTemplate.opsForValue().get(key);
            
        if (price == null) {
            log.debug("Price not found for symbol: {}", symbol);
            return NOT_FOUND;
        }
        
        return ResponseEntity.ok(price);
    }
    
    @GetMapping("/batch")
    public ResponseEntity<Map<String, PriceData>> getBatchPrices(
            @RequestParam List<String> symbols) {
        
        if (symbols.isEmpty()) {
            return ResponseEntity.badRequest().build();
        }
        
        if (!rateLimiter.tryAcquire(symbols.size())) {
            log.warn("Rate limit exceeded for batch request with {} symbols", symbols.size());
            return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).build();
        }
        
            List<String> keys = symbols.stream()
                    .map(s -> "price:" + s.toUpperCase())
                    .collect(Collectors.toList());
            
            List<PriceData> prices = redisTemplate.opsForValue().multiGet(keys);
            
            Map<String, PriceData> result = new HashMap<>();
            for (int i = 0; i < symbols.size(); i++) {
                if (prices != null && prices.get(i) != null) {
                    result.put(symbols.get(i).toUpperCase(), prices.get(i));
                }
            }
            
            return ResponseEntity.ok(result);
    }
    
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Map<String, String> status = new HashMap<>();
        status.put("status", "UP");
        status.put("redis", testRedisConnection() ? "UP" : "DOWN");
        return ResponseEntity.ok(status);
    }
    
    private boolean testRedisConnection() {
        try {
            redisTemplate.hasKey("test");
            return true;
        } catch (Exception e) {
            log.error("Redis connection test failed", e);
            return false;
        }
    }
}