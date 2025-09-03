#!/bin/bash

# get all possible args in var
FILES=("$@")  # all args in an array

# check if any
if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <filename(s)>"
  exit 1
fi

# loop over files in args
for filename in "${FILES[@]}";do
    # adapt header with original filename
    header="! SPDX-License-Identifier: GPL-3.0-or-later
! Copyright 2025, BRGM
! 
! This file is part of gridmarthe.
! 
! Gridmarthe is free software: you can redistribute it and/or modify it under the
! terms of the GNU General Public License as published by the Free Software
! Foundation, either version 3 of the License, or (at your option) any later
! version.
! 
! Gridmarthe is distributed in the hope that it will be useful, but WITHOUT ANY
! WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
! PARTICULAR PURPOSE. See the GNU General Public License for more details.
! 
! You should have received a copy of the GNU General Public License along with
! Gridmarthe. If not, see <https://www.gnu.org/licenses/>.
!
!
! (from MARTHE, file : ${filename}, convert utf-8 )
!
! MARTHE, Copyright (c) 1990-2025 BRGM
!
"
    # echo $filename
    # echo $header
    echo -e "$header$(cat $filename)" > "$filename.tmp" && mv "$filename.tmp" "$filename"
done

exit 0
