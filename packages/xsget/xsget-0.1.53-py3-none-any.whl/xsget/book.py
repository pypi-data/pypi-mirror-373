# Copyright (C) 2021,2022,2023,2024,2025 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Data model for an extracted Book."""

from dataclasses import dataclass, field

from xsget.chapter import Chapter


@dataclass
class Book:
    """Represents a book composed of multiple chapters.

    Attributes:
        title: The title of the book.
        authors: A list of authors for the book.
        chapters: A list of Chapter objects representing the book's content.
    """

    title: str = field(default="")
    authors: list[str] = field(default_factory=list)
    chapters: list[Chapter] = field(default_factory=list, repr=False)
