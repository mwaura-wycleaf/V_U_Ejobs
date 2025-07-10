import asyncio
import random
import time
from collections import deque, defaultdict
from statistics import mode

# Event types
EVENT_TYPES = ["fire", "medical", "police"]

# Simulated data for AI prioritization
LOCATIONS = ["Zone A", "Zone B", "Zone C", "Zone D"]
HISTORICAL_URGENCY = {"fire": 10, "medical": 8, "police": 6}
WEATHER_IMPACT = {"Zone A": 2, "Zone B": 1, "Zone C": 3, "Zone D": 2}

# Event object
class Event:
    def _init_(self, event_type, location, timestamp):
        self.event_type = event_type
        self.location = location
        self.timestamp = timestamp
        self.priority = self.assign_priority()

    def assign_priority(self):
        urgency = HISTORICAL_URGENCY[self.event_type]
        weather = WEATHER_IMPACT[self.location]
        time_of_day = self.timestamp % 24
        score = urgency * 2 + weather - abs(12 - time_of_day) // 3
        return score

    def _repr_(self):
        return f"[{self.event_type.upper()} at {self.location} | Priority: {self.priority}]"

# Dispatcher coroutine
async def dispatcher(name, event_queue, log_queue):
    while True:
        if event_queue:
            event = sorted(event_queue, key=lambda e: -e.priority).pop(0)
            log_queue.append((name, event))
            event_queue.remove(event)
        await asyncio.sleep(0.1)

# Event generator coroutine
async def generate_events(dispatch_queues):
    timestamp = 0
    while True:
        event_type = random.choice(EVENT_TYPES)
        location = random.choice(LOCATIONS)
        event = Event(event_type, location, timestamp)
        dispatch_queues[event_type].append(event)
        timestamp += 1
        await asyncio.sleep(random.uniform(0.3, 1.0))

# Scheduler coroutine
async def scheduler(dispatch_queues, log_queue):
    while True:
        top_events = []
        for queue in dispatch_queues.values():
            if queue:
                best = sorted(queue, key=lambda e: -e.priority)[0]
                top_events.append(best)
        if top_events:
            highest = sorted(top_events, key=lambda e: -e.priority)[0]
            dispatcher_name = highest.event_type
            dispatch_queues[dispatcher_name].remove(highest)
            log_queue.append((dispatcher_name, highest))
        await asyncio.sleep(1)

# Predictive AI coroutine
async def predict_resource_allocation(log_queue):
    history = deque(maxlen=20)
    while True:
        if log_queue:
            dispatcher_type, _ = log_queue[-1]
            history.append(dispatcher_type)
        if len(history) >= 5:
            try:
                busiest = mode(history)
                print(f"\n🔮 [AI PREDICTION] Prepare more units for: {busiest.upper()} team.\n")
            except:
                pass
        await asyncio.sleep(5)

# Logger coroutine
async def log_events(log_queue):
    time_step = 0
    while True:
        if log_queue:
            dispatcher_type, event = log_queue.popleft()
            print(f"⏱ {time_step:02d} | Dispatcher: {dispatcher_type.upper()} | Event: {event}")
        time_step += 1
        await asyncio.sleep(1)

# Main execution function
async def main():
    dispatch_queues = {
        "fire": [],
        "medical": [],
        "police": [],
    }
    log_queue = deque()

    await asyncio.gather(
        dispatcher("fire", dispatch_queues["fire"], log_queue),
        dispatcher("medical", dispatch_queues["medical"], log_queue),
        dispatcher("police", dispatch_queues["police"], log_queue),
        generate_events(dispatch_queues),
        scheduler(dispatch_queues, log_queue),
        predict_resource_allocation(log_queue),
        log_events(log_queue),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSimulation stopped.")
