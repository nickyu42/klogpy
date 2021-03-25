import click
import parsy

import src.parser as parser
import src.syntax as syntax
from src import __version__
from src.config import CONFIG_DIR, get_local_config


@click.command()
@click.option('-m', '--message', type=str)
@click.argument('val', type=str)
def entry(message, val):
    """Manipulate entries for the active day"""
    try:
        time_val = (parser.time_range | parser.duration).parse(val)
    except parsy.ParseError:
        click.secho(
            'Given entry value does not match duration or time range', fg='red')
        return

    e = syntax.Entry(
        time=time_val,
        description=message,
    )

    created, conf = get_local_config(should_create=True)

    if created:
        click.secho(
            f'Created a new config in {CONFIG_DIR.resolve()}', fg='green')
        return

    conf.current_record.entries.append(e)
    conf.store_pending()

    click.echo(f'Added {e.serialize()}')


@click.command('list')
def _list():
    """List all pending entries"""
    created, conf = get_local_config(should_create=True)

    if created:
        click.secho(
            f'Created a new config in {CONFIG_DIR.resolve()}', fg='green')
    else:
        if conf.current_record is None:
            click.echo('Currently no pending records')
            return

        for e in conf.current_record.entries:
            click.echo(e.serialize())


@click.command()
@click.option('-m', '--message', type=str)
def done(message):
    """Push all pending entries"""
    _, conf = get_local_config()

    if conf is None:
        click.secho(f'{CONFIG_DIR.name} does not exist', fg='red')

    try:
        conf.current_record.summary = [message.strip()]
        pushed = conf.push_record()
    except Exception as e:
        click.secho(str(e), fg='red')
    else:
        click.secho('Successfully added record\n', fg='green')
        click.echo(pushed.serialize())


@click.group()
@click.version_option(__version__)
def klg():
    pass


klg.add_command(entry)
klg.add_command(_list)
klg.add_command(done)
