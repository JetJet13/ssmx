import boto3
import click
import re
from os import environ
from tabulate import tabulate
from subprocess32 import Popen

@click.group()
@click.version_option()
def cli():
    """
    ssmx is a CLI tool for injecting parameters stored in AWS SSM into executables.
    It also provides commands to retrieve and set parameters in AWS SSM.
    """




def list_params(names, profile, region):
    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client('ssm')
    if names:
        filters = [{"Key": "Name", "Values": names}]
    # The whole list needs to be empty
    else:
        filters = []
    try:
        paginator = client.get_paginator('describe_parameters')
        response_iterator = paginator.paginate(Filters=filters)
    except Exception as e:
        click.echo("Error listing parameters:")
        click.echo(e.message)
        exit(1)

    output = []
    for page in response_iterator:
        for param in page['Parameters']:
            if 'Description' not in param:
                param['Description'] = ''
            output.append(dict(Name=param.get('Name'), Description=param.get('Description')))
    return output

@cli.command(name="list")
@click.option('--name', '-n', metavar='<name>', multiple=True, help='Show parameters starting with <name>')
@click.option('--profile', '-p', metavar='<profile>', required=False, help='an aws profile')
@click.option('--region', '-r', metavar='<region>', required=False, help='aws Region, i.e. us-east-1')
def list(name, profile, region):
    """List available parameters."""
    output = list_params(name, profile, region)
    if output:
            click.echo(tabulate({'Name': [item['Name'] for item in output],
                                'Description': [item['Description'] for item in output]},
                                headers='keys', tablefmt='grid'))
    else:
        click.echo("No parameters found.")





def delete_params(names, profile, region):
    session = boto3.Session(profile_name=profile, region_name=region)
    client = boto3.client('ssm')
    try:
        response = client.delete_parameters(Names=names)
    # TODO: catch  exceptions
    except Exception as e:
        click.echo("Error deleting parameters:")
        click.echo(e.message)
        exit(1)
    return response.get('DeletedParameters'), response.get('InvalidParameters')

@cli.command(name="delete")
@click.option('--name', '-n', metavar='<name>', multiple=True, required=True, help='Name of the parameter to delete')
@click.option('--profile', '-p', metavar='<profile>', required=False, help='an aws profile')
@click.option('--region', '-r', metavar='<region>', required=False, help='aws Region, i.e. us-east-1')
def delete(name, profile, region):
    """Delete parameters with <name>."""
    output, err = delete_params(name, profile, region)
    # Print if specified otherwise return output
    if output:
        click.echo(tabulate({'Deleted Parameters': output}, headers='keys', tablefmt='grid'))
    if err:
        click.echo(tabulate({'Invalid Parameters': err}, headers='keys', tablefmt='grid'))






def get_params(names, profile, region):
    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client('ssm')
    try:
        response = client.get_parameters(Names=names, WithDecryption=True)
    except Exception as e:
        click.echo("Error getting parameters")
        click.echo(e.message)
        exit(1)
    return response.get('Parameters'), response.get('InvalidParameters')

@cli.command(name="get")
@click.option('--name', '-n', metavar='<name>', multiple=True, required=True, help='Name of the parameter to retrieve')
@click.option('--profile', '-p', metavar='<profile>', required=False, help='an aws profile')
@click.option('--region', '-r', metavar='<region>', required=False, help='aws Region, i.e. us-east-1')
def get(name, profile, region, print_output=True):
    """Retrieve values of parameters with <name>."""
    output, err = get_params(name, profile, region)
    if output:
        click.echo(tabulate({'Name': [param['Name'] for param in output],
                             'Value': [param['Value']for param in output]},
                            headers='keys', tablefmt='grid'))
    if err:
        click.echo(tabulate({'Invalid Parameters': [param for param in err]},
                            headers='keys', tablefmt='grid'))







def put_param(name, value, encrypt, key_id, profile, region, description):
    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client('ssm')
    if encrypt:
        if key_id is None:
            click.echo("Heads Up! I'm unable to encrypt without specifying a KMS Key ID; Retry with --key-id <KMS_KEY_ID>")
            exit(1)
        param_type = 'SecureString'
    else:
        if key_id:
            click.echo("Heads Up! --key-id is required only when --encrypt is specified.")
            exit(1)
        param_type = 'String'
    try:
        if key_id:
            client.put_parameter(Name=name, Value=value, Description=description,
                                 Overwrite=True, Type=param_type, KeyId=key_id)
        else:
            client.put_parameter(Name=name, Value=value, Overwrite=True, Description=description, Type=param_type)
    except Exception as e:
        click.echo("Error putting parameters")
        click.echo(e.message)
        exit(1)
    # return the name of the variable in case of success
    return name

