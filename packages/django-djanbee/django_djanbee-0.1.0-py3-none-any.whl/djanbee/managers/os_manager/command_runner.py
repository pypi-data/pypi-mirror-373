from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union
import shlex
import subprocess

@dataclass
class CommandResult:
   """Result of a command execution with convenience methods for checking success."""
   success: bool
   stdout: str
   stderr: str
   exit_code: int

   def __bool__(self):
       """Allow using CommandResult in boolean contexts (if result: ...)"""
       return self.success

   def __iter__(self):
       """Unpack as (success, message) where message is stdout on success, stderr on failure."""
       msg = self.stdout if self.success else self.stderr
       yield self.success
       yield msg


class CommandRunner:
   def run(
       self,
       args: Union[str, List[str]],
       cwd: Optional[Path] = None,
       sudo: bool = False
   ) -> CommandResult:
       
       # Convert string commands to list format for subprocess
       if isinstance(args, str):
           cmd = shlex.split(args)
       else:
           cmd = args[:]
       
       # Prepend sudo if requested
       if sudo:
           cmd = ["sudo"] + cmd

       # Execute command and capture output
       proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
       return CommandResult(
           success=(proc.returncode == 0),
           stdout=proc.stdout.strip(),
           stderr=proc.stderr.strip(),
           exit_code=proc.returncode,
       )