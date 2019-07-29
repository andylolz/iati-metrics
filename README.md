# Parallel Registry Refresher

This is a task-based IATI data downloader. All downloaded data gets pushed to Amazon S3.

## Setup

You can run this wherever, but here are some instructions to run on [Heroku](https://heroku.com). It assumes you have a Heroku account, and have the [heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed.

 * Create a new app:
   ```
   heroku create [app name]
   ```
 * Create a Redis instance (for managing the task queue)
   ```
   heroku addons:create redistogo:nano
   ```
 * add some AWS environment variables (for hosting the files)
   ```
   heroku config:set AWS_ACCESS_KEY_ID=[AWS access key]
   heroku config:set AWS_SECRET_ACCESS_KEY=[AWS secret key]
   heroku config:set S3_BUCKET_NAME=[name of S3 bucket]
   ```
 * push the app to heroku
   ```
   git push heroku master
   ```
 * Then scale the number of workers. The more you do, the faster it is (but the more it costs!)
   ```
   heroku scale worker=[number of workers]
   ```

## Running

You can start a registry refresh using:
```
heroku run python run.py enqueue
```

You could add this as a cron job, or make it restart on completion so it crawls continuously.

## Status

You can check how many tasks are remaining in the queue using:
```
heroku run python run.py status
```