@cli.command(name="put", help='Upsert parameters')
@click.option('--name', '-n', metavar='<name>', required=True, help='Name of the parameter')
@click.option('--value', '-v', metavar='<value>', required=True, help='Value of the parameter')
@click.option('--description', '-d', metavar='<description>', default="", help='Description for the parameter')
@click.option('--encrypt', '-e', is_flag=True, default=False, help='Encrypt the parameter')
@click.option('--key-id', '-k', metavar='<key_id>', required=False, help='KMS Key ID to encrypt. Required option if --encrypt is used.')
@click.option('--profile', '-p', metavar='<profile>', required=False, help='an aws profile')
@click.option('--region', '-r', metavar='<region>', required=False, help='aws Region, i.e. us-east-1')
def put(name, value, encrypt, description, key_id, profile, region):
    """Put parameter with name <name>, value <value> and description <description>. Optionally encrypt the parameter."""
    output = put_param(name=name, value=value, description=description, encrypt=encrypt, key_id=key_id, profile=profile, region=region)
    if output:
        click.echo(tabulate({'Created Parameters': [output]}, headers='keys', tablefmt='grid'))






def get_param(name, profile, region):
    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client('ssm')
    try:
        response = client.get_parameter(Name=name, WithDecryption=True)
    # TODO: catch  exceptions
    except Exception as e:
        click.echo("Error getting parameters")
        click.echo(e.message)
        click.echo('Parameter Name: %s' % name)
        exit(1)
    return response.get('Parameter')

def get_parameters_by_path(path, profile, region):
    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client('ssm')
    try:
        paginator = client.get_paginator('get_parameters_by_path')
        response_iterator = paginator.paginate(Path=path, Recursive=True, WithDecryption=True)
    except Exception as e:
        click.echo("Error listing parameters:")
        click.echo(e.message)
        exit(1)

    output = []
    for page in response_iterator:
        for param in page['Parameters']:
            if 'Description' not in param:
                param['Description'] = ''
            output.append(dict(Name=param.get('Name'), Value=param.get('Value')))
    return output


def formatKey(input):
    """
    formatKey converts the parameter key stored in ssm into
    the traditional env. variable key format

    examples:
    /my-app/foo.bar -> FOO_BAR
    /my-app/dev/hello-world -> HELLO_WORLD
    /my-app/sbx/alpha/job_one -> JOB_ONE
    """
    paths = input.split('/')
    keyName = paths[-1] # last item is key name
    formattedKey = re.sub(r'[\.\-\_]', '_', keyName).upper()
    return formattedKey

@cli.command(name="exec", help='Inject env variables into an executable')
@click.argument('command', nargs=-1, required=False, type=click.UNPROCESSED)
@click.option('--env-file', '-f', metavar='<env_file>', required=False, help='filepath for .env file')
@click.option('--name', '-n', metavar='<name>', required=False, help='prefix-name of parameters, i.e. /<prefix-name>/hello-world')
@click.option('--profile', '-p', metavar='<profile>', required=False, help='an aws profile')
@click.option('--region', '-r', metavar='<region>', required=False, help='aws Region, i.e. us-east-1')
def execute(command, env_file, name, profile, region):
    """Inject env. variables into an executable via <name> and/or <env_file>"""

    # command is a tuple
    if len(command) == 0:
        click.echo("nothing to execute")
        return
    
    env_dict = {}
    if env_file:
        env_vars = []
        f = open(env_file, 'r')
        for line in f:
            if line.startswith('#'):
                continue
            key, value = line.strip().split('=', 1)
            env_vars.append({'name': key, 'value': value})
        for env_var in env_vars:
            key = env_var['name']
            value = env_var['value']
            if value.startswith('ssm:'):
                secretKey = value[6:]
                out = get_param(secretKey, profile, region)
                env_var['value'] = out['Value']

        for env_var in env_vars:
            key = env_var['name']
            value = env_var['value']
            env_dict[key] = value
            click.echo("injected %s" % key)

    if name:
        env_vars = []
        if name[0] == '/':
            path = name
        else:
            path = '/' + name
        params = get_parameters_by_path(path, profile, region)
        for param in params:
            key = formatKey(param['Name'])
            formatKey(key)
            value = param['Value']
            env_dict[key] = value
            click.echo("injected %s" % key)

    cmd_env = environ.copy()
    cmd_env.update(env_dict)

    p = Popen(command,
            universal_newlines=True,
            bufsize=0,
            shell=False,
            env=cmd_env)
    _, _ = p.communicate()

    return p.returncode