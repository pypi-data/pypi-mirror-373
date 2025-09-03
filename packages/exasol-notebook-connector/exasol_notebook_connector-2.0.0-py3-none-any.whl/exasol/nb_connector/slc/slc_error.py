class SlcError(Exception):
    """
    Signals errors related to ScriptLanguageContainer:

    * The name of the SLC is not unique

    * the Secure Configuration Storage (SCS / secrets / conf) does not contain
      a required option

    * The SLC Git repository has not been checked out (cloned)
    """
