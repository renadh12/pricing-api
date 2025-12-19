package com.pricing.controller;

import com.google.common.util.concurrent.RateLimiter;
import com.pricing.model.PriceData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Controller
public class PriceWebSocketController {
    
    private static final Logger log = LoggerFactory.getLogger(PriceWebSocketController.class);
    
    private final RedisTemplate<String, PriceData> redisTemplate;
    private final RateLimiter rateLimiter;
    private final SimpMessagingTemplate messagingTemplate;
    
    @Autowired
    public PriceWebSocketController(
            RedisTemplate<String, PriceData> redisTemplate,
            RateLimiter rateLimiter,
            SimpMessagingTemplate messagingTemplate) {
        this.redisTemplate = redisTemplate;
        this.rateLimiter = rateLimiter;
        this.messagingTemplate = messagingTemplate;
    }
    
    @MessageMapping("/price/{symbol}")
    @SendTo("/topic/price/{symbol}")
    public PriceData getPrice(@DestinationVariable String symbol) {
        if (!rateLimiter.tryAcquire()) {
            log.warn("Rate limit exceeded for symbol: {}", symbol);
            return null;
        }
        
        String key = "price:" + symbol.toUpperCase();
        return redisTemplate.opsForValue().get(key);
    }
    
    @MessageMapping("/prices/batch")
    @SendTo("/topic/prices/batch")
    public Map<String, PriceData> getBatchPrices(List<String> symbols) {
        if (symbols.isEmpty() || !rateLimiter.tryAcquire(symbols.size())) {
            return new HashMap<>();
        }
        
        Map<String, PriceData> result = new HashMap<>();
        for (String symbol : symbols) {
            String key = "price:" + symbol.toUpperCase();
            PriceData price = redisTemplate.opsForValue().get(key);
            if (price != null) {
                result.put(symbol.toUpperCase(), price);
            }
        }
        
        return result;
    }
}