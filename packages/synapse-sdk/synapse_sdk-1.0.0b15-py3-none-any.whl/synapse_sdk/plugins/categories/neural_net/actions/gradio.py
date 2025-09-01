import contextlib
import subprocess
from functools import cached_property
from pathlib import Path

from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod
from synapse_sdk.utils.network import get_available_ports_host


@register_action
class GradioAction(Action):
    name = 'gradio'
    category = PluginCategory.NEURAL_NET
    method = RunMethod.JOB

    @property
    def working_directory(self):
        dir = Path.cwd() / self.config['directory'].replace('.', '/')
        assert dir.is_dir(), f'Working directory {dir} does not exist.'
        return dir

    @property
    def requirements_file(self):
        requirements_file = self.working_directory / 'requirements.txt'
        if requirements_file.exists():
            return requirements_file

    @property
    def tag(self):
        _tag = f'{self.plugin_release.code}-{self.plugin_release.checksum}'
        return _tag.replace('@', '-')

    @cached_property
    def deploy_port(self):
        return get_available_ports_host()

    def deploy(self):
        self.run.log('deploy', 'Start deploying')

        try:
            # Write Dockerfile and requirements.txt
            path_dockerfile = self.write_dockerfile_template()
            self.check_requirements()

            # Build docker image
            self.build_docker_image(path_dockerfile)

            # Run docker image
            self.run_docker_image()
        except Exception as e:
            self.run.log('deploy', f'Error: {e}')
            raise e

    def start(self):
        self.deploy()
        return {'endpoint': f'http://localhost:{self.deploy_port}'}

    def write_dockerfile_template(self):
        dockerfile_path = self.working_directory / 'Dockerfile'

        with open(dockerfile_path, 'w') as f:
            f.write("""FROM python:3.12-slim
WORKDIR /home/user/app

RUN pip install --no-cache-dir pip -U && \\
    pip install --no-cache-dir uvicorn

RUN apt-get update && \\
    apt-get install -y git nmap ffmpeg libsm6 libxext6 libgl1-mesa-glx && \\
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && \\
    apt-get install -y curl && \\
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \\
    apt-get install -y nodejs && \\
    rm -rf /var/lib/apt/lists/* && \\
    apt-get clean

COPY requirements_default.txt .

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements_default.txt

RUN pip install --no-cache-dir -U -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
""")
        return dockerfile_path

    def check_requirements(self):
        default_packages = ['gradio', 'synapse-sdk', 'python-nmap']
        with open(self.working_directory / 'requirements_default.txt', 'a') as f:
            f.write('\n' + '\n'.join(default_packages))

        if self.requirements_file is None:
            with open(self.working_directory / 'requirements.txt', 'a'):
                pass

    def build_docker_image(self, path_dockerfile):
        self.run.log('deploy', 'Start building docker image')
        result = subprocess.run(
            ['docker', 'build', '-t', self.tag, '-f', str(path_dockerfile), '.'],
            cwd=self.working_directory,
            check=True,
        )
        print(result)

    def run_docker_image(self):
        self.run.log('deploy', 'Start running docker image')

        # Check for existing container
        self.run.log('deploy', 'Check for existing container')
        with contextlib.suppress(subprocess.CalledProcessError):
            subprocess.run(['docker', 'stop', self.tag], check=True)
            subprocess.run(['docker', 'rm', self.tag], check=True)

        # Run docker image
        command = [
            'docker',
            'run',
            '-d',
            '--name',
            self.tag,
            '-p',
            f'{self.deploy_port}:7860',
            '-p',
            '8991-8999:8991-8999',
            '--add-host',
            'host.docker.internal:host-gateway',
            '-e',
            'GRADIO_SERVER_NAME=0.0.0.0',
        ]

        # extend synapse env vars
        for key, value in self.envs.items():
            command.extend(['-e', f'{key}={value}'])
        command.append(self.tag)

        self.run.log('deploy', f'Starting docker container with command: {" ".join(command)}')

        subprocess.run(
            command,
            check=True,
        )
