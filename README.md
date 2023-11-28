# ghpm
Github based Package Manager

## ideas at the start of teh project, 2023-11-28
The idea behind this project is to create a python script that can work a bit like debian apt
but for applications that are not in debian repositories, but in Gitub repositories.

While there are some open source projects available that work for e.g. go or python programs,
this project is aimed at a more general approach: when a project offers release packages like
deb or rpm files, our ghpm should be able to use this to perform the install, update and
remove functionality.

One problem to solve is that we have no established standard on how to determine the version
of a program in github and local. For local programs, we will assume that the program will
respond to the 
<program> --version
convention.
This however changes the task to find out the program name (for the beginning we will use the repository name as first guess).

The idea of this project is to take code from https://github.com/froeb/manage-thorium and to make it more general.

