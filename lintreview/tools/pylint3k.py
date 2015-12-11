import os
import logging
from lintreview.tools import Tool
from lintreview.tools import run_command
from lintreview.utils import in_path

log = logging.getLogger(__name__)


class PyLint3k(Tool):
    """ Runs PyLint in --p3k mode, the python3 compatability checker """

    name = 'pylint3k'

    # see: http://docs.pylint.org/
    PYLINT3K_OPTIONS = [
        'disable',
        'output-format',
        'msg-template',
        'reports',
    ]

    def default_options(self):
        options = super(PyLint3k, self).default_options()
        options.update({
            'msg-template':'{path}:{line}:{column}: {msg_id} {msg}'
            'reports':'no'
            'output-format':'text'
        })
        return options

    def check_dependencies(self):
        """
        See if pylint is on the PATH
        """
        return in_path('pylint')

    def match_file(self, filename):
        base = os.path.basename(filename)
        name, ext = os.path.splitext(base)
        return ext == '.py'

    def process_files(self, files):
        """
        Run code checks with pylint --p3k.
        Only a single process is made for all files
        to save resources.
        """
        log.debug('Processing %s files with %s', files, self.name)
        command = ['pylint', '--py3k']
        for option in self.PYLINT3K_OPTIONS:
            if self.options.get(option):
                command.extend(
                    ['--%(option)s' % {'option': option},
                     self.options.get(option)])

        command += files
        output = run_command(command, split=True, ignore_error=True)
        if not output:
            log.debug('No pylint3k errors found.')
            return False

        for line in output:
            if line.startswith("******"):
                continue
            filename, line, error = self._parse_line(line)
            self.problems.add(filename, line, error)

    def _parse_line(self, line):
        """
        pylint only generates results as stdout.
        Parse the output for real data.
        """
        parts = line.split(':', 3)
        if len(parts) == 3:
            message = parts[2].strip()
        else:
            message = parts[3].strip()
        return (parts[0], int(parts[1]), message)
