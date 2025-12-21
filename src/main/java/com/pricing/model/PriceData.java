package com.pricing.model;

import java.io.Serializable;

public class PriceData implements Serializable {
    
    private static final long serialVersionUID = 1L;
    
    private String symbol;
    private Double price;
    private Double bidPrice;
    private Double askPrice;
    private Long volume;
    private Long timestamp;
    private Long receivedAt;
    
    // Default constructor
    public PriceData() {}
    
    // Getters and Setters
    public String getSymbol() { return symbol; }
    public void setSymbol(String symbol) { this.symbol = symbol; }
    
    public Double getPrice() { return price; }
    public void setPrice(Double price) { this.price = price; }
    
    public Double getBidPrice() { return bidPrice; }
    public void setBidPrice(Double bidPrice) { this.bidPrice = bidPrice; }
    
    public Double getAskPrice() { return askPrice; }
    public void setAskPrice(Double askPrice) { this.askPrice = askPrice; }
    
    public Long getVolume() { return volume; }
    public void setVolume(Long volume) { this.volume = volume; }
    
    public Long getTimestamp() { return timestamp; }
    public void setTimestamp(Long timestamp) { this.timestamp = timestamp; }
    
    public Long getReceivedAt() { return receivedAt; }
    public void setReceivedAt(Long receivedAt) { this.receivedAt = receivedAt; }
}