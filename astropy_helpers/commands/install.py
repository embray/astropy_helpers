from distutils.errors import DistutilsArgError
from setuptools.command.install import install as SetuptoolsInstall

from ..utils import _get_platlib_dir


class PipInstall(SetuptoolsInstall):
    command_name = 'install'
    user_options = SetuptoolsInstall.user_options + [
        ('pip', None, 'install using pip; ignored when also using '
                      '--single-version-externally-managed')
    ]
    boolean_options = SetuptoolsInstall.boolean_options + ['pip']

    def initialize_options(self):
        SetuptoolsInstall.initialize_options(self)
        self.pip = False

    def finalize_options(self):
        SetuptoolsInstall.finalize_options(self)

        if self.single_version_externally_managed:
            self.pip = False

        if self.pip:
            try:
                import pip
            except ImportError:
                raise DistutilsArgError(
                    'pip must be installed in order to install with the '
                    '--pip option')

    def run(self):
        if self.pip:
            import pip
            opts = ['install', '--ignore-installed'] + ['--install-option="{0}"'.format(opt)
                                  for opt in self._get_command_line_opts()]
            pip.main(opts + ['.'])
        else:
            SetuptoolsInstall.run(self)

    def _get_command_line_opts(self):
        # Generate a mapping from the attribute name associated with a
        # command-line option to the name of the command-line option (including
        # an = if the option takes an argument)
        attr_to_opt = dict((opt[0].rstrip('=').replace('-', '_'), opt[0])
                           for opt in self.user_options)

        opt_dict = self.distribution.get_option_dict(self.get_command_name())
        opts = []

        for attr, value in opt_dict.items():
            if value[0] != 'command line' or attr == 'pip':
                # Only look at options passed in on the command line (ignoring
                # the pip option itself)
                continue

            opt = attr_to_opt[attr]

            if opt in self.boolean_options:
                opts.append('--' + opt)
            else:
                opts.append('--{0}{1}'.format(opt, value[1]))

        return opts

    @staticmethod
    def _called_from_setup(run_frame):
        return SetuptoolsInstall._called_from_setup(run_frame.f_back)


class AstropyInstall(PipInstall):
    user_options = PipInstall.user_options[:]
    boolean_options = PipInstall.boolean_options[:]

    def finalize_options(self):
        build_cmd = self.get_finalized_command('build')
        platlib_dir = _get_platlib_dir(build_cmd)
        self.build_lib = platlib_dir
        PipInstall.finalize_options(self)
