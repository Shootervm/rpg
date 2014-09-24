from subprocess import check_output


class Command:

    """representation of scripts in spec file"""

    def __init__(self, cmdline=None):
        """cmdline could be list of strings or string containing multiple lines
           """

        self.rpm_variables = []
        self._command_lines = []
        if cmdline:
            self.append_cmdlines(cmdline)

    def __str__(self):
        """join command lines together. Returns one string that will be saved
           in spec file"""

        return "\n".join(self._command_lines)

    def __repr__(self):
        return "Command(%s)" % repr(str(self))

    def append_cmdlines(self, cmdline):
        """adds cmdline at the end of command sequence
           cmdline could be list of strings or string containing multiple lines
           """

        if isinstance(cmdline, list):
            self._command_lines.extend(cmdline)
        elif isinstance(cmdline, str):
            self._command_lines.extend(cmdline.split("\n"))
        else:
            msg = "Only list of command strings or command string is accepted"
            raise TypeError(msg)

    def execute_from(self, work_dir):
        """executes command in work_dir (instance of pathlib.Path),
           can raise CalledProcessError"""

        cd_workdir = ["cd %s" % work_dir.resolve()]
        command_lines = self._assign_rpm_variables() + cd_workdir + \
            self._command_lines
        o = check_output(["/bin/sh", "-c", " && ".join(command_lines)])
        # TODO don't print stdout of commands
        return o.decode('utf-8')

    def _assign_rpm_variables(self):
        return ['%s="%s"' % (v, p) for (v, p) in self.rpm_variables]
