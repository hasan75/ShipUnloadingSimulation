# ShipUnloadingSimulation
Ships arrive at a harbor with interarrival times that are IID exponential random variables with a mean of 1.25 days. 
The harbor has a dock with two berths and two cranes for unloading the ships; ships arriving when both berths are occupied 
join a FIFO queue. The time for one crane to unload a ship is distributed uniformly between 0.5 and 1.5 days. 
If only one ship is in the harbor, both cranes unload the ship and the (remaining) unloading time is cut in half. 
When two ships are in the harbor, one crane works on each ship. If both cranes are unloading one ship when a second 
ship arrives, one of the cranes immediately begins serving the second ship and the remaining service time of the first ship 
is doubled. Assuming that no ships are in the harbor at time 0, run the simulation for 90 days and 
compute the minimum, maximum, and average time that ships are in the harbor (which includes their time in berth). 
Also estimate the expected utilization of each berth and of the cranes. Use stream 1 for the interarrival times and stream 2 
for the unloading times.
