# DynamoDB Usage

## Entities

1. `WordGame`: the word of the day created by using a random word
2. `GameTurn`: attempts a user makes to win the game of the day

## Access Patterns

1. Get user attempts for a specific game
2. Get Word Game on a specific date
3. Get all Game Turns for a user

## Indices

- Table Index
  - Partition Key: `username`
  - Sort Key: `timestamp`