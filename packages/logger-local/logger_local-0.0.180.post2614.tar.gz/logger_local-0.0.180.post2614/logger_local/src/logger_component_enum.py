from enum import Enum


class LoggerComponentEnum:
    class ComponentType(Enum):
        Service = "Service"
        API = "API"
        Remote = "Remote"

    class ApiType(Enum):
        REST_API = "REST-API"
        GraphQL = "GraphQL"

    class ComponentCategory(Enum):
        Code = "Code"
        Unit_Test = "Unit-Test"
        E2E_Test = "E2E-Test"

    # TODO Should we change to TestingFramework? Or it doesn't worth the effort?
    #   do we use it a lot?
    class testingFramework(Enum):
        Vitetest = "Vitetest"
        Playwrite = "Playwrite"
        Python_Unittest = "Python Unittest"
        pytest = "pytest"
