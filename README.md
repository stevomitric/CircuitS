# Introduction

## About
CircuitS is a library written in Julia programming language for solving linear, time-invariant electric circuits. Using [JuliaSymbolics](https://github.com/JuliaSymbolics/Symbolics.jl) library as a computer algebra system and for solving linear equations, CircuitS successfully simulates and solves simple electric circuits.

## Why CircuitS?

 - Written in a high-level, high-performance, dynamic programming language
 - Completely free, open-source code licensed under GPLv3 
 - GUI Extension that offers user friendly way to create and modify circuits
 - Completely modular code. Ability to include it in other projects easily


## Algorithm

CircuitS uses [modified nodal analysis](https://www.swarthmore.edu/NatSci/echeeve1/Ref/mna/MNA2.html) to solve electric circuits. MNA is an extension of nodal analysis which not only determines the circuit's node voltages (as in classical nodal analysis), but also some branch currents. Modified nodal analysis was developed as a formalism to mitigate the difficulty of representing voltage-defined components in nodal analysis (e.g., voltage-controlled voltage sources).

## Limits

Julia, as a relatively new language, offers modern solutions to classic programming problems, but it does come at a cost. Lack of testing and support for it's symbolic library is reflected in this project and will be discuessed further in detail.

## Authors

- Stevo Mitrić
- Filip Drobnjaković

University of Belgrade, School of Electrical Engineering

##### Acknowledgment

We thank Prof. dr Dejan V. Tošić and Prof. dr Milka M. Potrebić for recommending this software project to us and for all discussions and help with the project.