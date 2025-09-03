COMMON_COOKIES = [
    {
        "name": "PHPSESSID",
        "description": "PHP session cookie",
        "category": "SESSION",
        "severity": "ERROR",
        "rules": {"value_format": r"^[a-z0-9]{26}$"},
    },
    {
        "name": "JSESSIONID",
        "description": "Java session cookie",
        "category": "SESSION",
        "severity": "ERROR",
        "rules": {"value_format": r"^[a-z0-9]{32}$"},
    },
    {
        "name": "Lang",
        "description": "Standard cookie for saving the set language",
        "category": "STANDARD",
        "severity": "INFO",
    },
    {
        "name": "password",
        "description": "Typical name for a cookie containing a password",
        "category": "SENSITIVE",
        "severity": "ERROR",
    },
    {
        "name": "ASP.NET",
        "description": "ASP.NET session cookie",
        "category": "SESSION",
        "severity": "ERROR",
        "rules": {"value_format": r"^[a-z0-9]{24}$"},
    },
    {
        "name": r"^ASPSESSIONID[A-Z0-9]{8}$",
        "description": "ASP session (IIS >= 6.0)",
        "category": "SESSION",
        "severity": "ERROR",
    },
    {
        "name": r"^ASPSESSIONID[A-Z]{4,6}$",
        "description": "ASP session (IIS <= 5.0)",
        "category": "SESSION",
        "severity": "ERROR",
    },
    {
        "name": "ASP",
        "description": "ASP session cookie",
        "category": "SESSION",
        "severity": "ERROR",
        "rules": {"value_format": r"^[A-Z]{24}$"},
    },
]
