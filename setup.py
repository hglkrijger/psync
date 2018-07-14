import os
import shutil
import stat
import subprocess

from setuptools import setup
from setuptools.command.install import install


class ServiceInstall(install):
    @staticmethod
    def exec_cmd(cmd):
        try:
            subprocess.check_output(cmd.split(' '))
            print(cmd)
        except subprocess.CalledProcessError as e:
            print('could not execute {0}: {1} {2}'.format(cmd, e.returncode, e.output))

    def run(self):
        install.run(self)

        print('creating service')
        service_file = 'psync.service'
        current_path = os.path.dirname(os.path.realpath(__file__))
        psync_service = os.path.join(current_path, 'service', service_file)
        if not os.path.exists(psync_service):
            print('{0} not found'.format(psync_service))
            return

        run_systemctl = True
        dest_path = '/lib/systemd/system'
        if not os.path.exists(dest_path):
            print('{0} not found, will not copy service file'.format(dest_path))
            run_systemctl = False
        else:
            dst = os.path.join(dest_path, service_file)
            print('copy {0} to {1}'.format(psync_service, dst))
            shutil.copy(psync_service, dst)
            os.chmod(dst, 0o664)

        print('creating runner')
        exec_file = 'psync'
        psync_exec = os.path.join(current_path, 'service', exec_file)
        if not os.path.exists(psync_exec):
            print('{0} not found'.format(psync_exec))
            return

        dest_path = '/usr/sbin'
        if not os.path.exists(dest_path):
            print('{0} not found, will not copy exec file'.format(dest_path))
            run_systemctl = False
        else:
            dst = os.path.join(dest_path, exec_file)
            print('copy {0} to {1}'.format(psync_exec, dst))
            shutil.copy(psync_exec, dst)
            os.chmod(dst, 0o755)
            os.chmod(dst, stat.S_IEXEC)

        if run_systemctl:
            self.exec_cmd('systemctl daemon-reload')
            self.exec_cmd('systemctl enable psync.service')
            self.exec_cmd('systemctl start psync.service')


setup(name='psync',
      version='0.1.0',
      packages=['psync'],
      entry_points={'console_scripts': ['psync = psync.__main__:main']},
      cmdclass={'install': ServiceInstall})
