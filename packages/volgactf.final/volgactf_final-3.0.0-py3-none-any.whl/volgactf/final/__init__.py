# -*- coding: utf-8 -*-
import os

import click

from .flag_api import SubmitResult, GetInfoResult, FlagAPIHelper
from .capsule_api import (
    GetPublicKeyResult, DecodeResult, CapsuleAPIHelper
)
from .service_api import (
    ListResult, GetServiceStatusResult, ServiceAPIHelper
)


def get_api_endpoint():
    return os.getenv('VOLGACTF_FINAL_API_ENDPOINT')


def get_proxy():
    return os.getenv('VOLGACTF_FINAL_PROXY', '') or None


def get_verify():
    str_value = os.getenv('VOLGACTF_FINAL_VERIFY', 'True')
    if str_value in ('True', 'False'):
        return str_value == 'True'
    else:
        return str_value

@click.group()
def cli():
    pass


@cli.group(name='flag')
def flag_cli():
    pass


def print_request_exception(request, exception):
    click.echo(click.style(repr(exception), fg='red'))


def print_flag_submit_results(results):
    for r in results:
        flag_part = click.style(r['flag'], bold=True)
        status_part = None
        if r['code'] == SubmitResult.SUCCESS:
            status_part = click.style(r['code'].name, fg='green')
        else:
            status_part = click.style(r['code'].name, fg='red')
        click.echo(flag_part + ' ' + status_part)


@flag_cli.command(name='submit')
@click.argument('flags', nargs=-1)
def flag_submit(flags):
    h = FlagAPIHelper(get_api_endpoint(),
                      exception_handler=print_request_exception,
                      proxy=get_proxy(), verify=get_verify())
    print_flag_submit_results(h.submit(*flags))


def print_flag_info_results(results):
    for r in results:
        flag_part = click.style(r['flag'], bold=True)
        status_part = None
        extra_part = ''
        if r['code'] == GetInfoResult.SUCCESS:
            status_part = click.style(r['code'].name, fg='green')
            extra_part += click.style('\n  Team: ', bold=True, fg='yellow')
            extra_part += click.style(r['team'])
            extra_part += click.style('\n  Service: ', bold=True, fg='yellow')
            extra_part += click.style(r['service'])
            extra_part += click.style('\n  Round: ', bold=True, fg='yellow')
            extra_part += click.style('{0:d}'.format(r['round']))
            extra_part += click.style(
                '\n  Not before: ', bold=True, fg='yellow')
            extra_part += click.style(
                '{0:%-m}/{0:%-d} {0:%H}:{0:%M}:{0:%S}'.format(r['nbf']))
            extra_part += click.style('\n  Expires: ', bold=True, fg='yellow')
            extra_part += click.style(
                '{0:%-m}/{0:%-d} {0:%H}:{0:%M}:{0:%S}'.format(r['exp']))
        else:
            status_part = click.style(r['code'].name, fg='red')

        click.echo(flag_part + ' ' + status_part + extra_part)


@flag_cli.command(name='info')
@click.argument('flags', nargs=-1)
def flag_info(flags):
    h = FlagAPIHelper(get_api_endpoint(),
                      exception_handler=print_request_exception,
                      proxy=get_proxy(),
                      verify=get_verify())
    print_flag_info_results(h.get_info(*flags))


@cli.group(name='capsule')
def capsule_cli():
    pass


def print_capsule_public_key_result(r):
    if r['code'] == GetPublicKeyResult.SUCCESS:
        click.echo(click.style(r['code'].name, bold=True, fg='green'))
        click.echo(r['public_key'])
    else:
        click.echo(click.style(r['code'].name, bold=True, fg='red'))


@capsule_cli.command(name='public_key')
def capsule_public_key():
    h = CapsuleAPIHelper(get_api_endpoint(), get_proxy(), get_verify())
    print_capsule_public_key_result(h.get_public_key())


def print_capsule_decode_result(r):
    if r['code'] == DecodeResult.SUCCESS:
        click.echo(click.style(r['code'].name, bold=True, fg='green'))
        if 'flag' in r['decoded']:
            click.echo(click.style('Flag: ', bold=True, fg='yellow') +
                       r['decoded']['flag'])
    else:
        click.echo(click.style(r['code'].name, bold=True, fg='red'))


@capsule_cli.command(name='decode')
@click.argument('capsule')
def capsule_decode(capsule):
    h = CapsuleAPIHelper(get_api_endpoint(), get_proxy(), get_verify())
    print_capsule_decode_result(h.decode(capsule))


@cli.group(name='service')
def service_cli():
    pass


def print_service_list_result(r):
    if r['code'] == ListResult.SUCCESS:
        click.echo(click.style(r['code'].name, bold=True, fg='green'))
        for item in r['list']:
            click.echo(click.style('#{0:d} '.format(item['id']), bold=True) + click.style(item['name'], bold=True, fg='yellow'))
    else:
        click.echo(click.style(r['code'].name, bold=True, fg='red'))


@service_cli.command(name='list')
def service_list():
    h = ServiceAPIHelper(get_api_endpoint(), proxy=get_proxy(), verify=get_verify())
    print_service_list_result(h.list())


def print_service_status_results(results):
    for r in results:
        service_part = click.style('#{0:d}'.format(r['service_id']), bold=True)
        status_part = None
        if r['code'] == GetServiceStatusResult.UP:
            status_part = click.style(r['code'].name, fg='green')
        elif r['code'] == GetServiceStatusResult.NOT_UP:
            status_part = click.style(r['code'].name, fg='yellow')
        else:
            status_part = click.style(r['code'].name, fg='red')

        click.echo(service_part + ' ' + status_part)


@service_cli.command(name='status')
@click.argument('service_ids', nargs=-1, type=int)
def service_status(service_ids):
    h = ServiceAPIHelper(get_api_endpoint(),
                      exception_handler=print_request_exception,
                      proxy=get_proxy(), verify=get_verify())
    print_service_status_results(h.get_status(*service_ids))
