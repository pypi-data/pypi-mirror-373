#  Copyright 2022-present, the Waterdip Labs Pvt. Ltd.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from rich.terminal_theme import TerminalTheme

theme_1 = TerminalTheme(
    background=(20, 20, 20),  # RGB triplet for grey
    foreground=(255, 255, 255),  # RGB triplet for white
    normal=[
        (0, 0, 0),  # black
        (255, 0, 0),  # red
        (0, 255, 0),  # green
        (255, 255, 0),  # yellow
        (0, 0, 255),  # blue
        (255, 0, 255),  # magenta
        (0, 255, 255),  # cyan
        (255, 255, 255),  # white
    ],
    bright=[
        (64, 64, 64),  # medium grey
        (128, 64, 64),  # medium red
        (64, 128, 64),  # medium green
        (128, 128, 64),  # medium yellow
        (64, 64, 128),  # medium blue
        (128, 64, 128),  # medium magenta
        (64, 128, 128),  # medium cyan
        (128, 128, 128),  # medium white (grey)
    ],
)
