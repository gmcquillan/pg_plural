# Days of Future Past

## Problem

### Background: what we're solving

#### Counting Tens of Thousands of Events per Second

### Background: what's not working

#### Adding New Dimensions

#### Invariants

#### Altering Schemas

## Solution Exploration

### Postgres

#### Problems

##### Not Particularly Good at Scaling Writes

##### Horizontal Scaling is Quite Difficult

#### PL Proxy

##### From Skype, Mostly Used to Join Data Silos

##### Increase Distribution of Writes

##### Shard Based on Unique Data (Event IDs) Where Possible

## Results

### Layout

#### Hardware Specs

### Proxy Hosts and Shard Hosts

### Anatomy of a Transaction

#### {Transaction Diagram}

#### {Screen Cast of Queries}

### Batching

#### {Screenshot of Simple Batch Logic}

### Deadlocks Detected!

#### {Diagram of how this happens}

### Write Throughput

### Read Latency

### A Note On Tuning

#### Parameters Tuned/Why

## Advantages of Design

### Scales Writes with Comparible Throughput to HBase OLAP

### Retains DDLs, Transactions

### Free OSS.

## Disadvantages

### High Availability

### Adding Capacity Still Difficult

### Transactional Semantics Mean Updates Need to be Communitive and Idempotent

#### HyperLogLog and its Implications

### Advanced Features Needed: Cross table joins

### Table Semantics Become Function Semantics for Queries

### Avoiding Deadlocks Requires Assistance from Clients

## References
