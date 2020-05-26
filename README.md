# Rest To GraphQL
Convert your existing REST API to GraphQL. This project's aim is to simply the conversion of the existing `REST API` into `GraphQL`
easier. Migrating an `API` to an entirely new stack is not an easy task. It requires a lot of efforts, testing, team-work, etc especially
if the `API` is serving hundreds of thousands of people every minute.

So, **what's the sol. to it?** Well when a developer is trying to migrate something like this, he/she have two options in their pockets.
Either the migration process will be done manually or by using some kind of automated tools like this.

## So, what's the point?
`GraphQL` has gained a lot of popularity during the couple of past years. By using GraphQL we can save a lot of our resources & use them
somewhere else some other meaningful stuff instead of wasting them in a scenerio where the work can be done even with less resources.

## How this project is helpful to me?
Well, this project will take information about your rest API (mostly about listing the end-points) as input & generate a fully fledged
server along with database connectivity of your choise. Here's a overview of technologies supported:

* **Database**: `MongoDB`, `PostgresSQL`, & `MySQL`
* **Server**: `Apollo Server`, & `Flask`
* **Languanges**: `TS`, & `JS` (preferably `TS`)

## How to use it?
* Install the dependencies:
  ```
  pip install -r requirements.txt
  ```
* Edit the `structure.json` file to fill information about your REST API
* Run the `cli.py` file & make some choices about the stack
* And, 🎉 your `GraphQL` server is ready to deploy directly.
