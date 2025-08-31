# Copyright (C) 2025 Kian-Meng, Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from videolab.cli import main


class TestCLI:
    """
    Tests for the command-line interface.
    """
    def test_no_command_shows_help(self, capsys):
        """
        Tests that running with no command shows the help message.
        """
        main([])
        captured = capsys.readouterr()
        output = captured.out
        assert "usage: videolab" in output
        assert "A console program to manipulate videos." in output
