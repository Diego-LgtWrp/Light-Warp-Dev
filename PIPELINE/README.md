# Folder **PIPELINE/**

* This folder is associated with all pipeline-related tools, scripts, program-specific plugins, and links to projects requiring individual spaces.

## Files

### The *PIPELINE/SecureTransfer*

* An application to securely transfer files.
* Current notes on use:
*   *  UI looks super cool and works super well to test the underlying code
    *  Having a thorough logging infrastructure of all the functions and processes would be nice for dev
    *  Maybe instead of "Move, Copy, Check" It defaults to move, and you toggle whether you copy and/or check the files?
    Or have check as a separate button since you might want to do multiple actions with a single set of selections, not sure.
    I might make it so that one button moves the file, and they toggle an option to copy. A second button checks and validates separately.
    *  Paper trail text file is great, but if you move a .txt file, it doesn't generate, so maybe generate as "[filename]_log.txt"
    *  Allowing a user to add comments might be nice as well?
    *  
