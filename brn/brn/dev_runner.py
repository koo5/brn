"""

https://click.palletsprojects.com/en/7.x/options/#values-from-environment-variables

"""





"""
Sometimes, you want to process arguments that look like options. For instance, imagine you have a file named -foo.txt. If you pass this as an argument in this manner, Click will treat it as an option.

To solve this, Click does what any POSIX style command line script does, and that is to accept the string -- as a separator for options and arguments. After the -- marker, all further parameters are accepted as arguments.

- https://click.palletsprojects.com/en/7.x/arguments/#option-like-arguments
"""
