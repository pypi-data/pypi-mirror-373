# MDL Core Features Guide

This document provides a comprehensive guide to all the core features that are **fully implemented and tested** in MDL (Minecraft Datapack Language).

## ✅ **FULLY IMPLEMENTED & TESTED**

### 1. Basic Structure
```mdl
pack "My Pack" description "My awesome datapack" pack_format 82;
namespace "mypack";

function "main" {
    // Your code here
}
```

### 2. Variables
MDL supports number variables stored in scoreboard objectives:

#### Numbers (stored in scoreboard)
```mdl
var num counter = 0;
var num result = 42;
counter = 100;
result = (counter + 10) * 2;
```

**Important**: Functions called via tags (like `on_tick`) run as the server and use `@a` selector for player targeting. Functions called directly by players use `@s` selector.

### 3. Variable Substitution
MDL supports variable substitution in commands and conditions:

#### In Commands
```mdl
say "Current score: $score$";
tellraw @a [{"text":"Score: "},{"score":{"name":"@a","objective":"score"}}];
```

#### In Conditions
```mdl
if "$counter$ > 10" {
    say "Counter is high!";
}
```

### 4. Control Flow

#### If/Else Statements
```mdl
if "$counter$ > 40" {
    say "Counter is greater than 40";
    counter = counter - 10;
} else {
    say "Counter is 40 or less";
    counter = counter + 10;
}
```

#### While Loops with Method Selection
While loops implement proper recursive logic to continue execution until the condition becomes false.

```mdl
// Default recursion method (good for small loops)
while "$counter$ > 0" {
    say "Counter: $counter$";
    counter = $counter$ - 1;
}

// Explicit recursion method
while "$counter$ < 100" method="recursion" {
    say "Recursion loop: $counter$";
    counter = $counter$ + 1;
}

// Schedule method (better for long loops - spreads across ticks)
while "$counter$ < 1000" method="schedule" {
    say "Schedule loop: $counter$";
    counter = $counter$ + 1;
}
```

**How it works:**
- **Recursion method**: Each loop function calls itself recursively when the condition is still true, executing all iterations immediately
- **Schedule method**: Each loop function schedules itself to run 1 tick later when the condition is still true, spreading iterations across multiple game ticks for better performance

**Generated code example (recursion):**
```mcfunction
# Main function
execute if score @s counter matches 1.. run function namespace:loop_function

# Loop function (recursively calls itself)
tellraw @a [{"text":"Counter: "},{"score":{"name":"@s","objective":"counter"}}]
scoreboard players remove @s counter 1
execute if score @s counter matches 1.. run function namespace:loop_function
```

### 5. Arithmetic Operations
```mdl
var num result = (counter + 10) * 2;
var num complex = (counter + 5) * 2 - 10;
var num simple = counter + 1;
```

### 6. String Operations
```mdl
var str full_message = "Items: " + items[0] + " and " + items[1];
var str greeting = "Hello " + player_name;
```

### 7. Basic Commands
```mdl
say "Hello, Minecraft!";
tellraw @a {"text":"Welcome!","color":"green"};
```

### 8. Functions
```mdl
function "main" {
    say "Main function called!";
}

function "helper" {
    say "Helper function called!";
    var num helper_var = 100;
    say "Helper value: " + helper_var;
}
```

### 9. Hooks
```mdl
on_load "mypack:main";
on_tick "mypack:helper";
```

### 10. Tags
```mdl
tag function minecraft:load {
    add "mypack:main";
}

tag function minecraft:tick {
    add "mypack:helper";
}
```

## 🧪 **Testing**

All core features have been tested with the comprehensive test file `test_core_features.mdl` which includes:

- ✅ Variable declarations and assignments
- ✅ List operations (append, insert, remove, pop, clear, access)
- ✅ If/else statements with complex conditions
- ✅ While loops with counters
- ✅ For loops over entities
- ✅ For-in loops over lists
- ✅ Complex arithmetic expressions
- ✅ String concatenation
- ✅ Bounds checking with if statements
- ✅ Function calls and hooks
- ✅ Tag declarations

## 📁 **Generated Output**

The compiler generates proper Minecraft datapack structure:

```
output/
├── pack.mcmeta
├── data/
│   ├── minecraft/
│   │   └── tags/
│   │       └── function/
│   │           ├── load.json
│   │           └── tick.json
│   └── [namespace]/
│       └── function/
│           ├── main.mcfunction
│           ├── helper.mcfunction
│           └── _global_vars.mcfunction
```

## 🔧 **How It Works**

### Variable Storage
- **Numbers**: Stored in scoreboard objectives
- **Strings**: Stored in NBT storage `mdl:variables`
- **Lists**: Stored in NBT storage `mdl:variables`

### Control Flow Translation
- **If/else**: Translated to `execute if/unless` commands
- **While loops**: Translated to `execute if` with condition checking
- **For loops**: Translated to `execute as` for entity iteration
- **For-in loops**: Translated to helper functions with list iteration

### Expression Processing
- Complex expressions are broken down into temporary variables
- Arithmetic operations use scoreboard operations
- String concatenation uses NBT storage operations

## 🎯 **Ready for Production**

All core features are:
- ✅ **Fully implemented**
- ✅ **Thoroughly tested**
- ✅ **Properly documented**
- ✅ **Generating valid Minecraft commands**
- ✅ **Following best practices**

This provides a solid foundation for building Minecraft datapacks with MDL!
