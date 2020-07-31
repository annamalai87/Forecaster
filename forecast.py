import bisect
import operator
import sys
from collections import OrderedDict
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd
from openpyxl import load_workbook

from model import (Allocation, Feature, Team, TeamPriority, TeamWeek, TeamWeeklyAllocations)

# Global variables
teams: Dict[str, Team] = {}
features: Dict[str, Feature] = {}
allocations: Dict[str, Allocation] = {}


# Extract team data from the excel sheet
def extract_teams(file: str):
    global teams
    excel_data = pd.read_excel(
        io=file, sheet_name='Team', index_col=0, header=0)

    # Dropping rows containing blank values
    excel_data.dropna(how="any", inplace=True)

    for data in excel_data.itertuples():
        teams[data[0]] = Team(name=data[0], head_count=data[1],
                              productivity=data[2], week_capacity=data[3])


# Extract features data from the excel sheet
def extract_features(file: str):
    global features
    excel_data = pd.read_excel(
        io=file, sheet_name='Feature', index_col=0, header=0)

    # Dropping rows containing blank values
    excel_data.dropna(how="any", inplace=True)

    for data in excel_data.itertuples():
        features[data[0]] = Feature(
            name=data[0], priority=data[1], total_efforts=data[2])


# Extract planning data from the excel sheet
def extract_planning(file: str):
    global allocations

    # Indexing both feature and team name
    excel_data = pd.read_excel(
        io=file, sheet_name='Planning', index_col=[0, 1], header=0)

    # Dropping rows containing blank values
    excel_data.dropna(how="any", inplace=True)

    for data in excel_data.itertuples():
        allocations[data[0][0] + data[0][1]] = Allocation(
            team_name=data[0][0], feature_name=data[0][1], efforts=data[1])


# Group features based on its priorities and team.
def group_team_feature_prioritizations():

    # Two types of sorts are done:
    #       1. For every priority level for a given team, features are sorted based on its effort required for that team
    #       2. Team and its priority are sorted
    # Sample data:
    #   Team1   Priority1   [Feature1, Feature3]
    #   Team1   Priority2   [Feature2]
    #   Team2   Priority1   [Feature3]

    prioritizations = {}
    for _, allocation in allocations.items():
        team_priority = TeamPriority(
            team_name=allocation.team_name, priority=features[allocation.feature_name].priority)
        if prioritizations.get(team_priority) == None:
            flist = [allocation]
            prioritizations[team_priority] = flist
        else:
            flist1 = prioritizations.get(team_priority)
            bisect.insort(flist1, allocation)

    return OrderedDict(
        sorted(prioritizations.items(), key=lambda x: x[0]))


def add_to_weekly_allocations(weekly_Allocation: Dict[TeamWeek, TeamWeeklyAllocations], team_weekly_allocations: TeamWeeklyAllocations):
    if weekly_Allocation.get(team_weekly_allocations.team_week) == None:
        weekly_Allocation[team_weekly_allocations.team_week] = team_weekly_allocations
    return weekly_Allocation


def forecast(prioritizations: Dict[TeamPriority, List[Allocation]]):
    start_week = 1
    current_allocated_week = 1
    last_allocated_week = 1
    last_allocated_team: str = ""

    weekly_allocation: Dict[TeamWeek, TeamWeeklyAllocations] = {}

    # Loop through each team and their prioritized features
    for team_priority, allocations in prioritizations.items():

        # When we move to next prioritized allocations for the same team, use last allocated week; Otherwise start from the very beginning.
        if last_allocated_team == team_priority.team_name:
            current_allocated_week = last_allocated_week
        else:
            current_allocated_week = start_week
            last_allocated_team = team_priority.team_name

        allocations_end: Dict[int, int] = {}
        remaining_features = len(allocations)
        week_capacity = teams[team_priority.team_name].week_capacity

        # Loop through each allocated features that has the same priority for the team.
        for allocation in iter(allocations):
            effort = allocation.efforts

            # Increment the week until the effort for the feature is consumed for the team.
            while(effort > 0):
                team_week = TeamWeek(
                    team_name=team_priority.team_name, week=current_allocated_week)
                weekly_allocation = add_to_weekly_allocations(weekly_allocation, TeamWeeklyAllocations(
                    team_week=team_week, features_allocation=[], remaining_efforts=week_capacity))

                if allocations_end.get(current_allocated_week) != None:
                    remaining_features -= 1

                can_consume = week_capacity/remaining_features
                team_weekly_allocations = weekly_allocation.get(team_week)

                # If the previously allocated feature does not consume the entire efforts,
                # use the remaining efforts for that week before moving to the next week.
                if team_weekly_allocations.remaining_efforts < can_consume:
                    can_consume = team_weekly_allocations.remaining_efforts
                
                if effort >= can_consume:
                    effort = effort - can_consume
                    team_weekly_allocations.remaining_efforts -= can_consume
                    allocation_per_week = Allocation(team_name=team_week.team_name, feature_name=allocation.feature_name, efforts=can_consume)
                    current_allocated_week += 1
                else:
                    team_weekly_allocations.remaining_efforts -= effort
                    allocation_per_week = Allocation(team_name=team_week.team_name, feature_name=allocation.feature_name, efforts=effort)
                    effort = 0
                
                team_weekly_allocations.features_allocation.append(allocation_per_week)


            allocations_end[current_allocated_week] = 1
            last_allocated_week = current_allocated_week
            current_allocated_week = start_week
    
    return weekly_allocation

def write_excel(forecasted_work: Dict[TeamWeek,TeamWeeklyAllocations], excel_file_name:str):
    col_feature = []
    col_rank = []
    col_week = []
    col_capacity = []
    col_team = []

    for team_week, team_weekly_allocations in forecasted_work.items():
        for allocation in iter(team_weekly_allocations.features_allocation):
            
            col_feature.append(allocation.feature_name)
            col_rank.append(features.get(allocation.feature_name).priority)
            col_week.append('Week ' + str(team_week.week))
            col_capacity.append(allocation.efforts)
            col_team.append(allocation.team_name)
    
    book = load_workbook(excel_file_name)
    df = pd.DataFrame({'Feature': col_feature, 'Rank': col_rank, 'Week': col_week, 'Week Capacity': col_capacity, 'Team': col_team})
    writer = pd.ExcelWriter(excel_file_name)
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    df.to_excel(writer, sheet_name='Pivot Data',index=False)
    writer.save()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide path to the input file")
        exit(1)
    
    excel_file_name = sys.argv[1]

    # Extract data
    extract_teams(excel_file_name)
    extract_features(excel_file_name)
    extract_planning(excel_file_name)

    # Process data
    prioritizations: Dict[TeamPriority, List[Allocation]] = group_team_feature_prioritizations()
    forecasted_work: Dict[TeamWeek,TeamWeeklyAllocations] = forecast(prioritizations)

    # Write data
    write_excel(forecasted_work,excel_file_name)
