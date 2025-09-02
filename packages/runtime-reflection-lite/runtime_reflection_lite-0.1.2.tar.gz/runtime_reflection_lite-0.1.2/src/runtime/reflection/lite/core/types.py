from types import (
    CodeType, ModuleType, FrameType, # pyright: ignore[reportUnusedImport]
    FunctionType, MethodType, LambdaType, BuiltinFunctionType, BuiltinMethodType,
    WrapperDescriptorType, MethodWrapperType, MethodDescriptorType, ClassMethodDescriptorType
)


FUNCTION_TYPES = (
    FunctionType, LambdaType,
    BuiltinFunctionType, WrapperDescriptorType
)
METHOD_TYPES = (
    MethodType, BuiltinMethodType, MethodWrapperType,
    MethodDescriptorType, ClassMethodDescriptorType
)
FUNCTION_AND_METHOD_TYPES = FunctionType | LambdaType | BuiltinFunctionType | WrapperDescriptorType | MethodType | BuiltinMethodType | MethodWrapperType | MethodDescriptorType | ClassMethodDescriptorType
