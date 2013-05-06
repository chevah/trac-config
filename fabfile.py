from fabric.api import run, settings

from braid import pip, postgres, cron, git
from braid.twisted import service

from braid import config
_hush_pyflakes = [config]


class Trac(service.Service):
    def task_install(self):
        """
        Install trac.
        """
        self.bootstrap(python='system')

        # FIXME: Make these idempotent.
        postgres.createUser('trac')
        postgres.createDb('trac', 'trac')

        with settings(user=self.serviceUser):
            pip.install('psycopg2', python='system')
            self.task_update(_installDeps=True)

            run('mkdir -p ~/svn')
            run('ln -nsf ~/svn {}/trac-env/svn-repo'.format(self.configDir))

            run('mkdir -p ~/attachments')
            run('ln -nsf ~/svn {}/trac-env/attachments'.format(self.configDir))

            run('ln -nsf {} {}/trac-env/log'.format(self.logDir, self.configDir))

            run('ln -nsf {}/start {}/start'.format(self.configDir, self.binDir))

            # Overwrite the generic stop executable provided by the base class
            run('ln -nsf {}/stop {}/stop'.format(self.configDir, self.binDir))
            run('ln -nsf {}/restart {}/restart'.format(self.configDir,
                                                       self.binDir))
            run('ln -nsf {}/monitor {}/monitor'.format(self.configDir,
                                                       self.binDir))
            run('ln -nsf {}/start-monitor {}/start-monitor'.format(
                self.configDir, self.binDir))
            cron.install(self.serviceUser, '{}/crontab'.format(self.configDir))


    def task_update(self, _installDeps=False):
        """
        Update trac config.
        """
        # TODO
        with settings(user=self.serviceUser):
            git.branch('https://github.com/twisted-infra/trac-config', self.configDir)

            if _installDeps:
                pip.install('git+https://github.com/twisted-infra/twisted-trac-source.git', python='system')
            else:
                pip.install('--no-deps --upgrade git+https://github.com/twisted-infra/twisted-trac-source.git', python='system')

globals().update(Trac('trac').getTasks())
