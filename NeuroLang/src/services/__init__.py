"""Warstwa serwisowa kompilatora (wspólna dla CLI i API webowego)."""

from src.services.compiler_service import CompileResult, compile_source, parse_ast

__all__ = ["CompileResult", "compile_source", "parse_ast"]
