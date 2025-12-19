# Pricing API - high frequency (updates per second) + low latency


Updates per second for equity updates (high frequency for writes)
Low latency (reads)

there is a UI
consumed by different consumers (Application to Application)
 - Algorithmic Trading
 - Close to market prices


Smart Order Router - split the orders

Requirements Analysis


API - Springboot Fraemwork


10000 RPS

#  Non blocking 

CompleteableFuture.runAsync()
return Result
    completing the handling the write operation in background
    use a callback/promise to handle the result 

low latency read

Producer > Consumer (handle the backpressure)

Pricing API to enforce rate limiting  

Consumer side - message polling 10000
               - 5 topics across 10 partitions 2k

Throw in a Kafka Consumer

Tech Stack:
    Feeder API --> Kafka < [Data Streaming source] > Redis

    UI -> reads 
    Java Springboot Framework - 
        Pricing API
            - read GetMapping ()
        Smart Order Router: ordering API (microservice)
        AlgoTrading API (microservice)
        Execution API ()
    Kafka as an external resource
    Data Persistence (Redis)

    Single Responsiblity Pattern


    User Flow





