from blocks_cli.commands.__base__ import blocks_cli
from blocks_cli.commands.configure import configure
from blocks_cli.commands.push import push
from blocks_cli.commands.init import init
from blocks_cli.commands.test import test
from blocks_cli.commands.create import create

if __name__ == "__main__":
    blocks_cli()