# RainDuck

A simple BrainFuck extension with macros transpiled to BrainFuck.

## Installation

Use `pip` to install RainDuck.
```bash
pip install rainduck
```

## Usage

```bash
# transpiles code to BrainFuck
rainduck my-program.rd

# use your favourite BrainFuck compiler or interpreter
brainfuck my-program.bf
```

### Basic Syntax

```rainduck
// comments are created with '//'
let // if you want to define macros, you must start with the word 'let'
#import(folder/file.rd) // imports all global macros in folder/file.rd
clear = {[-]} // macro without arguments
five_left = {5<} // integer repeats given string
ten_right = {-2five_left} // negative integer reverses string and turns > <-> < and + <-> -
error = {-3[+]} // loop cannot be inverted, this raises an error...
no_error = {-1 error} // ...but double iversion doesn't have effect, this raises no error
move_cell(
    from;
    to = < // default value for this argument
) = {from [- -1from to + -1to from] -1from}

// most whitespace characters are optional
copy_cell(from={};to={};storage=<)={from[--1from storage+-1storage to+-1to from]move(storage)-1from}
in // end of macro definitions
// follows executed code
move( // macro call
    { // code blocks are created with curly brackets...
        let five_left={5{<<>}} in // ...and can contain local macro definition...
        3 {five_left >} // ...but don't have to
    };
    >
)
```

## Contributing

Pull requests are welcome.

## License

[MIT](https://choosealicense.com/licenses/mit/)
