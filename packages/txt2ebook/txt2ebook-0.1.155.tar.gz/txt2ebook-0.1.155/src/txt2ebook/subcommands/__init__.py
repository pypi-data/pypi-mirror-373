# Copyright (c) 2021,2022,2023,2024,2025 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Common utils for subcommand."""

import importlib
import pkgutil


def build_subparser(subparsers):
    """Build subparser for each subcommands."""
    iter_namespace = pkgutil.iter_modules(__path__, __name__ + ".")

    subcommands = {
        name: importlib.import_module(name)
        for finder, name, ispkg in iter_namespace
    }

    for subcommand in subcommands.values():
        subcommand.build_subparser(subparsers)
