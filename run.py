from datetime import datetime

import click
from rq import Queue

from worker import conn
import utils


@click.group()
def cli():
    pass


@cli.command()
def enqueue():
    """Enqueue all datasets."""
    q = Queue('low', connection=conn)
    q.enqueue(utils.enqueue, result_ttl=0)


@cli.command()
def status():
    """Show how many items remain in each queue."""
    time_now = str(datetime.utcnow())
    click.echo(f'It is {time_now}')
    click.echo('')

    low_q = Queue('low', connection=conn)
    default_q = Queue('default', connection=conn)
    high_q = Queue('high', connection=conn)
    total_low = len(low_q)
    total_default = len(default_q)
    total_high = len(high_q)
    click.echo('Current queue status:')
    click.echo(f'      Low: {total_low} items')
    click.echo(f'  Default: {total_default} items')
    click.echo(f'     High: {total_high} items')
    click.echo('')

    total_failed_low = len(low_q.failed_job_registry)
    total_failed_default = len(default_q.failed_job_registry)
    total_failed_high = len(high_q.failed_job_registry)
    click.echo('Failed queue status:')
    click.echo(f'      Low: {total_failed_low} items')
    click.echo(f'  Default: {total_failed_default} items')
    click.echo(f'     High: {total_failed_high} items')


if __name__ == '__main__':
    cli()
