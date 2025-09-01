import os
from pathlib import Path

import click

from synapse_sdk.clients.agent import AgentClient
from synapse_sdk.clients.backend import BackendClient
from synapse_sdk.plugins.models import PluginRelease
from synapse_sdk.plugins.utils import read_requirements, run_plugin


@click.command()
@click.argument('action')
@click.argument('params')
@click.option('--job-id')
@click.option('--direct/--no-direct', default=False)
@click.option('--run-by', type=click.Choice(['script', 'agent', 'backend']), default='script')
@click.option('--agent-host')
@click.option('--agent-token')
@click.option('--host')
@click.option('--agent')
@click.option('--user-token')
@click.option('--tenant')
@click.pass_context
def run(ctx, action, params, job_id, direct, run_by, agent_host, agent_token, host, agent, user_token, tenant):
    debug = ctx.obj['DEBUG']

    if run_by == 'script':
        run_by_script(action, params, job_id, direct, debug)
    elif run_by == 'agent':
        run_by_agent(action, params, job_id, agent_host, agent_token, user_token, tenant, debug)
    elif run_by == 'backend':
        run_by_backend(action, params, agent, host, user_token, tenant)


def run_by_script(action, params, job_id, direct, debug):
    requirements = read_requirements('./requirements.txt')
    result = run_plugin(action, params, requirements=requirements, debug=debug, job_id=job_id, direct=direct)

    if debug:
        click.echo(result)


def run_by_agent(action, params, job_id, agent_host, agent_token, user_token, tenant, debug):
    client = AgentClient(agent_host, agent_token, user_token, tenant)
    data = {'action': action, 'params': params}
    plugin_path = os.getcwd()
    requirements = read_requirements(Path(plugin_path) / 'requirements.txt')
    if requirements:
        data = {'requirements': requirements}

    if job_id:
        data['job_id'] = job_id

    if debug:
        data.update({
            'plugin_path': plugin_path,
            'modules': os.getenv('SYNAPSE_DEBUG_MODULES', '').split(','),
        })
        result = client.run_debug_plugin_release(data=data)
    else:
        plugin_release = PluginRelease()
        result = client.run_plugin_release(plugin_release.code, data=data)

    click.echo(result)


def run_by_backend(action, params, agent, host, user_token, tenant):
    client = BackendClient(host, user_token, tenant=tenant)
    plugin_release = PluginRelease()
    data = {'agent': agent, 'version': plugin_release.version, 'action': action, 'params': params}
    result = client.run_plugin(plugin_release.plugin, data=data)

    click.echo(result)
