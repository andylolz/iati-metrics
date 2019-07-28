# Parallel Registry Refresher

This is a task-based IATI data downloader. Add downloaded data gets pushed to Amazon S3.

## Usage

```
heroku scale worker=1
heroku run python run.py enqueue
```
