package com.pricing.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PriceData implements Serializable {
    
    private static final long serialVersionUID = 1L;
    
    private String symbol;
    private Double price;
    private Double bidPrice;
    private Double askPrice;
    private Long volume;
    private Long timestamp;
    private Long receivedAt;
}