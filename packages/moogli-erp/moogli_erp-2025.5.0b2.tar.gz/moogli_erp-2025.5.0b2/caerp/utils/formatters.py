def format_civilite(civilite_str):
    """
    Shorten the civilite string

    :param str civilite_str: Monsieur/Madame
    :returns: Mr/Mme
    :rtype: str
    """
    res = civilite_str
    if civilite_str.lower() == "monsieur":
        res = "M."
    elif civilite_str.lower() == "madame":
        res = "Mme"
    elif civilite_str.lower() == "mr&mme":
        res = "M. et Mme"
    return res
