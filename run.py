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
    low_q = Queue('low', connection=conn)
    total_low = len(low_q)
    default_q = Queue('default', connection=conn)
    total_default = len(default_q)
    high_q = Queue('high', connection=conn)
    total_high = len(high_q)
    click.echo('Current queue status:')
    click.echo(f'      Low: {total_low} items')
    click.echo(f'  Default: {total_default} items')
    click.echo(f'     High: {total_high} items')


if __name__ == '__main__':
    cli()
