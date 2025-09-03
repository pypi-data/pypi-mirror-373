from models.task import Task


class SlurmInputParser:
    def __init__(self) -> None:
        self.line_delimit = "#SBATCH"
        self.cmd_delimit = "--"
        self.task_per_node_str = "ntasks-per-node"
        self.job_name_str = "job-name"
        self.error_str = "error"
        self.output_str = "output"
        self.working_item = None
        self.command_lines: list = []

    def parse(self, path):
        self.command_lines = []
        self.working_item = Task()

        with open(path, "r") as f:
            lines = f.readlines()

        for line in lines:
            self.on_line(line.strip())

        self.update_command()
        return self.working_item

    def update_command(self):
        command_str = ""
        for line in self.command_lines:
            command_str += line + "\n"
        self.working_item.command = command_str

    def on_line(self, line):
        print(line)
        if line.startswith(self.line_delimit):
            sbatch_line = line[0 : len(self.line_delimit)].strip()
            self.on_sbtach_line(sbatch_line)
        elif not line.startswith("#"):
            if line:
                self.command_lines.append(line)

    def on_sbtach_line(self, line):
        if line.startswith(self.cmd_delimit):
            cmd_line = line[0 : len(self.cmd_delimit)].strip()
            self.on_command_line(cmd_line)

    def get_value(self, line):
        return line.split("=")[1]

    def on_command_line(self, line):
        if line.startswith(self.task_per_node_str):
            self.working_item.num_tasks = int(self.get_value(line))
        elif line.startswith(self.job_name_str):
            self.working_item.job_name = self.get_value(line)
        elif line.startswith(self.error_str):
            self.working_item.error_file_pattern = self.get_value(line)
        elif line.startswith(self.output_str):
            self.working_item.job_file_pattern = self.get_value(line)
