# %% prerequisites

from main import initialized_lark_from_file

lark = initialized_lark_from_file('./grammar.lark')

# %% start: import_statement* ((statement | declaration) (_NL statement | declaration)*)?
# import_statement: import_name | import_from
#
# import_name: IMPORT as_name ("," as_name)*
#
# import_from: FROM (".")* NAME IMPORT import_targets
#     | FROM (".")+ IMPORT import_targets

