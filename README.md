# CircuitS

[![Generic badge](https://img.shields.io/badge/docs-stable-blue.svg)](https://stevomitric.github.io/CircuitS/)
[![Generic badge](https://img.shields.io/badge/playlist-stable-green.svg)](https://www.youtube.com/watch?v=_FDBpXHv5K4&list=PLsdlVaS2tAjwrjH75B9gKyHN_5_nphFlJ&ab_channel=FilipDrobnjakovi%C4%87)

## About
CircuitS is a library written in Julia programming language for solving linear, time-invariant electric circuits. Using [JuliaSymbolics](https://github.com/JuliaSymbolics/Symbolics.jl) library as a computer algebra system and for solving linear equations, CircuitS successfully simulates and solves simple electric circuits.

## Why CircuitS?

 - Written in a high-level, high-performance, dynamic programming language
 - Completely free, open-source code licensed under GPLv3 
 - GUI Extension that offers user friendly way to create and modify circuits
 - Completely modular code. Ability to include it in other projects easily


## Algorithm

CircuitS uses [modified nodal analysis](https://www.swarthmore.edu/NatSci/echeeve1/Ref/mna/MNA2.html) to solve electric circuits. MNA is an extension of nodal analysis which not only determines the circuit's node voltages (as in classical nodal analysis), but also some branch currents. Modified nodal analysis was developed as a formalism to mitigate the difficulty of representing voltage-defined components in nodal analysis (e.g., voltage-controlled voltage sources).

## Getting started

CircuitS features a detailed documentation and has a rich example base that can be found [here](https://stevomitric.github.io/CircuitS/).

There are also video demonstrations (voiced in Serbian language, with english captions):
- [Introduction and installation](https://www.youtube.com/watch?v=_FDBpXHv5K4&ab_channel=FilipDrobnjakovi%C4%87)
- [Current divider](https://www.youtube.com/watch?v=eYmp1-jlMks&t=201s&ab_channel=FilipDrobnjakovi%C4%87)

## Authors

- Stevo Mitrić
- Filip Drobnjaković

University of Belgrade, School of Electrical Engineering

#### Acknowledgment

We thank Prof. dr Dejan V. Tošić and Prof. dr Milka M. Potrebić for recommending this software project to us and for all discussions and help with the project.
