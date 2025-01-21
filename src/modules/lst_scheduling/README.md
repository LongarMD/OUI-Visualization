# LST Scheduling Algorithm

## Core Concepts

### Activities

- Each activity has:
  - Unique ID
  - Duration
  - Dependencies (activities that must complete before this one can start)
  - Required resources
  - ES (Earliest Start time)
  - LS (Latest Start time)
  - Completion status (finished/unfinished)

### Resources

- Resources can be assigned to activities
- Each resource can only be used by one activity at a time
- The system tracks resource availability over time

## Key Algorithm Steps

### 1. Initial Setup

```python
# Calculate ES (Earliest Start) for each activity
- Start with ES = 0 for activities only dependent on "start"
- For other activities: ES = max(dependency.ES + dependency.duration)

# Calculate LS (Latest Start) for each activity
- Start with LS = project_duration for final activities
- For other activities: LS = min(dependent_activity.LS - activity.duration)
```

### 2. Scheduling Loop

```python
while unfinished_activities_exist:
    # Find ready activities (all dependencies completed)
    ready_activities = [a for a in unfinished_activities
                       if all_dependencies_finished(a)]

    # Calculate slack time for each ready activity
    # Slack = Latest Start - Earliest Start
    slack_times = {activity: activity.LS - activity.ES
                  for activity in ready_activities}

    # Select activity with minimum slack
    next_activity = min(slack_times, key=slack_times.get)

    # Find available time slot considering:
    # - Resource availability
    # - Earliest possible start time
    start_time = find_next_available_time(
        required_resources,
        activity_duration,
        earliest_start
    )
```

### 3. Resource Management

- The algorithm maintains a timeline of resource usage
- When scheduling an activity:
  1. Checks when all required resources are available
  2. Reserves resources for the activity's duration
  3. Updates resource availability timeline
