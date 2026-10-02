# Cool Static Website Generator

I started working on this because I have a static website, and I had some issues with the way I built it. I learned about static site generators and found most of the popular options were a bit more robust than I needed, so I figured if I'm going to learn something anyways I might as well make it up.

## How to use

Probably don't right now, but

### Generate

Running the python file `make_page.py` reads everything in the source directories and spits out the complete deployable website into the `output` directory

Project is still quite WIP so expect this to change and for this readme to be behind. Eventual intent is for source and output to exist outside the python files' directory (specified by user)

### Templates

Templates are html files that exist in the source `template` directory. They define the layout of components. Components must specify a template to be used.

Templates specify where component variables are used in the page. Any string within enclosed `%` characters are treated as a variable (haven't added escape character yet).

- For example, `%title%` can be written within an HTML head like `<title>%title%</title>`
- If a variable starts with `component`, like `component/header`, then that component will replace that text (with default variable values if any, maybe I'll add variables to templates but this is already complex enough for me no?)

`%content%` is a special variable that is populated a little differently, see Components

### Components

Components are `.yaml` files in the source `component` directory. They define the content of the generated parts of the website.

Variables are defined in the component YAML file as root key-pair values.

- The `template` key is required, and points to an HTML file in the `template` directory
- All other keys are treated as variables, and are parsed into templates according to a few rules.
  1. String values will simply parse as its string value
  2. Objects with a `type` key will be treated differently depending on the type.
    - I gotta document the types still and it's definitely something that will arbitrarily grow
    - The `component` type within content must have `component` defined (target component to add), and can have `variables` defined (overrides the default variables of that component)
  3. Arrays will fill in instances of strings and objects just like `1.` and `2.`, except strings will be treated as paragraph blocks. This is useful for filling normal page content


There's definitely a way to consolidate some of this down consistently, I think I want the ability to have multiple "content" sections in a template instead of having a reserved keyword. 

### Includes

Anything can be put in the source `include` directory, and it will be copied 1:1 to the output directory. This is where css, scripts, and non-generated html can be kept.
