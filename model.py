from datetime import datetime
from typing import Dict
from typing import List


class Team:
    def __init__(self, name: str, head_count: int, productivity: float, week_capacity: float):
        self.name = name
        self.head_count = head_count
        self.productivity = productivity
        self.week_capacity = week_capacity

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return not(self == other)

    def __str__(self):
        return 'Name: ' + self.name + ' ' + \
            'Head count: ' + str(self.head_count) + ' ' + \
            'Productivity: ' + str(self.productivity) + ' ' + \
            'Week capacity: ' + str(self.week_capacity)


class Feature:
    def __init__(self, name: str, priority: int, total_efforts: float):
        self.name = name
        self.priority = priority
        self.total_efforts = total_efforts

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return not(self == other)

    def __lt__(self, other):
        return self.total_efforts < other.total_efforts

    def __str__(self):
        return 'Name: ' + self.name + ' ' + \
            'priority: ' + str(self.priority) + ' ' + \
            'Total efforts: ' + str(self.total_efforts)


class Allocation:
    def __init__(self, team_name: str, feature_name: str, efforts: float):
        self.team_name = team_name
        self.feature_name = feature_name
        self.efforts = efforts

    def __hash__(self):
        return hash(self.team_name + self.feature_name)

    def __eq__(self, other):
        return self.feature_name == other.feature_name and self.team_name == other.team_name

    def __lt__(self, other):
        return (self.efforts) < (other.efforts)

    def __str__(self):
        return 'Team: ' + self.team_name + ' ' + \
            'Feature: ' + self.feature_name + ' ' + \
            'Efforts: ' + str(self.efforts)


class TeamPriority:
    def __init__(self, team_name: str, priority: int):
        self.team_name = team_name
        self.priority = priority

    def __hash__(self):
        return hash(self.team_name + str(self.priority))

    def __eq__(self, other):
        return (self.team_name, str(self.priority)) == (other.team_name, str(other.priority))

    def __lt__(self, other):
        return (self.team_name, str(self.priority)) < (other.team_name, str(other.priority))

    def __str__(self):
        return 'Team: ' + self.team_name + ' ' + \
            'Priority: ' + str(self.priority) + ' '

class TeamWeek:
    def __init__(self, team_name: str, week: int):
        self.team_name = team_name
        self.week = week

    def __hash__(self):
        return hash(self.team_name + str(self.week))

    def __eq__(self, other):
        return (self.team_name, str(self.week)) == (other.team_name, str(other.week))

    def __lt__(self, other):
        return (self.team_name, str(self.week)) < (other.team_name, str(other.week))

    def __str__(self):
        return 'Team: ' + self.team_name + ' ' + \
            'Week: ' + str(self.week) + ' '

class TeamWeeklyAllocations:
    def __init__(self, team_week:TeamWeek, features_allocation: List[Allocation], remaining_efforts: float):
        self.team_week = team_week
        self.features_allocation = features_allocation
        self.remaining_efforts = remaining_efforts

    def __hash__(self):
        return hash(self.team_week) 

    def __eq__(self, other):
        return other is not None and (self.team_week == other.team_week)
    
    def __str__(self):
        return 'Team name: ' + self.team_week.team_name + ' ' + \
            'Week : ' + str(self.team_week.week) + ' ' + \
            'remaining_efforts: ' + str(self.remaining_efforts) + ' '