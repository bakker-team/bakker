import os
import sys

import click

from bakker.checkpoint import Checkpoint
from bakker.storage import FileSystemStorage, NoUniqueMatchError

from bakker.config import Config, DEFAULT_STORAGE_KEY, DEFAULT_STORAGE_CHOICES, STORAGE_FILE_SYSTEM_PATH


config = Config()

@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option()
def cli():
    """
    Bakker.
    """
    pass


@cli.group('config')
def cli_config():
    """
    Config description.
    """
    pass


@cli_config.command('list')
def cli_config_list():
    items = list(config.items())
    items.sort()
    for key, value in items:
        click.echo(key + ' = ' + value)


@cli_config.command('set')
@click.argument('key')
@click.argument('value')
def cli_config_set(key, value):
    config[key] = value


@cli_config.command('get')
@click.argument('key')
def cli_config_get(key):
    click.echo(key + ' = ' + config[key])


@cli_config.command('unset')
@click.argument('key')
def cli_config_unset(key):
    if key in config:
        del config[key]
    else:
        click.echo('Config does not contain key: ' + key)


@cli.group('list', invoke_without_command=True)
@click.pass_context
def cli_list(ctx):
    """
    List the checkpoints.
    """
    if ctx.invoked_subcommand is None:
        storage_choice = get_storage_choice()
        if storage_choice == 'fs':
            list_fs()


@cli_list.command('fs')
@click.option('--path', default=None)
def cli_list_fs(path):
    list_fs(path)


@cli.group('create', invoke_without_command=True)
@click.option('--name', '-n', 'checkpoint_name')
@click.pass_context
def cli_create(ctx, checkpoint_name):
    if ctx.invoked_subcommand is None:
        storage_choice = get_storage_choice()
        if storage_choice == 'fs':
            create_fs(checkpoint_name, None)
    elif checkpoint_name is not None:
        click.echo(ctx.get_help())
        sys.exit(-1)


@cli_create.command('fs')
@click.option('--path', 'path')
@click.option('--name', '-n', 'checkpoint_name')
def cli_create_fs(path, checkpoint_name):
    create_fs(checkpoint_name, path)


@cli.group('restore', invoke_without_command=True)
@click.option('--identifier', '-i', 'identifier')
@click.pass_context
def cli_restore(ctx, identifier):
    if ctx.invoked_subcommand is None:
        if identifier is None:
            ctx.fail('Missing option "--identifier" / "-i".')
        storage_choice = get_storage_choice()
        if storage_choice == 'fs':
            restore_fs(None, identifier)
    elif identifier is not None:
        click.echo(ctx.get_help())
        sys.exit(-1)


@cli_restore.command('fs')
@click.option('--path')
@click.option('--identifier', '-i', 'identifier', required=True)
def cli_restore_fs(path, identifier):
    restore_fs(identifier, path)


def get_storage_choice():
    if DEFAULT_STORAGE_KEY not in config:
        click.echo('No default storage is defined.')
        click.echo()
        click.echo('Set default storage with:')
        click.echo('\tbakker config set ' + DEFAULT_STORAGE_KEY + ' <storage>')
        click.echo('Available storages: ' + ', '.join(DEFAULT_STORAGE_CHOICES))
        sys.exit(-1)
    storage_choice = config[DEFAULT_STORAGE_KEY]
    if storage_choice not in DEFAULT_STORAGE_CHOICES:
        click.echo('Default storage choice is not available: ' + storage_choice)
        click.echo()
        click.echo('Set default storage with:')
        click.echo('\tbakker config set ' + DEFAULT_STORAGE_KEY + ' <storage>')
        click.echo('Available storages: ' + ', '.join(DEFAULT_STORAGE_CHOICES))
        sys.exit(-1)
    return storage_choice


def get_fs_path():
    if STORAGE_FILE_SYSTEM_PATH not in config:
        click.echo('No default backup folder defined.')
        click.echo()
        click.echo('Set default backup directory with:')
        click.echo('\tbakker config set ' + STORAGE_FILE_SYSTEM_PATH + ' <path>')
        sys.exit(-1)
    return config[STORAGE_FILE_SYSTEM_PATH]


def list_fs(path=None):
    if path is None:
        path = get_fs_path()
    storage = FileSystemStorage(path)
    checkpoint_metas = storage.retrieve_checkpoint_metas()
    if not checkpoint_metas:
        click.echo('No checkpoints found.')
    else:
        for checkpoint_meta in checkpoint_metas:
            echo_checkpoint_meta(checkpoint_meta)


def echo_checkpoint_meta(checkpoint_meta):
    click.echo(checkpoint_meta.checksum)
    click.echo(checkpoint_meta.time)
    click.echo(checkpoint_meta.name)
    click.echo()


def create_fs(checkpoint_name=None, path=None):
    if path is None:
        path = get_fs_path()
    src_path = os.getcwd()
    checkpoint = Checkpoint.build_checkpoint(src_path, checkpoint_name)

    storage = FileSystemStorage(path)
    storage.store(src_path, checkpoint)


def restore_fs(identifier, path=None):
    if path is None:
        path = get_fs_path()
    dst_path = os.getcwd()
    storage = FileSystemStorage(path)
    try:
        storage.retrieve_by_checksum(dst_path, identifier)
    except FileNotFoundError:
        try:
            storage.retrieve_by_name(dst_path, identifier)
        except FileNotFoundError:
            click.echo('No checkpoints matching identifier: ' + identifier)
        except NoUniqueMatchError:
            click.echo('Multiple checkpoints matching identifier: ' + identifier)
    except NoUniqueMatchError:
        click.echo('Multiple checkpoints matching identifier: ' + identifier)
