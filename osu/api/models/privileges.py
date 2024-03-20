from enum import IntFlag, unique


@unique
class RippleScopes(IntFlag):
    PrivilegeReadDEPRECATED = 1 << 0               # deprecated, methods with PrivilegeRead used to be the ones that now are "auth-free"
    PrivilegeReadConfidential = 1 << 1             # (eventual) private messages, reports... of self
    PrivilegeWrite = 1 << 2                        # change user information, write into confidential stuff...
    PrivilegeManageBadges = 1 << 3                 # can change various users' badges.
    PrivilegeBetaKeys = 1 << 4                     # can add, remove, upgrade/downgrade, make public beta keys.
    PrivilegeManageSettings = 1 << 5               # maintainance, set registrations, global alerts, bancho settings
    PrivilegeViewUserAdvanced = 1 << 6             # can see user email, and perhaps warnings in the future, basically.
    PrivilegeManageUser = 1 << 7                   # can change user email, allowed status, userpage, rank, username...
    PrivilegeManageRoles = 1 << 8                  # translates as admin, as they can basically assign roles to anyone, even themselves
    PrivilegeManageAPIKeys = 1 << 9                # admin permission to manage user permission, not only self permissions. Only ever do this if you completely trust the application, because this essentially means to put the entire ripple database in the hands of a (potentially evil?) application.
    PrivilegeBlog = 1 << 10                        # can do pretty much anything to the blog, and the documentation.
    PrivilegeAPIMeta = 1 << 11                     # can do /meta API calls. basically means they can restart the API server.
    PrivilegeBeatmap = 1 << 12                     # rank/unrank beatmaps. also BAT when implemented
    PrivilegeBancho = 1 << 13                      # can log in to bancho and use the chat through the delta ws api