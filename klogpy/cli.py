from datetime import datetime
from pathlib import Path
from typing import Optional

import click
import parsy

import klogpy.parser as parser
import klogpy.syntax as syntax
from klogpy import __version__
from klogpy.config import CONFIG_DIR, RECORD_STORE, get_local_config
from klogpy.convert import convert_to_csv


@click.command('init')
def _init():
    """Initialize a new record store if it does not exist"""
    created, _ = get_local_config(True)

    if created:
        click.secho(
            f'Created a new record store in {CONFIG_DIR.resolve()}', fg='green'
        )
    else:
        click.echo(f'Record store in {CONFIG_DIR.resolve()} already exists')


@click.command('convert')
@click.option('-t', '--output-type', type=click.Choice(('csv',)), default='csv', help='The format to output to')
@click.option('-o', '--output-file', type=Path,
              help='The file to output write to, defaults to same directory as input_file')
@click.argument('input_file', type=Path)
def _convert(output_type: str, output_file: Optional[Path], input_file: Path):
    """Converts a Klog file to other file formats"""
    if output_file is None:
        out_dir = input_file.parent
        output_file = out_dir / input_file.stem

    with input_file.open('r') as f:
        records = parser.parse(f.read())

    if output_type == 'csv':
        output_file = output_file.parent / f'{output_file.name}.csv'
        convert_to_csv(records, output_file)

    click.secho(f'Converted {input_file.name} to {output_file}')


@click.command('entry', short_help='Manipulate entries for the active day')
@click.pass_context
@click.option('-m', '--message', help='Add a summary to the record')
@click.option('-l', '--list', 'should_list', is_flag=True, help='Print the entries of the currently selected record')
@click.argument('val', type=str, required=False, metavar='[ENTRY]')
def _entry(ctx, message, should_list, val):
    """Manipulate entries for the active day

    \b
    VAL must be a time or range entry
    Some examples of entries:

    \b
    - "2h30m"
    - "10:00am - 12:00pm"
    """
    if should_list:
        _, conf = get_local_config()

        if conf is None:
            click.secho(
                f'Record store ({RECORD_STORE}) does not exist, or file is corrupt',
                fg='red'
            )
            ctx.exit()

        if conf.current_record is None:
            click.echo('Currently no pending records')
            ctx.exit()

        for e in conf.current_record.entries:
            click.echo(e.serialize())

        ctx.exit()

    if val is None:
        click.echo(ctx.get_help(), color=ctx.color)
        ctx.exit()

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
            f'Created a new record store in {CONFIG_DIR.resolve()}', fg='green')
        return

    conf.current_record.entries.append(e)
    conf.commit()

    click.echo(f'Added {e.serialize()}')


@click.group('record', invoke_without_command=True)
@click.pass_context
@click.option('-l', '--list', 'should_list', is_flag=True, help='List all records in the record store')
def _record(ctx, should_list: bool):
    """Create or modify records"""
    if should_list:
        _, conf = get_local_config()

        if conf is None:
            click.secho(
                f'Record store ({RECORD_STORE}) does not exist, or file is corrupt',
                fg='red'
            )
            return

        for i, record in enumerate(conf.records):
            if i == conf.current_record_index:
                click.secho('* ', nl=False, fg='green')
            else:
                click.echo('  ', nl=False)

            click.echo('  '.join(record.serialize().split('\n')))

        return

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help(), color=ctx.color)
        ctx.exit()


@click.command('finalize')
@click.option('-m', '--message', multiple=True)
@click.option('-e', '--edit', is_flag=True)
def _finalize(message, edit):
    """Write the current selected record to the Klog file"""
    _, conf = get_local_config()

    if conf is None:
        click.secho(
            f'Record store ({RECORD_STORE}) does not exist, or file is corrupt', fg='red')
        return

    conf.current_record.summary = [m.strip() for m in message]

    if edit:
        # Add previous message in text buffer if present
        text = click.edit('\n'.join(conf.current_record.summary))

        # Remove empty lines
        conf.current_record.summary = [
            line for line in text.split('\n') if line != '']

    try:
        pushed = conf.write_selected()
    except Exception as e:
        click.secho(str(e), fg='red')
    else:
        click.secho('Successfully added record\n', fg='green')
        click.echo(pushed.serialize())


@click.command('new')
def _new():
    """Create a new record for today"""
    rec = syntax.Record(datetime.today())
    _, conf = get_local_config()

    if conf is None:
        click.secho(
            f'Record store ({RECORD_STORE}) does not exist, or file is corrupt', fg='red')
        return

    conf.push_record(rec)
    conf.commit()


_record.add_command(_finalize)
_record.add_command(_new)


@click.group()
@click.version_option(__version__)
def klg():
    pass


klg.add_command(_init)
klg.add_command(_convert)
klg.add_command(_entry)
klg.add_command(_record)
